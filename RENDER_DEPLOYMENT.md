# Smart Inventory - Render Deployment Guide

## ✅ What Has Been Done

The following files have been created/updated to prepare your project for Render deployment:

1. **`.gitignore`** - Configured to exclude node_modules, build artifacts, and cache files
2. **`render.yaml`** - Multi-service configuration for backend API and frontend dashboard
3. **`Procfile`** - Defines how to start the backend service
4. **`build.sh`** - Build script for the React frontend
5. **`main.py` updated** - Added health check endpoint and CORS configuration for production
6. **`.git` initialized** - Repository ready for deployment

---

## 📋 Step-by-Step Deployment Instructions

### **Step 1: Push to GitHub (Required)**

1. Create a new GitHub repository
2. Add GitHub as remote and push your code:
   ```bash
   git remote add origin https://github.com/YOUR_USERNAME/smart-inventory.git
   git branch -M main
   git push -u origin main
   ```

### **Step 2: Create Render Account & Blueprint**

1. Go to [https://render.com](https://render.com) and sign up/log in
2. Click **"New +"** → **"Blueprint"**
3. Connect your GitHub account and select your `smart-inventory` repository
4. Click **"Connect"**

### **Step 3: Deploy from Blueprint**

1. Render will auto-detect `render.yaml`
2. Click **"Create New Blueprint"**
3. Review the configuration:
   - **Backend Service**: `inventory-backend` (Python 3.11)
   - **Frontend Service**: `inventory-dashboard` (Node 18)
4. Click **"Deploy"**

### **Step 4: Monitor Deployment**

- Check the **Logs** tab for both services
- Wait for both services to show **"Live"** status
- Note the URLs provided (e.g., `https://inventory-backend-xxx.onrender.com`)

### **Step 5: Configure Environment Variables (if needed)**

1. Go to each service → **Environment**
2. Add environment variables:
   - For **Backend**: `PYTHON_VERSION=3.11`
   - For **Frontend**: `REACT_APP_API_URL=https://your-backend-url.onrender.com`

### **Step 6: Update Frontend API Calls**

In your React app (e.g., `InventoryHealthPage.jsx`), update API calls to use the deployed backend:

```javascript
const API_URL = process.env.REACT_APP_API_URL || 'http://localhost:8000';

// Then use:
fetch(`${API_URL}/predict-bulk`, { ... })
```

---

## 🔄 Continuous Deployment

Once deployed:
- **Every push to `main` branch** will automatically trigger a new deployment
- Render monitors your GitHub repository for changes
- Deployments typically complete in 3-5 minutes

---

## 🧪 Test Your Deployment

Once live:

1. **Backend Health Check**:
   ```bash
   curl https://your-backend-url.onrender.com/health
   ```
   Expected response: `{"status":"healthy"}`

2. **Frontend**: Visit the dashboard URL in your browser

3. **Test API**:
   ```bash
   curl -X POST https://your-backend-url.onrender.com/predict-bulk \
     -H "Content-Type: application/json" \
     -d '{
       "items": [
         {"sku_id": "SKU001", "store_id": "STORE1", "current_stock": 100, "sales_last_30_days": 30}
       ]
     }'
   ```

---

## ⚠️ Important Notes

1. **Free Tier Limitations**:
   - Services spin down after 15 minutes of inactivity
   - Add a cron job to keep them alive (optional)

2. **Data Persistence**:
   - Current setup stores data in memory (resets on redeploy)
   - For persistent data, add a database (PostgreSQL, MongoDB, etc.)

3. **CORS Configuration**:
   - Updated to allow all origins (`"*"`) for development
   - Restrict to specific domains in production

4. **Node Submodule Warning**:
   - The `inventory-dashboard` directory appears to be a git submodule
   - Ensure it's properly initialized or remove the `.git` folder from it

---

## 🛠️ Troubleshooting

| Issue | Solution |
|-------|----------|
| Frontend can't reach backend | Check `REACT_APP_API_URL` environment variable |
| Port binding error | Render automatically assigns `$PORT` environment variable |
| Build fails | Check logs for missing dependencies in `package.json` or `requirements.txt` |
| Service won't start | Verify start command in `render.yaml` matches your directory structure |

---

## 📞 Quick Reference

- **Render Dashboard**: https://dashboard.render.com
- **Backend Endpoint**: `https://your-backend-url.onrender.com`
- **Frontend URL**: `https://your-dashboard-url.onrender.com`
- **Logs Location**: Service Dashboard → Logs tab
- **Manual Deploy**: Service Dashboard → Manual Deploy button

---

**Your project is now ready for deployment! 🚀**
