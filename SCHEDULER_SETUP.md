# 📅 Automated Scheduling Setup

## 🚀 Quick Setup (Recommended)

**For macOS/Linux:**
```bash
# From project directory, run this one command:
echo "0 18 * * 1-5 $(pwd)/schedule_updater.sh" | crontab -
```

**For Windows:**
Use Task Scheduler (see detailed steps below).

---

## 🕰 Schedule Details
- **Time**: 6:00 PM (18:00) daily
- **Days**: Monday through Friday only
- **Excludes**: Saturday and Sunday
- **Logs**: Saved to `data/scheduler.log`

## 🔧 Detailed Setup Instructions

### For macOS/Linux (using cron):
1. **Get full project path:**
```bash
cd /path/to/gdp-dashboard
pwd  # Copy this full path
```

2. **Edit crontab:**
```bash
crontab -e
```

3. **Add this line (replace with your actual path):**
```bash
0 18 * * 1-5 /full/path/to/gdp-dashboard/schedule_updater.sh
```

### Cron Schedule Explanation:
- `0 18 * * 1-5` = At 6:00 PM (18:00) on weekdays (Monday=1 to Friday=5)
- Excludes Saturday (6) and Sunday (0)

### For Windows (using Task Scheduler):

1. **Open Task Scheduler**
2. **Create Basic Task**
3. **Set trigger:** Daily at 6:00 PM
4. **Set days:** Monday through Friday only
5. **Action:** Start program
6. **Program:** `python`
7. **Arguments:** `src/tastock/workflows/wf_stock_data_updater.py`
8. **Start in:** Full path to your gdp-dashboard folder

## 📋 Verify Setup

Check if cron job is active:
```bash
crontab -l
```

View scheduler logs:
```bash
tail -f data/scheduler.log
```

## 🛑 Remove Schedule

To remove the scheduled job:
```bash
crontab -e
# Delete the line and save
```