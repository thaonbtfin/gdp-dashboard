"""
BizUni Crawler for fetching stock data from bizuni.vn
Supports both manual login and automated crawling with session management
Automatically detects and uses existing sessions or prompts for login
"""

import asyncio
import pandas as pd
from playwright.async_api import async_playwright
import platform
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
        self._cleaned = False  # prevent double cleanup prints / operations
    
    async def __aenter__(self):
        self.playwright = await async_playwright().start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self._cleanup()
    
    async def _human_delay(self, min_s=2.5, max_s=5.0):
        """Random delay to mimic human behavior"""
        delay = random.uniform(min_s, max_s)
        await asyncio.sleep(delay)
    
    def _get_credentials(self):
        """Get credentials based on machine user - only on Mac for thao/anh"""
        import getpass
        
        current_os = platform.system()
        username = getpass.getuser().lower()
        
        print(f"🔍 _get_credentials debug:")
        print(f"   OS: '{current_os}' (Darwin check: {current_os == 'Darwin'})")
        print(f"   User: '{username}' (in list: {username in ['thaonguyen', 'anhchau']})")
        
        # Only allow automation on Mac
        if current_os != "Darwin":
            print(f"   ❌ OS not Darwin, returning None")
            return None
            
        # Only allow specific users - check exact username
        if username not in ['thaonguyen', 'anhchau']:
            print(f"   ❌ User '{username}' not in allowed list ['thaonguyen', 'anhchau'], returning None")
            return None
        
        credentials = {
            'thaonguyen': {
                'email': 'nb2t71@gmail.com',
                'password': '070186'
            },
            'anhchau': {
                'email': 'anh.chau515@gmail.com',
                'password': '170583'
            }
        }
        
        result = credentials.get(username)
        print(f"   ✅ Credentials lookup result: {result is not None}")
        if result:
            print(f"   📧 Email: {result['email']}")
            print(f"   🔑 Password length: {len(result['password'])} chars")
        else:
            print(f"   ❌ No credentials found for user: {username}")
        return result
    
    async def _try_auto_login(self):
        """Try automated login with stored credentials"""
        creds = self._get_credentials()
        if not creds:
            import getpass
            current_user = getpass.getuser().lower()
            current_os = platform.system()
            print(f"⚠️ Automated login not available")
            print(f"   Current OS: {current_os} (requires: Darwin/Mac)")
            print(f"   Current user: {current_user} (requires: thao or anh)")
            return False
        
        print(f"🤖 Attempting automated login for user: {creds['email']}")
        
        try:
            # Wait for page to load completely
            print("🔄 Waiting for page to load...")
            await self.page.wait_for_load_state('domcontentloaded', timeout=15000)
            await self._human_delay(2, 3)
            
            # Check if already logged in
            current_url = self.page.url
            if 'dang-nhap' not in current_url:
                print("✅ Already logged in")
                return True
            
            # Use multiple selector strategies
            username_selectors = [
                '#form-element-username',
                'input[name="username"]',
                'input[type="email"]',
                'input[placeholder*="email"]'
            ]
            
            password_selectors = [
                '#form-element-password', 
                'input[name="password"]',
                'input[type="password"]'
            ]
            
            login_button_selectors = [
                'button[type="submit"].btn.btn-p',
                'button[type="submit"]',
                '.btn-primary',
                'input[type="submit"]'
            ]
            
            # Find username field
            username_field = None
            for selector in username_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    username_field = selector
                    print(f"✅ Found username field: {selector}")
                    break
                except:
                    continue
            
            if not username_field:
                print("❌ Could not find username field")
                return False
            
            # Find password field
            password_field = None
            for selector in password_selectors:
                try:
                    await self.page.wait_for_selector(selector, timeout=3000)
                    password_field = selector
                    print(f"✅ Found password field: {selector}")
                    break
                except:
                    continue
            
            if not password_field:
                print("❌ Could not find password field")
                return False
            
            # Clear and fill username
            await self.page.click(username_field)
            await self.page.fill(username_field, '')
            await self.page.type(username_field, creds['email'], delay=100)
            print(f"✅ Username entered: {creds['email']}")
            await self._human_delay(1, 2)
            
            # Clear and fill password
            await self.page.click(password_field)
            await self.page.fill(password_field, '')
            await self.page.type(password_field, creds['password'], delay=100)
            print("✅ Password entered")
            await self._human_delay(1, 2)
            
            # Find and click login button
            login_button = None
            for selector in login_button_selectors:
                try:
                    if await self.page.locator(selector).is_visible():
                        login_button = selector
                        print(f"✅ Found login button: {selector}")
                        break
                except:
                    continue
            
            if not login_button:
                print("❌ Could not find login button")
                return False
            
            # Click login button
            await self.page.click(login_button)
            print("✅ Login button clicked")
            
            # Wait for navigation
            print("⏳ Waiting for login to complete...")
            try:
                await self.page.wait_for_load_state('networkidle', timeout=15000)
            except:
                print("⚠️ Timeout waiting for networkidle")
            
            await self._human_delay(2, 3)
            
            # Check if login was successful
            current_url = self.page.url
            print(f"🌐 Current URL: {current_url}")
            
            if 'dang-nhap' not in current_url:
                print("✅ Automated login successful")
                return True
            else:
                print("❌ Still on login page - login failed")
                return False
                
        except Exception as e:
            print(f"⚠️ Automated login failed: {e}")
            return False
    
    async def manual_login_prompt(self):
        """Try automated login first, fallback to manual login"""
        try:
            # Start in headed mode for login
            self.browser = await self.playwright.chromium.launch(headless=False, slow_mo=200)
            self.context = await self.browser.new_context()
            self.page = await self.context.new_page()
            
            print("➡️ Opening BizUni login page...")
            try:
                await self.page.goto(f"{self.base_url}/dang-nhap", wait_until='domcontentloaded', timeout=60000)
                print("✅ Login page loaded")
            except Exception as e:
                print(f"❌ Failed to load login page: {e}")
                print("⚠️ BizUni website may be down or blocked")
                raise
            
            # Try automated login first
            print("\n🤖 Attempting automated login...")
            if await self._try_auto_login():
                print("✅ Automated login succeeded, proceeding with data extraction")
                return
            
            # Fallback to manual login
            print("❌ Automated login failed, falling back to manual login")
            print("\n" + "="*60)
            print("🔐 MANUAL LOGIN REQUIRED")
            print("="*60)
            print("Please login manually in the browser window.")
            print("="*60)
            await asyncio.to_thread(input, "\n👆 Press Enter AFTER you have successfully logged in: ")
            
            print("✅ Manual login completed")
            
        except Exception as e:
            print(f"❌ Login process failed: {e}")
            raise
    
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
        debug_dir = Path(__file__).parent / "debug_captcha"
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
        """Handle CAPTCHA by pausing for manual intervention"""
        print("⚠️ CAPTCHA detected! Please solve it manually in the browser.")
        
        # If environment cannot show browser, save debug artifacts
        def _can_show_browser():
            if platform.system() == "Darwin":
                return True
            if os.environ.get("CI") or os.environ.get("GITHUB_ACTIONS") or os.environ.get("RUNNING_IN_DOCKER"):
                return False
            if os.environ.get("DISPLAY"):
                return True
            return sys.stdout.isatty()

        if not _can_show_browser():
            await self._save_captcha_debug_artifacts()
            raise RuntimeError("CAPTCHA detected and no display available to solve it automatically.")

        # Wait for user to solve CAPTCHA
        await asyncio.to_thread(input, "Press Enter after solving CAPTCHA...")
    
    async def crawl_stock_data(self):
        """Main method to crawl stock data from BizUni"""
        try:
            # Start login process (auto + manual fallback)
            print("\n🔐 Starting login process (automated + manual fallback)...")
            await self.manual_login_prompt()
            
            print("✅ Login completed. Proceeding with data crawl...\n")
            print("\n=== 🚀 Starting data fetch... ===")
            
            try:
                print(f"➡️ Navigating to {self.data_url}")
                await self.page.goto(self.data_url, timeout=60000, wait_until="load")
                await self._human_delay()
                
                # Check for CAPTCHA on data page
                if await self._detect_captcha():
                    await self._handle_captcha()
                
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
async def crawl_bizuni_data():
    """Crawl BizUni stock data with manual login"""
    async with BizUniCrawler() as crawler:
        filename = await crawler.crawl_stock_data()
        return filename

def main():
    """Main function to handle command line arguments"""
    import sys
    
    command = sys.argv[1].lower() if len(sys.argv) > 1 else "crawl"
    
    if command == "crawl":
        print("\n=== 📥 Starting data crawl... ===")
        try:
            filename = asyncio.run(crawl_bizuni_data())
            print(f"\n=> ✅ Successfully crawled data to: {filename}")
        except Exception as e:
            print(f"\n=> ❌ Crawling failed: {e}")
    
    else:
        print(f"\n=== ❌ Unknown command: {command} ===")
        print("Available commands: crawl")

if __name__ == "__main__":
    main()