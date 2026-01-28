"""
Google Drive Configuration Helper
"""
import json
from pathlib import Path

# Default Google Drive URL for shared config
DEFAULT_GDRIVE_URL = "https://drive.google.com/drive/folders/1250E9USH25t0sy3np9ajhurpdYROpm9N?usp=sharing"

def get_gdrive_url() -> str:
    """Get Google Drive URL from local settings"""
    settings_file = Path(__file__).parent / "gdrive_settings.json"
    
    if settings_file.exists():
        try:
            with open(settings_file, 'r') as f:
                settings = json.load(f)
                return settings.get('gdrive_url', DEFAULT_GDRIVE_URL)
        except Exception:
            pass
    
    return DEFAULT_GDRIVE_URL

def set_gdrive_url(url: str):
    """Save Google Drive URL to local settings"""
    settings_file = Path(__file__).parent / "gdrive_settings.json"
    
    try:
        settings = {'gdrive_url': url}
        with open(settings_file, 'w') as f:
            json.dump(settings, f, indent=2)
        return True
    except Exception:
        return False

def create_config_file_in_folder():
    """Instructions to create config file in the shared folder"""
    return {
        'folder_url': DEFAULT_GDRIVE_URL,
        'filename': 'notification_config.json',
        'content': create_sample_config()
    }

def create_sample_config():
    """Create sample notification config for Google Drive"""
    sample_config = {
        "telegram_bot_token": "",
        "telegram_chat_id": "",
        "discord_webhook_url": "",
        "email_user": "",
        "email_pass": "",
        "email_to": "",
        "pushover_app_token": "",
        "pushover_user_key": "",
        "notification_threshold": 80,
        "enabled_channels": ["telegram", "discord"]
    }
    
    return json.dumps(sample_config, indent=2)

def get_folder_instructions():
    """Get instructions for using the shared Google Drive folder"""
    return """
📁 **Setup Steps:**

1. **Access folder**: https://drive.google.com/drive/folders/1250E9USH25t0sy3np9ajhurpdYROpm9N
2. **Upload config**: Upload `notification_config.json` with your settings
3. **Share file**: Right-click file → Share → "Anyone with link can view"
4. **Copy URL**: Copy the file's share URL (not folder URL)
5. **Paste below**: Add the file URL in the configuration

**Alternative**: Use local config file if Google Drive not accessible
    """