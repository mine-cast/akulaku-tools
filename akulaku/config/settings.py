"""
Akulaku Dropship Configuration
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv('config/.env')

# API Configuration
AKULAKU_APP_KEY = os.getenv('AKULAKU_APP_KEY', '')
AKULAKU_APP_SECRET=*** '')
AKULAKU_API_BASE = os.getenv('AKULAKU_API_BASE', 'https://open.akulaku.com/api')

# Telegram Notifications
NOTIFICATION_TELEGRAM = os.getenv('AKULAKU_NOTIFICATION_TELEGRAM', 'false').lower() == 'true'
TELEGRAM_CHAT_ID = os.getenv('AKULAKU_TELEGRAM_CHAT_ID', '')
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '')

# Auto Features
AUTO_ACCEPT = os.getenv('AKULAKU_AUTO_ACCEPT', 'false').lower() == 'true'
AUTO_REPLY = os.getenv('AKULAKU_AUTO_REPLY', 'false').lower() == 'true'
AUTO_PROMO = os.getenv('AKULAKU_AUTO_PROMO', 'false').lower() == 'true'

# Polling
POLL_INTERVAL = int(os.getenv('AKULAKU_POLL_INTERVAL', '60'))

# Rate Limiting
REQUEST_DELAY = float(os.getenv('AKULAKU_REQUEST_DELAY', '1.0'))

# Paths
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATES_DIR = os.path.join(BASE_DIR, 'templates')
DATA_DIR = os.path.join(BASE_DIR, 'data')
LOGS_DIR = os.path.join(BASE_DIR, 'logs')

# Create directories if not exist
for dir_path in [DATA_DIR, LOGS_DIR]:
    os.makedirs(dir_path, exist_ok=True)
