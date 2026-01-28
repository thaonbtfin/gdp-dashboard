"""
Notification Configuration Manager
"""
import os
import json
import requests
from typing import Dict, Optional

class NotificationConfig:
    def __init__(self, gdrive_url: str = None, local_file: str = None):
        self.gdrive_url = gdrive_url
        self.local_file = local_file or os.path.join(os.path.dirname(__file__), 'notification_config.json')
        self.config = self._load_config()
    
    def _load_config(self) -> Dict:
        """Load configuration from Google Drive or local file"""
        config = {}
        
        # Try to load from Google Drive first
        if self.gdrive_url:
            try:
                config = self._load_from_gdrive()
                if config:
                    return config
            except Exception:
                pass
        
        # Fallback to local file
        if os.path.exists(self.local_file):
            try:
                with open(self.local_file, 'r') as f:
                    config = json.load(f)
            except Exception:
                pass
        
        # Default config if nothing found
        if not config:
            config = {
                'notification_threshold': 80,
                'enabled_channels': ['telegram', 'discord']
            }
        
        return config
    
    def _load_from_gdrive(self) -> Dict:
        """Load configuration from Google Drive file"""
        try:
            # Handle different Google Drive URL formats
            if '/file/d/' in self.gdrive_url:
                file_id = self.gdrive_url.split('/file/d/')[1].split('/')[0]
                download_url = f"https://drive.google.com/uc?id={file_id}&export=download"
            elif '/folders/' in self.gdrive_url:
                # For folder URLs, user needs to provide direct file URL
                return {}
            else:
                download_url = self.gdrive_url
            
            response = requests.get(download_url, timeout=10)
            response.raise_for_status()
            return response.json()
        except Exception:
            return {}
    
    def save_config(self, new_config: Dict):
        """Save configuration to local file"""
        self.config.update(new_config)
        try:
            with open(self.local_file, 'w') as f:
                json.dump(self.config, f, indent=2)
        except Exception as e:
            print(f"Failed to save config: {e}")
    
    def get(self, key: str, default=None):
        """Get configuration value"""
        return self.config.get(key, default)
    
    def is_channel_enabled(self, channel: str) -> bool:
        """Check if notification channel is enabled"""
        enabled_channels = self.config.get('enabled_channels', [])
        return channel in enabled_channels
    
    def get_threshold(self) -> int:
        """Get notification confidence threshold"""
        return self.config.get('notification_threshold', 80)
    
    def set_gdrive_url(self, url: str):
        """Set Google Drive URL and reload config"""
        self.gdrive_url = url
        self.config = self._load_config()
    
    def validate_config(self) -> Dict[str, bool]:
        """Validate configuration for each channel"""
        return {
            'telegram': bool(self.config.get('telegram_bot_token') and self.config.get('telegram_chat_id')),
            'discord': bool(self.config.get('discord_webhook_url')),
            'email': bool(self.config.get('email_user') and self.config.get('email_pass') and self.config.get('email_to')),
            'pushover': bool(self.config.get('pushover_app_token') and self.config.get('pushover_user_key'))
        }