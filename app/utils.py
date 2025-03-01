import re
import time
import platform
import os
import json

def clean_filename(filename):
    """Remove invalid characters from filename"""
    # Replace invalid characters with underscore
    return re.sub(r'[\\/*?:"<>|]', "_", filename)

def get_system_info():
    """Get current system information"""
    return {
        'platform': platform.system(),
        'platform_release': platform.release(),
        'platform_version': platform.version(),
        'architecture': platform.machine(),
        'processor': platform.processor(),
        'python_version': platform.python_version()
    }

def create_user_settings_dir():
    """Create user settings directory if it doesn't exist"""
    home = os.path.expanduser("~")
    settings_dir = os.path.join(home, ".madick_ai")
    
    if not os.path.exists(settings_dir):
        os.makedirs(settings_dir)
        
    return settings_dir

def save_user_settings(settings):
    """Save settings to user settings directory"""
    settings_dir = create_user_settings_dir()
    settings_file = os.path.join(settings_dir, "settings.json")
    
    with open(settings_file, 'w') as f:
        json.dump(settings, f, indent=2)

def load_user_settings():
    """Load settings from user settings directory"""
    settings_dir = create_user_settings_dir()
    settings_file = os.path.join(settings_dir, "settings.json")
    
    if os.path.exists(settings_file):
        with open(settings_file, 'r') as f:
            return json.load(f)
    
    return {}

def format_bytes(bytes_num):
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if bytes_num < 1024:
            return f"{bytes_num:.2f} {unit}"
        bytes_num /= 1024
    return f"{bytes_num:.2f} PB"

class Timer:
    """Simple timer for measuring execution time"""
    
    def __init__(self, name=""):
        self.name = name
        self.start_time = None
        
    def __enter__(self):
        self.start_time = time.time()
        return self
        
    def __exit__(self, exc_type, exc_val, exc_tb):
        elapsed = time.time() - self.start_time
        if self.name:
            print(f"{self.name} took {elapsed:.4f} seconds")
        else:
            print(f"Execution took {elapsed:.4f} seconds")

def truncate_text(text, max_length=100):
    """Truncate text to maximum length and add ellipsis if needed"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."
