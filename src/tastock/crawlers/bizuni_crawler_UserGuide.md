# BizUni Crawler - User Guide

A Python script to automatically fetch and save stock data from [bizuni.vn](https://bizuni.vn).

## 📋 Prerequisites

- **OS**: macOS (Darwin)
- **Python**: 3.8+
- **User**: Must be `thaonguyen` or `anhchau`

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
│           └── .sessions/                 # Session storage (auto-created)
│               ├── auth_state_thaonguyen.json
│               └── auth_state_anhchau.json
└── data/                                  # Output data folder
    └── bizuni_cpgt_DDMMYYYY_HHMMSS.csv
```

## 🚀 Quick Start

### First Run (Automatic Login)

Simply run the script without any arguments:

```bash
cd /Users/thaonguyen/dev/github/thaonbtfin/gdp-dashboard/src/tastock/crawlers
python bizuni_crawler.py
```

**What happens:**

1. ✅ Script validates your macOS environment
2. ✅ Detects you don't have a saved session
3. 🔐 Opens browser and prompts you to log in manually
4. ✅ Saves your session automatically
5. 📥 Fetches and saves stock data to CSV

### Subsequent Runs (Automatic)

Just run the same command:

```bash
python bizuni_crawler.py
```

**What happens:**

- ✅ Script detects existing session
- ✅ Reuses saved session automatically
- 📥 Fetches and saves data without manual login
- ⚠️ If CAPTCHA appears, switches to headed mode for manual verification

## 📌 Available Commands

### 1. **Default - Crawl Data**

```bash
python bizuni_crawler.py
```

Fetches stock data. Auto-logs in first time, reuses session afterwards.

### 2. **Force New Login**

```bash
python bizuni_crawler.py login
```

Creates a fresh session, even if one exists. Useful if:

- Your session has expired
- You want to update credentials
- Previous login failed

### 3. **Reset Session**

```bash
python bizuni_crawler.py reset
```

Deletes the saved session file for your account. Use this if:

- You want to start fresh
- Session is corrupted
- You're switching accounts

### 4. **Explicit Crawl**

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

## 🔐 Session Management

### How Sessions Work

- **First login**: Script opens browser, you log in manually → saves session
- **Subsequent runs**: Script uses saved session → no login needed
- **Session file location**: `.sessions/auth_state_<username>.json`
- **Per-user sessions**: Each account has its own session file

### Session Files

```
.sessions/
├── auth_state_thaonguyen.json    # Thao's session
└── auth_state_anhchau.json        # Anh's session
```

## ⚠️ Troubleshooting

### Issue: "No session found" on first run

**Solution**: Run the script normally - it will auto-prompt for login.

```bash
python bizuni_crawler.py
```

### Issue: CAPTCHA appears during crawl

**What happens**:

1. Script detects CAPTCHA
2. Automatically switches to headed mode
3. Browser opens for manual CAPTCHA completion
4. Script continues after you solve it

**No action needed** - just complete the CAPTCHA in the browser.

### Issue: "Incorrect running environment"

**Possible causes**:

- ❌ Running on non-macOS system
- ❌ User is not `thaonguyen` or `anhchau`

**Solution**: Run only on macOS as the correct user.

```bash
whoami  # Check your username
```

### Issue: Session expired or invalid

**Solution**: Reset and create new session

```bash
python bizuni_crawler.py reset    # Delete old session
python bizuni_crawler.py login    # Create new session
```

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

- ✅ Session-based authentication (no repeated logins)
- ✅ User-specific session files
- ✅ Automatic CAPTCHA detection and handling
- ✅ Headless mode for automation
- ✅ Human-like delays to avoid detection
- ✅ Comprehensive error handling
- ✅ Pandas DataFrame for data processing

### Supported Users

- `thaonguyen` → nb2t71@gmail.com
- `anhchau` → anh.chau515@gmail.com (password needed)

## ❓ FAQ

**Q: Will the script work if I close the terminal?**
A: Yes, Playwright runs independently. Only affects interactive login prompts.

**Q: How long does crawling take?**
A: Typically 30-60 seconds depending on page load time and data size.

**Q: Can multiple users use the same script?**
A: Yes! Each user has their own session file automatically.

**Q: Is my password stored?**
A: No. Only session cookies/tokens are saved, not passwords.

**Q: Can I share session files?**
A: Not recommended. Sessions are tied to machine/user. Each user should log in once.

**Q: What if I forget to import pandas?**
A: Script will fail with helpful error. Just run: `pip install pandas`

## 📞 Support

If you encounter issues:

1. Check the **Troubleshooting** section above
2. Review the terminal output for error messages
3. Run with `python bizuni_crawler.py login` to refresh session
4. Reset session with `python bizuni_crawler.py reset`

---

**Last Updated**: November 13, 2025
**Version**: 1.0
