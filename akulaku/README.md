# 🚀 Akulaku Dropship Automation

Complete automation toolkit for Akulaku dropshippers in Indonesia.

## Features

### Core Automation
- **Bulk Product Uploader** - Upload ratusan produk dari CSV
- **Order Monitor** - Real-time order notifications + auto-accept
- **Price & Stock Syncer** - Sync dari supplier
- **Auto-Resi Filler** - Isi resi otomatis

### Marketing & Traffic
- **Keyword Research Tool** - Riset keyword trending, generate judul SEO
- **Auto Promo Manager** - Bikin voucher, diskon, flash sale otomatis
- **Review Booster** - Follow-up buyer, minta review
- **Kompetitor Tracker** - Pantau harga & strategi kompetitor
- **Chat Bot** - Auto-reply pertanyaan buyer
- **Analytics Dashboard** - Monitor performa toko

## Installation

```bash
# Clone repository
git clone https://github.com/lo/akulaku-dropship.git
cd akulaku-dropship

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp config/.env.example config/.env
# Edit config/.env dengan credentials lo
```

## Quick Start

### 1. Setup Credentials

Edit `config/.env`:
```bash
AKULAKU_APP_KEY=app_key_lo
AKULAKU_APP_SECRET=app_...n### 2. Upload Produk

```python
from src.akulaku_utils import setup_credentials, bulk_upload_products

setup_credentials()
results = bulk_upload_products('templates/products.csv')
```

### 3. Monitor Order

```python
from src.order_monitor import OrderMonitor

monitor = OrderMonitor()
monitor.start()
```

### 4. Riset Keyword

```python
from src.keyword_research import KeywordResearch

kr = KeywordResearch()
keywords = kr.get_trending_keywords('elektronik')
title = kr.generate_seo_title(keywords, 'iPhone 15')
```

### 5. Bikin Promo

```python
from src.promo_manager import PromoManager

pm = PromoManager()
pm.create_voucher('DISKON10', 10, min_purchase=100000)
```

### 6. Auto-Reply Chat

```python
from src.chat_bot import ChatBot

bot = ChatBot()
bot.start_auto_reply()
```

### 7. Lihat Analytics

```python
from src.analytics import Analytics

analytics = Analytics()
analytics.print_summary()
```

## Project Structure

```
akulaku-dropship/
├── README.md
├── requirements.txt
├── setup.py
├── config/
│   ├── .env.example
│   └── settings.py
├── src/
│   ├── __init__.py
│   ├── akulaku_utils.py        # Core API wrapper
│   ├── order_monitor.py        # Order monitoring
│   ├── keyword_research.py     # SEO keyword tool
│   ├── promo_manager.py        # Promo automation
│   ├── review_booster.py       # Review follow-up
│   ├── kompetitor_tracker.py   # Price monitoring
│   ├── chat_bot.py             # Auto-reply chat
│   └── analytics.py            # Sales analytics
├── templates/
│   ├── products.csv
│   ├── promo.csv
│   └── chat_templates.json
├── docs/
│   ├── API.md
│   └── SETUP.md
└── tests/
    └── test_utils.py
```

## CLI Commands

```bash
# Upload produk
python -m src.cli upload products.csv

# Monitor order
python -m src.cli monitor

# Riset keyword
python -m src.cli keyword "iphone 15"

# Bikin promo
python -m src.cli promo create --code DISKON10 --discount 10

# Start chat bot
python -m src.cli chatbot

# Lihat analytics
python -m src.cli analytics
```

## Environment Variables

```bash
# Required
AKULAKU_APP_KEY=your_app_key
AKULAKU_APP_SECRET=your_a...n
# Telegram Notifications
AKULAKU_NOTIFICATION_TELEGRAM=true
AKULAKU_TELEGRAM_CHAT_ID=your_chat_id
TELEGRAM_BOT_TOKEN=your_b...n
# Auto Features
AKULAKU_AUTO_ACCEPT=true
AKULAKU_AUTO_REPLY=true

# Polling
AKULAKU_POLL_INTERVAL=60
```

## Documentation

- [API Documentation](docs/API.md)
- [Setup Guide](docs/SETUP.md)

## Contributing

1. Fork repository
2. Create feature branch
3. Commit changes
4. Push to branch
5. Create Pull Request

## License

MIT License

## Support

- Developer Portal: https://developer.akulaku.com
- Issues: https://github.com/lo/akulaku-dropship/issues
