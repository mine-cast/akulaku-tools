# 🚀 Akulaku Dropship Web App - Development Plan

## Overview
Web-based dashboard untuk monitoring dan automasi dropship Akulaku.
Deploy ke Vercel/Railway, akses dari browser/HP.

---

## PHASE 1: Foundation (Hari 1-2)

### 1.1 Project Setup
```
akulaku/
├── api/                        # Backend FastAPI
│   ├── main.py                 # Server entry point
│   ├── config.py               # Konfigurasi
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── products.py         # CRUD produk
│   │   ├── orders.py           # Order management
│   │   ├── analytics.py        # Data analytics
│   │   ├── promos.py           # Promo/voucher
│   │   └── settings.py         # App settings
│   ├── services/
│   │   ├── __init__.py
│   │   ├── akulaku_api.py      # Akulaku API wrapper
│   │   ├── telegram.py         # Notifikasi Telegram
│   │   └── scheduler.py        # Background tasks
│   └── models/
│       ├── __init__.py
│       └── database.py         # SQLite/PostgreSQL
├── frontend/                   # Dashboard UI
│   ├── index.html              # Main dashboard
│   ├── products.html           # Kelola produk
│   ├── orders.html             # Monitor order
│   ├── analytics.html          # Charts & stats
│   ├── promos.html             # Promo manager
│   ├── settings.html           # Pengaturan
│   ├── css/
│   │   └── style.css           # TailwindCSS
│   └── js/
│       ├── app.js              # Main logic
│       ├── api.js              # API client
│       ├── charts.js           # Chart.js integration
│       └── notifications.js    # Real-time notif
├── static/                     # Static assets
│   ├── images/
│   └── icons/
├── vercel.json                 # Vercel config
├── railway.toml                # Railway config (alternative)
├── requirements.txt            # Python dependencies
├── package.json                # Frontend dependencies (if needed)
└── README.md
```

### 1.2 Tech Stack
- **Backend**: FastAPI (Python 3.11+)
- **Database**: SQLite (dev) → PostgreSQL (prod)
- **Frontend**: HTML + TailwindCSS + Alpine.js (lightweight)
- **Charts**: Chart.js
- **Deploy**: Vercel (serverless) atau Railway

### 1.3 Dependencies
```txt
# requirements.txt
fastapi==0.104.1
uvicorn==0.24.0
python-dotenv==1.0.0
requests==2.31.0
sqlalchemy==2.0.23
python-jose==3.3.0
passlib==1.7.4
python-multipart==0.0.6
jinja2==3.1.2
httpx==0.25.2
apscheduler==3.10.4
```

---

## PHASE 2: Backend API (Hari 2-3)

### 2.1 Akulaku API Service
```python
# api/services/akulaku_api.py

class AkulakuAPI:
    BASE_URL = "https://open.akulaku.com/api"
    
    def __init__(self, app_key: str, app_secret: str):
        self.app_key = app_key
        self.app_secret=***    
    def _generate_sign(self, params: dict) -> str:
        # HMAC-SHA256 signature
        pass
    
    # Products
    async def list_products(self, page=1, size=50): pass
    async def get_product(self, goods_id): pass
    async def create_product(self, data): pass
    async def update_product(self, goods_id, data): pass
    async def update_stock(self, goods_id, sku_id, stock): pass
    async def update_price(self, goods_id, sku_id, price): pass
    
    # Orders
    async def list_orders(self, status=None, page=1): pass
    async def get_order(self, order_id): pass
    async def accept_order(self, order_id): pass
    async def reject_order(self, order_id): pass
    
    # Logistics
    async def update_tracking(self, order_id, tracking, courier): pass
    
    # Promos
    async def create_voucher(self, data): pass
    async def list_vouchers(self): pass
    
    # Shop
    async def get_shop_info(self): pass
```

### 2.2 API Routes
```python
# api/routes/products.py
from fastapi import APIRouter, Depends

router = APIRouter(prefix="/api/products", tags=["products"])

@router.get("/")
async def list_products(page: int = 1, search: str = None):
    """List semua produk dengan search & pagination"""
    pass

@router.post("/")
async def create_product(data: ProductCreate):
    """Upload produk baru"""
    pass

@router.post("/bulk-upload")
async def bulk_upload(file: UploadFile):
    """Upload dari CSV"""
    pass

@router.put("/{goods_id}/stock")
async def update_stock(goods_id: str, stock: int):
    """Update stok produk"""
    pass

@router.put("/{goods_id}/price")
async def update_price(goods_id: str, price: float):
    """Update harga produk"""
    pass
```

```python
# api/routes/orders.py
router = APIRouter(prefix="/api/orders", tags=["orders"])

@router.get("/")
async def list_orders(status: str = None):
    """List order dengan filter status"""
    pass

@router.get("/{order_id}")
async def get_order(order_id: str):
    """Detail order"""
    pass

@router.post("/{order_id}/accept")
async def accept_order(order_id: str):
    """Terima order"""
    pass

@router.post("/{order_id}/tracking")
async def update_tracking(order_id: str, tracking: str, courier: str):
    """Update nomor resi"""
    pass
```

