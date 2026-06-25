# 🤖 INSTRUCTIONS FOR HERMES AGENT

## Baca File Ini Pertama!

Kamu adalah developer yang ditugaskan membangun web app untuk Akulaku Dropship Automation.

**LANGKAH PERTAMA:**
1. Baca `PLAN.md` untuk roadmap lengkap
2. Baca `SUMMARY.md` untuk daftar file yang sudah ada
3. Baca `README.md` untuk dokumentasi

**TUGAS KAMU:**
Bangun web app lengkap berdasarkan `PLAN.md` dengan semua scripts yang sudah ada di folder `src/`.

---

## Yang Sudah Ada (JANGAN ULANG!)

Scripts Python di `src/` sudah siap pakai:
- `akulaku_utils.py` - Core API wrapper (authentication, semua endpoint)
- `order_monitor.py` - Monitor order real-time
- `keyword_research.py` - Riset keyword SEO
- `promo_manager.py` - Promo & voucher automation
- `review_booster.py` - Follow-up buyer
- `kompetitor_tracker.py` - Pantau harga kompetitor
- `chat_bot.py` - Auto-reply chat
- `analytics.py` - Dashboard analytics

**Tugas kamu:** BUNGKUS scripts ini ke dalam web app (FastAPI backend + HTML frontend).

---

## Step-by-Step yang Harus Dilakukan

### STEP 1: Setup Project (5 menit)
```bash
# Install dependencies
pip install fastapi uvicorn python-dotenv requests sqlalchemy python-multipart jinja2 httpx apscheduler

# Copy environment
cp config/.env.example config/.env
```

### STEP 2: Buat Backend API (30 menit)

Buat file `api/main.py`:
```python
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import uvicorn

app = FastAPI(title="Akulaku Dropship Dashboard")

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Import routes
from api.routes import products, orders, analytics, promos, settings

app.include_router(products.router)
app.include_router(orders.router)
app.include_router(analytics.router)
app.include_router(promos.router)
app.include_router(settings.router)

@app.get("/")
async def root():
    return FileResponse("frontend/index.html")

@app.get("/api/health")
async def health():
    return {"status": "ok", "app": "Akulaku Dropship Dashboard"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

Buat folder `api/routes/` dengan files:
- `products.py` → wrap `src/akulaku_utils.py` (list_products, create_product, update_stock, update_price)
- `orders.py` → wrap `src/order_monitor.py` (list_orders, accept_order, update_tracking)
- `analytics.py` → wrap `src/analytics.py` (dashboard data, charts)
- `promos.py` → wrap `src/promo_manager.py` (create_voucher, list_promos)
- `settings.py` → CRUD settings (API keys, notifications)

### STEP 3: Buat Frontend Dashboard (1 jam)

Buat folder `frontend/` dengan files:

**index.html** - Dashboard utama:
- 4 kotak stats (Orders, Revenue, Conversion, Rating)
- Revenue chart (Chart.js)
- Top products list
- Recent orders table
- Auto-refresh setiap 30 detik

**products.html** - Kelola produk:
- Search & filter
- Table produk dengan edit langsung
- Button bulk upload CSV
- Toggle status active/inactive

**orders.html** - Monitor order:
- Real-time order list
- Filter by status (Pending, Shipped, Delivered)
- Button Accept/Reject
- Form update tracking number
- Notifikasi sound saat order baru

**analytics.html** - Charts & stats:
- Revenue chart (7d, 30d, 90d)
- Orders per day chart
- Conversion funnel
- Jam ramai order (heatmap)
- Produk terlaris ranking

**promos.html** - Promo manager:
- Create voucher form
- List voucher aktif
- Schedule flash sale
- Promo performance stats

**settings.html** - Pengaturan:
- Form API credentials (App Key, App Secret)
- Telegram notification settings
- Auto-accept toggle
- Chat bot template editor

### STEP 4: Styling (30 menit)

Gunakan TailwindCSS (CDN):
```html
<link href="https://cdn.jsdelivr.net/npm/tailwindcss@2.2.19/dist/tailwind.min.css" rel="stylesheet">
```

Dark theme modern:
- Background: `bg-gray-900`
- Cards: `bg-gray-800` dengan `rounded-xl shadow-lg`
- Text: `text-white`, `text-gray-400`
- Accent: `bg-blue-600` (primary), `bg-green-600` (success)

Icons pakai Lucide:
```html
<script src="https://unpkg.com/lucide@latest"></script>
```

Charts pakai Chart.js:
```html
<script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
```

### STEP 5: Real-time Features (30 menit)

**WebSocket untuk live updates:**
```python
# api/routes/websocket.py
from fastapi import WebSocket
import asyncio

