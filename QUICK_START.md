# 🚀 Quick Start Guide - Smart Inventory Dashboard

## What You Have

✅ **Fully deployed inventory management system**
- Backend API running on Render
- Frontend dashboard ready to deploy
- Boltic workflow integration ready
- Modern, responsive UI with analytics

---

## 🎯 In 3 Steps

### Step 1: Deploy Frontend (2 minutes)
1. Go to https://dashboard.render.com
2. Find **`inventory-dashboard`** service
3. Click **Settings** → **Environment**
4. Ensure `REACT_APP_API_URL` = `https://smart-inventory-4ubc.onrender.com`
5. Click **Manual Deploy**
6. Wait for "Deploy successful" ✅

### Step 2: Verify It Works (1 minute)
1. Click your dashboard URL (e.g., `https://inventory-dashboard-xxx.onrender.com`)
2. Should see table with inventory data
3. Click **Refresh** button → should update timestamp
4. Try a filter (Store dropdown) → should filter data

### Step 3: Connect Boltic (1 minute)
1. Go to your Boltic workflow
2. Add HTTP POST request node with:
   - **URL**: `https://smart-inventory-4ubc.onrender.com/ingest`
   - **Method**: POST
   - **Body** (JSON):
   ```json
   {
     "predictions": [
       {
         "sku_id": "ITEM_001",
         "store_id": "STORE_1",
         "current_stock": 50,
         "avg_daily_sales": 2.0,
         "days_to_stockout": 25,
         "status": "Safe",
         "recommended_reorder_quantity": 30,
         "category": "Electronics",
         "city": "Mumbai"
       }
     ]
   }
   ```
3. Test the workflow → data should appear on dashboard

**Total time: ~5 minutes** ⏱️

---

## 📊 Dashboard Features

### Filters
- **Store**: Filter by location
- **Category**: Filter by product type
- **Search**: Find SKUs (type SKU name)
- **Critical Only**: Quick filter for urgent items

### Actions
- 🔄 **Refresh**: Fetch latest data
- ⬇️ **Export**: Download CSV
- 🌙 **Dark Mode**: Toggle (saved)
- ℹ️ **Info**: Learn how predictions work

### Views
- **Summary Cards**: Count of Critical/Warning/Safe items
- **Sortable Table**: Click column headers to sort
- **Top Critical**: Quick list on right sidebar
- **Critical by Store**: Bar chart showing distribution

---

## 🔧 Local Testing (Optional)

Want to test locally before deploying to Render?

### Start Backend
```bash
cd inventory-backend
python -m venv venv
venv\Scripts\activate  # Windows: venv\Scripts\activate.bat
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
→ API at `http://localhost:8000`

### Start Frontend
```bash
cd inventory-dashboard
npm install
REACT_APP_API_URL=http://localhost:8000 npm start
```
→ Dashboard at `http://localhost:3000`

---

## 📚 Documentation

| Doc | For | Read if... |
|-----|-----|-----------|
| `RENDER_DEPLOYMENT.md` | Render setup | You need deployment steps |
| `ENHANCEMENT_README.md` | Dashboard features | You want to understand features |
| `ACCEPTANCE_CRITERIA.md` | Testing | You want a checklist |
| `PROJECT_COMPLETION_SUMMARY.md` | Overview | You want full project status |

---

## ✅ Quick Checklist

- [ ] Frontend deployed on Render
- [ ] Dashboard loads without errors
- [ ] Table shows data
- [ ] Filters work
- [ ] Export CSV works
- [ ] Dark mode toggle works
- [ ] Boltic webhook URL configured
- [ ] Boltic test run successful

---

## 🆘 Troubleshooting

### Dashboard shows "Failed to fetch data"
```
→ Check: Is REACT_APP_API_URL set to correct backend URL?
→ Fix: Go to Render → Settings → Environment → verify URL
```

### No data in table
```
→ Check: Did Boltic send data to /ingest yet?
→ Fix: Check backend logs in Render dashboard
```

### Export CSV is empty
```
→ Check: Are filters too restrictive?
→ Fix: Set Store to "ALL" and Category to "ALL"
```

### Dark mode doesn't save
```
→ Check: Is localStorage enabled?
→ Fix: Hard refresh (Ctrl+Shift+R)
```

---

## 📞 Support

**Backend Logs**: https://dashboard.render.com → Smart-Inventory-Backend → Logs
**Frontend Logs**: Browser DevTools (F12) → Console

**API Docs**: `https://smart-inventory-4ubc.onrender.com/docs`

**Health Check**: `https://smart-inventory-4ubc.onrender.com/health`

---

## 🎉 That's it!

You have a **production-ready inventory dashboard** that:
- ✅ Integrates with Boltic
- ✅ Shows real-time inventory status
- ✅ Alerts on critical stock levels
- ✅ Works on mobile/tablet/desktop
- ✅ Exports data to CSV

**Happy inventory management!** 📦

---

*For detailed info, see other README files in the project.*