```python
# api/routes/analytics.py
router = APIRouter(prefix="/api/analytics", tags=["analytics"])

@router.get("/dashboard")
async def get_dashboard():
    """Data untuk dashboard utama"""
    return {
        "today_orders": 0,
        "today_revenue": 0,
        "total_products": 0,
        "conversion_rate": 0,
        "top_products": [],
        "recent_orders": []
    }

@router.get("/charts/revenue")
async def get_revenue_chart(period: str = "7d"):
    """Data chart revenue"""
    pass

@router.get("/charts/orders")
async def get_orders_chart(period: str = "7d"):
    """Data chart orders"""
    pass
```

### 2.3 Database Models
```python
# api/models/database.py
from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()

class Product(Base):
    __tablename__ = "products"
    
    id = Column(Integer, primary_key=True)
    goods_id = Column(String, unique=True)
    name = Column(String)
    category_id = Column(String)
    price = Column(Float)
    stock = Column(Integer)
    description = Column(String)
    image_urls = Column(String)  # JSON array
    status = Column(String)  # active/inactive
    created_at = Column(DateTime)
    updated_at = Column(DateTime)

class Order(Base):
    __tablename__ = "orders"
    
    id = Column(Integer, primary_key=True)
    order_id = Column(String, unique=True)
    product_name = Column(String)
    quantity = Column(Integer)
    total_amount = Column(Float)
    status = Column(String)
    buyer_name = Column(String)
    tracking_number = Column(String)
    courier = Column(String)
    created_at = Column(DateTime)

class Promo(Base):
    __tablename__ = "promos"
    
    id = Column(Integer, primary_key=True)
    code = Column(String, unique=True)
    discount_percent = Column(Float)
    min_purchase = Column(Float)
    start_date = Column(DateTime)
    end_date = Column(DateTime)
    usage_limit = Column(Integer)
    used_count = Column(Integer)
    status = Column(String)

class Settings(Base):
    __tablename__ = "settings"
    
    id = Column(Integer, primary_key=True)
    key = Column(String, unique=True)
    value = Column(String)
```

---

## PHASE 3: Frontend Dashboard (Hari 3-5)

### 3.1 Design System
- **Framework**: TailwindCSS (CDN)
- **Icons**: Lucide Icons
- **Charts**: Chart.js
- **Interactivity**: Alpine.js (lightweight)
- **Theme**: Dark mode (modern look)

### 3.2 Pages

#### Dashboard (index.html)
```
┌─────────────────────────────────────────────────────────┐
│  🏪 Akulaku Dropship Dashboard                    [⚙️] │
├─────────────────────────────────────────────────────────┤
│                                                         │
│  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │
│  │ 📦 Orders│ │ 💰 Revenue│ │ 📈 Conv. │ │ ⭐ Rating│  │
│  │   125    │ │  Rp 15jt │ │   3.2%   │ │   4.8    │  │
│  │  +12% ↑  │ │  +8% ↑   │ │  +0.5% ↑ │ │   ─      │  │
│  └──────────┘ └──────────┘ └──────────┘ └──────────┘  │
│                                                         │
│  ┌─────────────────────────┐ ┌────────────────────────┐│
│  │ 📊 Revenue Chart (7d)   │ │ 🏆 Top Products        ││
│  │                         │ │ 1. iPhone 15 (45 sold) ││
│  │    📈                   │ │ 2. Samsung S24 (32)    ││
│  │                         │ │ 3. Airpods Pro (28)    ││
│  └─────────────────────────┘ └────────────────────────┘│
│                                                         │
│  ┌─────────────────────────────────────────────────────┐│
│  │ 📋 Recent Orders                                    ││
│  │ ┌─────────────────────────────────────────────────┐ ││
│  │ │ #ORD001 | iPhone 15 | Rp 15jt | ⏳ Pending     │ ││
│  │ │ #ORD002 | Samsung   | Rp 8jt  | ✅ Shipped     │ ││
│  │ │ #ORD003 | Airpods   | Rp 3jt  | 📦 Delivered   │ ││
│  │ └─────────────────────────────────────────────────┘ ││
│  └─────────────────────────────────────────────────────┘│
└─────────────────────────────────────────────────────────┘
```

#### Products Page (products.html)
- List produk dengan search & filter
- Button bulk upload CSV
- Edit harga/stok langsung
- Status toggle (active/inactive)

#### Orders Page (orders.html)
- Real-time order list
- Filter: Pending, Shipped, Delivered, Cancelled
- Button: Accept, Reject, Update Resi
- Auto-refresh setiap 30 detik

#### Analytics Page (analytics.html)
- Revenue chart (7d, 30d, 90d)
- Orders chart
- Conversion funnel
- Jam ramai order
- Produk terlaris

#### Promos Page (promos.html)
- Create voucher baru
- List voucher aktif
- Schedule flash sale
- Promo performance

#### Settings Page (settings.html)
- API credentials
- Telegram notification
- Auto-accept toggle
- Chat bot templates

### 3.3 Components

