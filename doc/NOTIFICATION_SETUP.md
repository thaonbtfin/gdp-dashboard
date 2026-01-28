# 🔔 TAstock Notification Setup Guide

## 📱 Quick Setup (Free Options)

### 1. Telegram Bot (Recommended - Free)
1. **Create Bot**: Message @BotFather on Telegram
   - Send `/newbot`
   - Choose bot name and username
   - Copy the **Bot Token**

2. **Get Chat ID**:
   - Start chat with your bot
   - Send any message
   - Visit: `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Copy the **Chat ID** from response

3. **Configure in TAstock**:
   - Create JSON config file (see sample below)
   - Upload to Google Drive
   - Share with "Anyone with the link" can view
   - Copy share URL to TAstock

### 2. Discord Webhook (Free)
1. **Create Webhook**:
   - Go to Discord Server Settings → Integrations → Webhooks
   - Click "New Webhook"
   - Copy the **Webhook URL**

2. **Configure**:
   - Add webhook URL to Google Drive config file

## 📧 Email Setup (Gmail)

1. **Enable App Password**:
   - Go to Google Account Settings
   - Security → 2-Step Verification → App passwords
   - Generate password for "Mail"

2. **Configure**:
   - Add email settings to Google Drive config file

## 📱 Pushover Setup ($5 one-time)

1. **Create Account**: Register at pushover.net
2. **Get Credentials**:
   - User Key from dashboard
   - Create application for App Token

3. **Configure**:
   - Add Pushover settings to Google Drive config file

## ⚙️ Configuration Options

### Google Drive Config File
```json
{
  "telegram_bot_token": "your_bot_token",
  "telegram_chat_id": "your_chat_id",
  "discord_webhook_url": "your_webhook_url",
  "email_user": "your_email@gmail.com",
  "email_pass": "your_app_password",
  "email_to": "recipient@gmail.com",
  "pushover_app_token": "your_app_token",
  "pushover_user_key": "your_user_key",
  "notification_threshold": 80,
  "enabled_channels": ["telegram", "discord"]
}
```

### Setup Steps
1. Create JSON file with above content
2. Upload to Google Drive
3. Share with "Anyone with the link" can view
4. Copy share URL
5. Paste URL in TAstock notification settings

### Streamlit UI
- Use the **🔔 Thông báo** tab in the app
- Configure all settings through the web interface
- Test notifications before saving

## 🚀 Usage

### Automatic Notifications
- Notifications sent during data pipeline execution
- Only high-confidence signals (above threshold)
- Runs with `wf_stock_data_updater.py`

### Manual Notifications
```bash
# Send notifications for current signals
python src/tastock/scripts/send_notifications.py
```

### Streamlit Integration
- Configure in **🔔 Thông báo** tab
- Test notifications with sample data
- Send immediate notifications for high-priority BUY signals

## 📊 Notification Format

### Telegram/Discord
```
🚀 TAstock Alert

📈 ACB
🎯 Signal: BUY
📊 Confidence: 85%
💰 Price: 25,000 VND

⏰ 2024-01-15 14:30:00
```

### Email
- HTML formatted with colors
- Green for BUY, Red for SELL
- Detailed table format

## 🔧 Troubleshooting

### Common Issues
1. **Telegram "Unauthorized"**: Check bot token
2. **Discord "Not Found"**: Verify webhook URL
3. **Email "Authentication Failed"**: Use app password, not regular password
4. **No Notifications**: Check threshold settings and signal confidence

### Debug Mode
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🎯 Best Practices

1. **Start with Telegram**: Easiest to setup and test
2. **Use Multiple Channels**: Redundancy for important signals
3. **Set Appropriate Threshold**: 80%+ for high-quality signals
4. **Test Regularly**: Use the test button in Streamlit
5. **Monitor Logs**: Check for delivery failures

## 📈 Integration with Investment Analysis

- Notifications triggered by `InvestmentSignalCalculator`
- Based on combined analysis (Value + CANSLIM + Technical)
- Priority system using BizUni data
- Confidence scoring for signal quality