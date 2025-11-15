# BizUni Crawler - User Guide

A Python script to automatically fetch and save stock data from [bizuni.vn](https://bizuni.vn) with auto-login functionality.

## 📋 Prerequisites

- **OS**: macOS (Darwin)
- **Python**: 3.8+
- **User**: Must be `thaonguyen` or `anhchau`
- **Credentials**: Pre-configured for each user

## 🔧 Installation

### 1. Install Python Dependencies

```bash
pip install playwright pandas
playwright install
```

### 2. Project Structure

```
gdp-dashboard/
├── src/
│   └── tastock/
│       └── crawlers/
│           ├── bizuni_crawler.py          # Main crawler script
│           └── debug_captcha/             # CAPTCHA debug files (auto-created)
└── data/                                  # Output data folder
    └── bizuni_cpgt_DDMMYYYY_HHMMSS.csv
```

## 🚀 Quick Start

### Auto-Login Process

Simply run the script without any arguments:

```bash
cd /Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/src/tastock/crawlers
python bizuni_crawler.py
```

**What happens:**

1. ✅ Script validates your macOS environment and loads your credentials
2. 🔐 Opens browser and automatically fills login form
3. ⚠️ Handles CAPTCHA if present (manual intervention required)
4. ✅ Completes login automatically
5. 📥 Fetches and saves stock data to CSV

### Every Run is Fresh

- 🔄 **No session storage** - fresh login every time
- 🤖 **Auto-fill credentials** - based on your machine user
- 🛡️ **CAPTCHA handling** - pauses for manual solving when needed
- ⚡ **Robust selectors** - tries multiple form field selectors

## 📌 Available Commands

### 1. **Default - Crawl Data**

```bash
python bizuni_crawler.py
```

Fetches stock data with auto-login. Fresh login every time.

### 2. **Login Only**

```bash
python bizuni_crawler.py login
```

Performs login process only without data crawling. Useful for:

- Testing login functionality
- Verifying credentials
- Debugging login issues

### 3. **Explicit Crawl**

```bash
python bizuni_crawler.py crawl
```

Same as running without arguments. Explicit way to fetch data.

## 📊 Output

Data is saved to: `/data/bizuni_cpgt_<DDMMYYYY>_<HHMMSS>.csv`

Example filename: `bizuni_cpgt_13112025_143022.csv`

**File contains:**

- Stock ticker symbols
- Stock prices
- Other market data in table format
- UTF-8 encoded (supports Vietnamese characters)

## 🔐 Auto-Login System

### How Auto-Login Works

- **Fresh login every time**: No session storage, always starts fresh
- **Automatic credential filling**: Uses pre-configured credentials based on machine user
- **Smart form detection**: Tries multiple selectors to find login fields
- **CAPTCHA handling**: Pauses for manual intervention when CAPTCHA appears

### User Credentials

- **thaonguyen** → nb2t71@gmail.com (password: 070186)
- **anhchau** → anh.chau515@gmail.com (password: [need to fulfill])

### Form Field Detection

The script tries multiple selectors for robust form filling:
- **Email field**: `name="email"`, `name="username"`, `type="email"`, placeholder-based
- **Password field**: `name="password"`, `type="password"`
- **Submit button**: `type="submit"`, Vietnamese/English text, CSS classes

## ⚠️ Troubleshooting

### Issue: CAPTCHA appears on login page

**What happens**:

1. Script opens browser in headed mode
2. Detects CAPTCHA and pauses
3. Prompts you to solve CAPTCHA manually
4. Continues auto-login after you press Enter

**Action needed**: Solve CAPTCHA in browser, then press Enter in terminal.

### Issue: CAPTCHA appears during data crawl

**What happens**:

1. Script detects CAPTCHA on data page
2. Pauses for manual intervention
3. Script continues after you solve it

**Action needed**: Solve CAPTCHA in browser, then press Enter in terminal.

### Issue: "Could not find email/username input field"

**Possible causes**:

- ❌ BizUni changed their form structure
- ❌ Page didn't load completely

**Solution**: Check browser window, wait for page to load, or report issue.

### Issue: "Incorrect running environment"

**Possible causes**:

- ❌ Running on non-macOS system
- ❌ User is not `thaonguyen` or `anhchau`

**Solution**: Run only on macOS as the correct user.

```bash
whoami  # Check your username
```

### Issue: Login credentials not working

**Solution**: Update credentials in the script for your user.

### Issue: DataFrame/Pandas error

**Solution**: Ensure pandas is installed

```bash
pip install --upgrade pandas
```

### Issue: Browser not found

**Solution**: Reinstall Playwright

```bash
pip install --upgrade playwright
playwright install chromium
```

## 🔄 Automation (Scheduling)

### macOS - Using Launchd

Create a file: `~/Library/LaunchAgents/com.bizuni.crawler.plist`

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.bizuni.crawler</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>/Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/src/tastock/crawlers/bizuni_crawler.py</string>
    </array>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>/tmp/bizuni_crawler.log</string>
    <key>StandardErrorPath</key>
    <string>/tmp/bizuni_crawler_error.log</string>
</dict>
</plist>
```

Load it:

```bash
launchctl load ~/Library/LaunchAgents/com.bizuni.crawler.plist
```

Run daily at 9:00 AM automatically.

### macOS - Using Cron

Edit crontab:

```bash
crontab -e
```

Add line (runs at 9:00 AM daily):

```
0 9 * * * cd /Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/src/tastock/crawlers && python3 bizuni_crawler.py
```

## 📝 Log Output Example

```
✅ Environment validated for user: thaonguyen
🚀 Starting data fetch...
➡️ Navigating to https://bizuni.vn/co-phieu-gia-tri
✅ Page loaded successfully. Extracting data...
📊 Data saved to: /Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/data/bizuni_cpgt_13112025_143022.csv
📈 Total records: 245
💾 Successfully saved data to 'bizuni_cpgt_13112025_143022.csv'.
🏁 Cleanup completed
```

## 🛠️ Development

### File Location

```
/Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/src/tastock/crawlers/bizuni_crawler.py
```

### Key Features

- ✅ Auto-login with pre-configured credentials
- ✅ Smart form field detection (multiple selectors)
- ✅ Automatic CAPTCHA detection and handling
- ✅ Fresh login every time (no session storage)
- ✅ Human-like delays to avoid detection
- ✅ Comprehensive error handling
- ✅ Pandas DataFrame for data processing

### Supported Users

- `thaonguyen` → nb2t71@gmail.com
- `anhchau` → anh.chau515@gmail.com (password needed)

## ❓ FAQ

**Q: Will the script work if I close the terminal?**
A: No, the script needs terminal interaction for CAPTCHA handling.

**Q: How long does crawling take?**
A: Typically 60-90 seconds including fresh login and potential CAPTCHA.

**Q: Can multiple users use the same script?**
A: Yes! Credentials are automatically selected based on machine user.

**Q: Is my password stored securely?**
A: Passwords are hardcoded in the script for automation. Keep script secure.

**Q: Why no session storage?**
A: BizUni has session time limits, so fresh login is more reliable.

**Q: What if CAPTCHA appears every time?**
A: This is normal. Just solve it manually when prompted.

**Q: What if I forget to import pandas?**
A: Script will fail with helpful error. Just run: `pip install pandas`

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the terminal output for error messages
3. Ensure browser window is visible for CAPTCHA solving
4. Try running `python bizuni_crawler.py login` to test login only

---

**Last Updated**: November 13, 2025
**Version**: 2.0 (Auto-Login)