#### Sidebar Navigation
```html
<aside class="sidebar">
  <nav>
    <a href="/">📊 Dashboard</a>
    <a href="/products">📦 Products</a>
    <a href="/orders">🛒 Orders</a>
    <a href="/analytics">📈 Analytics</a>
    <a href="/promos">💰 Promos</a>
    <a href="/settings">⚙️ Settings</a>
  </nav>
</aside>
```

#### Notification Toast
```html
<div x-data="{ show: false, message: '' }" 
     x-show="show" 
     x-transition
     class="toast">
  <span x-text="message"></span>
</div>
```

---

## PHASE 4: Real-time Features (Hari 5-6)

### 4.1 WebSocket untuk Live Updates
```python
# api/routes/websocket.py
from fastapi import WebSocket

@router.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    """Real-time order updates"""
    await websocket.accept()
    while True:
        # Check new orders
        new_orders = await check_new_orders()
        if new_orders:
            await websocket.send_json(new_orders)
        await asyncio.sleep(30)
```

### 4.2 Background Scheduler
```python
# api/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

# Poll orders setiap 30 detik
@scheduler.scheduled_job('interval', seconds=30)
async def poll_orders():
    """Check new orders & send notifications"""
    pass

# Sync stok setiap 5 menit
@scheduler.scheduled_job('interval', minutes=5)
async def sync_stock():
    """Sync stock with supplier"""
    pass

# Daily analytics report
@scheduler.scheduled_job('cron', hour=0)
async def daily_report():
    """Generate daily analytics"""
    pass
```

### 4.3 Telegram Notifications
```python
# api/services/telegram.py
import httpx

class TelegramNotifier:
    def __init__(self, bot_token: str, chat_id: str):
        self.bot_token = bot_token
        self.chat_id = chat_id
    
    async def send_order_notification(self, order: dict):
        message = f"""
🆕 ORDER BARU!

📦 #{order['order_id']}
🛍️ {order['product_name']}
💰 Rp {order['total_amount']:,.0f}
👤 {order['buyer_name']}
        """
        await self._send(message)
    
    async def send(self, message: str):
        url = f"https://api.telegram.org/bot{self.bot_token}/sendMessage"
        async with httpx.AsyncClient() as client:
            await client.post(url, json={
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": "HTML"
            })
```

---

## PHASE 5: Deploy (Hari 6-7)

### 5.1 Vercel Config
```json
// vercel.json
{
  "version": 2,
  "builds": [
    {
      "src": "api/main.py",
      "use": "@vercel/python"
    },
    {
      "src": "frontend/**",
      "use": "@vercel/static"
    }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/main.py" },
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
```

### 5.2 Railway Config (Alternative)
```toml
# railway.toml
[build]
builder = "nixpacks"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/health"
restartPolicyType = "on_failure"
```

### 5.3 Environment Variables (Deploy)
```
AKULAKU_APP_KEY=xxx
AKULAKU_APP_SECRET=xxx
DATABASE_URL=postgresql://...
TELEGRAM_BOT_TOKEN=xxx
TELEGRAM_CHAT_ID=xxx
```

---

## PHASE 6: Testing & Launch (Hari 7)

### 6.1 Testing Checklist
- [ ] API endpoints working
- [ ] Dashboard loads correctly
- [ ] Order monitoring works
- [ ] Notifications sending
- [ ] CSV upload works
- [ ] Charts displaying data
- [ ] Mobile responsive

### 6.2 Launch Steps
1. Push ke GitHub
2. Connect ke Vercel
3. Set environment variables
4. Deploy
5. Test production
6. Share link!

---

## Timeline Summary

| Phase | Duration | Deliverable |
|-------|----------|-------------|
| 1. Foundation | Day 1-2 | Project structure, dependencies |
| 2. Backend API | Day 2-3 | All API endpoints working |
| 3. Frontend | Day 3-5 | Dashboard UI complete |
| 4. Real-time | Day 5-6 | WebSocket, notifications |
| 5. Deploy | Day 6-7 | Live on Vercel |
| 6. Launch | Day 7 | Production ready |

---

## Commands untuk Hermes ke-2

```bash
# 1. Download folder ini sebagai zip
# 2. Extract di environment baru
# 3. Jalankan:

# Install dependencies
pip install -r requirements.txt

# Setup environment
cp config/.env.example config/.env
# Edit config/.env dengan credentials

# Run development server
uvicorn api.main:app --reload --port 8000

# Buka browser
# http://localhost:8000

# Deploy ke Vercel
vercel deploy
```

---

## Notes

- Database: SQLite untuk dev, PostgreSQL untuk production
- Auth: Bisa ditambahkan nanti (JWT token)
- Scaling: Vercel auto-scale, Railway manual
- Monitoring: Sentry untuk error tracking
- Backup: Database backup otomatis di Railway

---

## Future Enhancements (v2.0)

- [ ] Multi-marketplace (Shopee, Tokopedia)
- [ ] AI-powered pricing
- [ ] Customer segmentation
- [ ] Automated supplier ordering
- [ ] Mobile app (React Native)
- [ ] Multi-user support
- [ ] Advanced analytics (ML predictions)
