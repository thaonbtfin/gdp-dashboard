"""
TAstock Notification Service
Supports Telegram, Discord, Email, and Pushover notifications
"""
import requests
import smtplib
import os
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import Dict, List, Optional
import logging

class NotificationService:
    def __init__(self, config: Dict = None):
        self.config = config or {}
        self.logger = logging.getLogger(__name__)
        
    def send_telegram(self, message: str, parse_mode: str = "HTML") -> bool:
        """Send message via Telegram Bot"""
        bot_token = self.config.get('telegram_bot_token') or os.getenv('TELEGRAM_BOT_TOKEN')
        chat_id = self.config.get('telegram_chat_id') or os.getenv('TELEGRAM_CHAT_ID')
        
        if not bot_token or not chat_id:
            self.logger.warning(f"Telegram credentials missing - token: {'Yes' if bot_token else 'No'}, chat_id: {'Yes' if chat_id else 'No'}")
            return False
            
        try:
            url = f"https://api.telegram.org/bot{bot_token}/sendMessage"
            data = {
                "chat_id": chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            response = requests.post(url, data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Telegram send failed: {e}")
            return False
    
    def send_discord(self, message: str) -> bool:
        """Send message via Discord Webhook"""
        webhook_url = self.config.get('discord_webhook_url') or os.getenv('DISCORD_WEBHOOK_URL')
        
        if not webhook_url:
            self.logger.warning("Discord webhook not configured")
            return False
            
        try:
            data = {"content": message}
            response = requests.post(webhook_url, json=data, timeout=10)
            return response.status_code == 204
        except Exception as e:
            self.logger.error(f"Discord send failed: {e}")
            return False
    
    def send_email(self, subject: str, message: str) -> bool:
        """Send email notification"""
        smtp_server = self.config.get('smtp_server', 'smtp.gmail.com')
        smtp_port = self.config.get('smtp_port', 587)
        email_user = self.config.get('email_user') or os.getenv('EMAIL_USER')
        email_pass = self.config.get('email_pass') or os.getenv('EMAIL_PASS')
        email_to = self.config.get('email_to') or os.getenv('EMAIL_TO')
        
        if not all([email_user, email_pass, email_to]):
            self.logger.warning("Email credentials not configured")
            return False
            
        try:
            msg = MIMEMultipart()
            msg['From'] = email_user
            msg['To'] = email_to
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'html'))
            
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(email_user, email_pass)
            server.send_message(msg)
            server.quit()
            return True
        except Exception as e:
            self.logger.error(f"Email send failed: {e}")
            return False
    
    def send_pushover(self, message: str, title: str = "TAstock Alert") -> bool:
        """Send notification via Pushover"""
        app_token = self.config.get('pushover_app_token') or os.getenv('PUSHOVER_APP_TOKEN')
        user_key = self.config.get('pushover_user_key') or os.getenv('PUSHOVER_USER_KEY')
        
        if not app_token or not user_key:
            self.logger.warning("Pushover credentials not configured")
            return False
            
        try:
            data = {
                "token": app_token,
                "user": user_key,
                "message": message,
                "title": title
            }
            response = requests.post("https://api.pushover.net/1/messages.json", data=data, timeout=10)
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Pushover send failed: {e}")
            return False
    
    def send_notification(self, signal_data: Dict) -> Dict[str, bool]:
        """Send notification via all configured channels"""
        stock_code = signal_data.get('stock_code', 'Unknown')
        signal = signal_data.get('signal', 'HOLD')
        confidence = signal_data.get('confidence', 0)
        price = signal_data.get('price', 0)
        
        # Format message
        telegram_msg = self._format_telegram_message(stock_code, signal, confidence, price)
        discord_msg = self._format_discord_message(stock_code, signal, confidence, price)
        email_msg = self._format_email_message(stock_code, signal, confidence, price)
        pushover_msg = f"{signal} signal for {stock_code} (confidence: {confidence}%)"
        
        results = {}
        results['telegram'] = self.send_telegram(telegram_msg)
        results['discord'] = self.send_discord(discord_msg)
        results['email'] = self.send_email(f"TAstock Alert: {stock_code}", email_msg)
        results['pushover'] = self.send_pushover(pushover_msg)
        
        return results
    
    def _format_telegram_message(self, stock_code: str, signal: str, confidence: int, price: float) -> str:
        """Format message for Telegram"""
        emoji = "🚀" if signal == "BUY" else "🔻" if signal == "SELL" else "⏸️"
        return f"""
{emoji} <b>TAstock Alert</b>

📈 <b>{stock_code}</b>
🎯 Signal: <b>{signal}</b>
📊 Confidence: <b>{confidence}%</b>
💰 Price: <b>{price:,.0f} VND</b>

⏰ {self._get_timestamp()}
        """.strip()
    
    def _format_discord_message(self, stock_code: str, signal: str, confidence: int, price: float) -> str:
        """Format message for Discord"""
        emoji = "🚀" if signal == "BUY" else "🔻" if signal == "SELL" else "⏸️"
        return f"""
{emoji} **TAstock Alert**

📈 **{stock_code}**
🎯 Signal: **{signal}**
📊 Confidence: **{confidence}%**
💰 Price: **{price:,.0f} VND**

⏰ {self._get_timestamp()}
        """.strip()
    
    def _format_email_message(self, stock_code: str, signal: str, confidence: int, price: float) -> str:
        """Format HTML message for Email"""
        color = "#28a745" if signal == "BUY" else "#dc3545" if signal == "SELL" else "#ffc107"
        return f"""
        <html>
        <body style="font-family: Arial, sans-serif;">
            <h2 style="color: {color};">TAstock Investment Alert</h2>
            <table style="border-collapse: collapse; width: 100%;">
                <tr><td><strong>Stock:</strong></td><td>{stock_code}</td></tr>
                <tr><td><strong>Signal:</strong></td><td style="color: {color}; font-weight: bold;">{signal}</td></tr>
                <tr><td><strong>Confidence:</strong></td><td>{confidence}%</td></tr>
                <tr><td><strong>Price:</strong></td><td>{price:,.0f} VND</td></tr>
                <tr><td><strong>Time:</strong></td><td>{self._get_timestamp()}</td></tr>
            </table>
        </body>
        </html>
        """
    
    def _get_timestamp(self) -> str:
        """Get formatted timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")