"""
BizUni Crawler for fetching stock data from bizuni.vn
Supports both manual login and automated crawling with session management
Automatically detects and uses existing sessions or prompts for login
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import platform
import getpass
from datetime import datetime
import os
from pathlib import Path
import random
import sys

class BizUniCrawler:
    def __init__(self):
        self.base_url = "https://bizuni.vn"
        self.data_url = f"{self.base_url}/co-phieu-gia-tri"
        self.playwright = None
        self.browser = None
        self.page = None
        self.context = None
        self.credentials = None
        self.current_user = None
        self.session_file = None
        self._cleaned = False  # prevent double cleanup prints / operations
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._cleanup()
    
    def _get_session_file(self):
        """Get session file path based on current user"""
        if not self.current_user:
            self.current_user = getpass.getuser()
        
        session_dir = Path(__file__).parent / ".sessions"
        session_dir.mkdir(exist_ok=True)
        
        self.session_file = session_dir / f"auth_state_{self.current_user}.json"
        return self.session_file
    
    def _session_exists(self) -> bool:
        """Check if session file exists for current user"""
        self._get_session_file()
        return self.session_file.exists()
    
    async def _human_delay(self, min_s=2.5, max_s=5.0):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_s, max_s)
        await asyncio.sleep(delay)
    
    def _validate_environment(self):
        """Validate OS and user environment"""
        if platform.system() != "Darwin":
            raise OSError("❌ Incorrect running environment: OS must be macOS")
        
        self.current_user = getpass.getuser()
        
        if "thao" in self.current_user.lower():
            self.credentials = {
                'username': 'nb2t71@gmail.com',
                'password': '070186'
            }
        elif "anh" in self.current_user.lower():
            self.credentials = {
                'username': 'anh.chau515@gmail.com',
                'password': '[need to fulfill]'
            }
        else:
            raise ValueError(f"❌ Incorrect running environment: Unknown user '{self.current_user}'")
        
        self._get_session_file()
        print(f"✅ Environment validated for user: {self.current_user}")
    
    async def login_and_save_session(self):
        """Manual login process with session state saving"""
        temp_browser = None
        temp_context = None
        temp_page = None
        
        try:
            self._validate_environment()
            
            # Check if session already exists
            if self.session_file.exists():
                print(f"ℹ️  Session file already exists at: {self.session_file}")
                response = (await asyncio.to_thread(input, "Do you want to create a new session? (yes/no): ")).strip().lower()
                if response not in ['yes', 'y']:
                    print("✅ Keeping existing session.")
                    return
                else:
                    print("🔄 Creating new session...")
            
            temp_browser = await self.playwright.chromium.launch(headless=False, slow_mo=200)
            temp_context = await temp_browser.new_context()
            temp_page = await temp_context.new_page()
            
            print("➡️ Opening login page...")
            await temp_page.goto(f"{self.base_url}/dang-nhap")
            
            print("⚙️ Please log in manually in the browser window.")
            print("✅ Once you're fully logged in, press Enter here.")
            await asyncio.to_thread(input, "Press Enter when ready...")
            
            # Save cookies and local storage
            await temp_context.storage_state(path=str(self.session_file))
            print(f"💾 Session saved successfully to '{self.session_file}'.")
            
        finally:
            # Clean up temporary browser resources
            if temp_page:
                await temp_page.close()
            if temp_context:
                await temp_context.close()
            if temp_browser:
                await temp_browser.close()
    
    async def _detect_captcha(self) -> bool:
        """Detect if CAPTCHA or access denied page is shown"""
        captcha_indicators = [
            "text=Truy cập không hợp lệ",
            "text=CAPTCHA",
            "text=xác thực",
            "[data-testid*='captcha']",
            ".g-recaptcha"
        ]
        
        for indicator in captcha_indicators:
            try:
                if await self.page.locator(indicator).is_visible(timeout=2000):
                    return True
            except Exception:
                pass
        return False
    
    async def _save_captcha_debug_artifacts(self):
        """Save debug artifacts when CAPTCHA is detected but no display is available"""
        debug_dir = Path(__file__).parent / ".sessions" / "debug_captcha"
        debug_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        screenshot_path = debug_dir / f"captcha_{timestamp}.png"
        html_path = debug_dir / f"captcha_{timestamp}.html"
        try:
            if self.page:
                await self.page.screenshot(path=str(screenshot_path), full_page=True)
                html = await self.page.content()
                await asyncio.to_thread(lambda: html_path.write_text(html, encoding="utf-8"))
            print(f"ℹ️ CAPTCHA detected but no display available. Saved screenshots/html to: {debug_dir}")
            print("ℹ️ To resolve: run the script locally (with GUI) or open the saved HTML/screenshot and complete the CAPTCHA manually in a browser session.")
        except Exception as e:
            print(f"⚠️ Failed to save debug artifacts: {e}")
    
    async def _handle_captcha(self):
        """Handle CAPTCHA by switching to headed mode"""
        print("⚠️ CAPTCHA detected! Switching to headed mode for manual verification...")
        
        # If environment cannot show browser (CI / headless server), save debug artifacts and abort
        def _can_show_browser():
            # macOS GUI normally ok; on CI or headless linux without DISPLAY, don't try to show
            if platform.system() == "Darwin":
                return True
            if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS") or os.environ.get("RUNNING_IN_DOCKER"):
                return False
            if os.environ.get("DISPLAY"):
                return True
            # fallback to tty check
            return sys.stdout.isatty()

        if not _can_show_browser():
            await self._save_captcha_debug_artifacts()
            raise RuntimeError("CAPTCHA detected and no display available to solve it automatically.")

        # Close current headless browser
        if self.page and not self.page.is_closed():
            await self.page.close()
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        
        # Relaunch in headed mode
        self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=150)
        self.context = await self.browser.new_context(storage_state=str(self.session_file))
        self.page = await self.context.new_page()
        
        await self.page.goto(self.data_url)
        print("✅ Please complete the CAPTCHA manually. The browser will continue after you close it.")
        await self.page.pause()
    
    async def crawl_stock_data(self):
        """Main method to crawl stock data from BizUni"""
        try:
            self._validate_environment()
            
            # Check if session exists
            if not self._session_exists():
                print(f"\n⚠️  No session found for user '{self.current_user}'")
                print("🔐 Starting login process...")
                await self.login_and_save_session()
                
                if not self._session_exists():
                    raise RuntimeError("❌ Session creation failed. Please try again.")
                print("✅ Session created successfully. Proceeding with data crawl...\n")
            
            print("\n=== 🚀 Starting data fetch... ===")
            
            # Launch browser with saved session
            # No need to clear cache/cookies - session handles authentication
            self.browser = await self.playwright.chromium.launch(headless=True)
            self.context = await self.browser.new_context(storage_state=str(self.session_file))
            self.page = await self.context.new_page()
            
            try:
                print(f"➡️ Navigating to {self.data_url}")
                await self.page.goto(self.data_url, timeout=60000, wait_until="networkidle")
                await self._human_delay()
                
                # Check for CAPTCHA
                if await self._detect_captcha():
                    await self._handle_captcha()
                    await self.page.goto(self.data_url, wait_until="networkidle")
                
                print(f"✅ Successfully loaded page {self.data_url}.")
                print("\n=== 🔍 Starting data extraction... ===")
                
                # Wait for table
                await self.page.wait_for_selector("#dataTable", timeout=15000)
                
                # Extract and save data
                filename = await self._extract_and_save_data()
                
                print(f"💾 Saved data to '{filename}'.")
                return filename
                
            except Exception as e:
                print(f"❌ Error during crawl: {e}")
                raise
                
        except Exception as e:
            print(f"❌ Crawling failed: {e}")
            raise
        finally:
            await self._cleanup()
    
    async def _extract_and_save_data(self):
        """Extract data from table and save to CSV"""
        try:
            # Wait for table to be fully loaded
            await self.page.wait_for_selector('#dataTable tbody tr', timeout=10000)
            
            # Get table headers
            headers = await self.page.evaluate('''
                () => {
                    const table = document.querySelector('#dataTable');
                    if (!table) return [];
                    const headerRow = table.querySelector('thead tr');
                    if (!headerRow) return [];
                    return Array.from(headerRow.cells).map(cell => cell.textContent.trim());
                }
            ''')
            
            # Get table rows
            rows_data = await self.page.evaluate('''
                () => {
                    const table = document.querySelector('#dataTable');
                    if (!table) return [];
                    const rows = table.querySelectorAll('tbody tr');
                    return Array.from(rows).map(row => 
                        Array.from(row.cells).map(cell => cell.textContent.trim())
                    );
                }
            ''')
            
            if not headers or not rows_data:
                raise ValueError("❌ Could not extract table data. Table might be empty or structure changed.")
            
            # Create DataFrame
            df = pd.DataFrame(rows_data, columns=headers)
            
            # Generate filename and date folder
            now = datetime.now()
            date_folder = now.strftime("%Y%m%d")
            time_str = now.strftime("%H%M%S")
            filename = f"bizuni_cpgt_{now.strftime('%d%m%Y')}_{time_str}.csv"
            
            # Create date-based folder structure
            data_dir = Path(__file__).parent.parent.parent.parent / "data" / date_folder / "BizUni_CPGT"
            data_dir.mkdir(parents=True, exist_ok=True)
            
            # Save to CSV
            filepath = data_dir / filename
            df.to_csv(filepath, index=False, encoding='utf-8-sig')
            
            # Keep only 3 latest bizuni files
            self._cleanup_old_files(data_dir)
            
            # Copy latest file to root data folder
            self._copy_to_root(filepath)
            
            print(f"📊 Data will be saved to: {filepath}")
            print(f"📈 Total records: {len(df)}")
            
            return filename
            
        except Exception as e:
            print(f"❌ Error extracting data: {e}")
            raise
    
    def _cleanup_old_files(self, data_dir: Path):
        """Keep only 3 latest bizuni files in the directory"""
        try:
            bizuni_files = list(data_dir.glob("bizuni_*.csv"))
            if len(bizuni_files) > 3:
                bizuni_files.sort(key=lambda f: f.stat().st_mtime, reverse=True)
                for old_file in bizuni_files[3:]:
                    old_file.unlink()
                    print(f"🗑️ Removed old file: {old_file.name}")
        except Exception as e:
            print(f"⚠️ Error cleaning up old files: {e}")
    
    def _copy_to_root(self, source_file: Path):
        """Copy latest file to project root data folder as bizuni_cpgt.csv"""
        try:
            import shutil
            root_data_dir = Path(__file__).parent.parent.parent.parent / "data"
            root_data_dir.mkdir(exist_ok=True)
            
            target_file = root_data_dir / "bizuni_cpgt.csv"
            shutil.copy2(source_file, target_file)
            print(f"📋 Copied to root: {target_file}")
        except Exception as e:
            print(f"⚠️ Error copying to root: {e}")
    
    async def _cleanup_page(self):
        """Clean up page resource"""
        if self.page:
            try:
                if not self.page.is_closed():
                    await self.page.close()
            except Exception:
                pass
    
    async def _cleanup_context(self):
        """Clean up context resource"""
        if self.context:
            try:
                await self.context.close()
            except Exception:
                pass
    
    async def _cleanup_browser(self):
        """Clean up browser resource"""
        if self.browser:
            try:
                await self.browser.close()
            except Exception:
                pass
    
    async def _cleanup_playwright(self):
        """Clean up playwright resource"""
        if self.playwright:
            try:
                await self.playwright.stop()
            except Exception:
                pass
    
    async def _cleanup(self):
        """Clean up browser resources (idempotent)"""
        if self._cleaned:
            return
        self._cleaned = True

        try:
            await self._cleanup_page()
            await self._cleanup_context()
            await self._cleanup_browser()
            await self._cleanup_playwright()
            print("\n🏁 Cleanup completed")
        except Exception as e:
            print(f"\n⚠️ Error during cleanup: {e}")

# Main functions
async def login_bizuni():
    """Login and save session"""
    async with BizUniCrawler() as crawler:
        await crawler.login_and_save_session()

async def crawl_bizuni_data():
    """Crawl BizUni stock data - auto-login if needed"""
    async with BizUniCrawler() as crawler:
        filename = await crawler.crawl_stock_data()
        return filename

async def reset_session():
    """Reset session for current user"""
    async with BizUniCrawler() as crawler:
        crawler._validate_environment()
        if crawler.session_file.exists():
            crawler.session_file.unlink()
            print(f"✅ Session deleted: {crawler.session_file}")
        else:
            print(f"ℹ️  No session found for user '{crawler.current_user}'")

def main():
    """Main function to handle command line arguments"""
    import sys
    
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "crawl"
    
    if command == "login":
        print("\n🔐 Starting login process...")
        try:
            asyncio.run(login_bizuni())
        except Exception as e:
            print(f"❌ Login failed: {e}")
    
    elif command == "reset":
        print("\n🔄 Resetting session...")
        try:
            asyncio.run(reset_session())
        except Exception as e:
            print(f"❌ Reset failed: {e}")
    
    elif command == "crawl":
        print("\n=== 📥 Starting data crawl... ===")
        try:
            filename = asyncio.run(crawl_bizuni_data())
            print(f"\n=> ✅ Successfully crawled data to: {filename}")
        except Exception as e:
            print(f"\n=> ❌ Crawling failed: {e}")
    
    else:
        print(f"\n=== ❌ Unknown command: {command} ===")
        print("Available commands: login, crawl, reset")

if __name__ == "__main__":
    main()