@app.websocket("/ws/orders")
async def websocket_orders(websocket: WebSocket):
    await websocket.accept()
    while True:
        # Cek order baru
        new_orders = await check_new_orders()
        if new_orders:
            await websocket.send_json(new_orders)
        await asyncio.sleep(30)
```

**Background scheduler:**
```python
# api/services/scheduler.py
from apscheduler.schedulers.asyncio import AsyncIOScheduler

scheduler = AsyncIOScheduler()

@scheduler.scheduled_job('interval', seconds=30)
async def poll_orders():
    """Auto-check new orders"""
    pass

@scheduler.scheduled_job('interval', minutes=5)
async def sync_stock():
    """Sync stok dari supplier"""
    pass
```

**Telegram notifications:**
```python
# api/services/telegram.py
async def send_order_notification(order):
    message = f"🆕 ORDER BARU!\n📦 #{order['order_id']}\n💰 Rp {order['total_amount']:,.0f}"
    await send_telegram(message)
```

### STEP 6: Deploy ke Vercel (15 menit)

Buat `vercel.json`:
```json
{
  "version": 2,
  "builds": [
    { "src": "api/main.py", "use": "@vercel/python" },
    { "src": "frontend/**", "use": "@vercel/static" }
  ],
  "routes": [
    { "src": "/api/(.*)", "dest": "api/main.py" },
    { "src": "/(.*)", "dest": "frontend/$1" }
  ]
}
```

Deploy:
```bash
vercel deploy
```

---

## Checklist Sebelum Selesai

- [ ] Backend API jalan di `http://localhost:8000`
- [ ] Dashboard load dengan benar
- [ ] Semua menu bisa diakses (Products, Orders, Analytics, Promos, Settings)
- [ ] Charts menampilkan data
- [ ] Form settings bisa simpan credentials
- [ ] Order monitoring jalan (background task)
- [ ] Telegram notification terkirim
- [ ] Mobile responsive
- [ ] Deploy ke Vercel berhasil
- [ ] Production URL bisa diakses

---

## Jangan Lupa!

1. **Database**: Pakai SQLite untuk dev, PostgreSQL untuk prod
2. **Error handling**: Semua API call harus ada try-catch
3. **Loading state**: Tampilkan spinner saat data loading
4. **Empty state**: Tampilkan pesan "No data" jika kosong
5. **Mobile**: Pastikan responsive di HP
6. **Security**: Jangan expose App Secret di frontend

---

## File yang HARUS Dibuat

```
akulaku/
├── api/
│   ├── __init__.py
│   ├── main.py                 ← Entry point FastAPI
│   ├── config.py               ← Load environment
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── products.py         ← CRUD produk
│   │   ├── orders.py           ← Order management
│   │   ├── analytics.py        ← Data analytics
│   │   ├── promos.py           ← Promo/voucher
│   │   ├── settings.py         ← App settings
│   │   └── websocket.py        ← Real-time updates
│   ├── services/
│   │   ├── __init__.py
│   │   ├── akulaku_api.py      ← Wrapper src/ scripts
│   │   ├── telegram.py         ← Notifikasi
│   │   └── scheduler.py        ← Background tasks
│   └── models/
│       ├── __init__.py
│       └── database.py         ← SQLAlchemy models
├── frontend/
│   ├── index.html              ← Dashboard
│   ├── products.html           ← Kelola produk
│   ├── orders.html             ← Monitor order
│   ├── analytics.html          ← Charts
│   ├── promos.html             ← Promo manager
│   ├── settings.html           ← Pengaturan
│   ├── static/
│   │   ├── css/
│   │   │   └── style.css
│   │   └── js/
│   │       ├── app.js          ← Main logic
│   │       ├── api.js          ← API client
│   │       └── charts.js       ← Chart configs
│   └── components/
│       ├── sidebar.html
│       ├── header.html
│       └── footer.html
├── vercel.json                 ← Deploy config
├── railway.toml                ← Alternative deploy
└── .gitignore
```

---

## Contoh Prompt ke Hermes ke-2

Upload folder ini ke Hermes ke-2, lalu bilang:

```
Baca file INSTRUCTIONS.md dan PLAN.md.
Bangun web app Akulaku Dropship sesuai instruksi.
Mulai dari STEP 1 sampai selesai.
```

Atau lebih singkat:

```
Baca INSTRUCTIONS.md dan kerjakan semua step.
```

---

## Support

- FastAPI docs: https://fastapi.tiangolo.com/
- TailwindCSS: https://tailwindcss.com/
- Chart.js: https://www.chartjs.org/
- Vercel: https://vercel.com/docs

**GOOD LUCK! 🚀**
