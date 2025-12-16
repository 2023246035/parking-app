# 🚀 Deploy Full ParkMyCar Application to Render

Complete guide to deploy your **Reflex application with UI** to Render.

---

## ✅ **What You'll Deploy**

- ✅ Reflex Frontend (UI)
- ✅ FastAPI Backend (API)
- ✅ Database Connection (Aiven PostgreSQL)
- ✅ Background Schedulers (Auto-booking, Reminders)

---

## 📋 **Prerequisites**

- ✅ Render account
- ✅ GitHub repository
- ✅ Aiven PostgreSQL database
- ✅ Code pushed to GitHub

---

## 🚀 **Deployment Steps**

### **Step 1: Push Code to GitHub**

```bash
git add Dockerfile
git commit -m "Add full Reflex app Dockerfile"
git push origin feature
```

---

### **Step 2: Create New Web Service on Render**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select `parking-app`

---

### **Step 3: Configure Service**

#### **Basic Settings:**

| Field | Value |
|-------|-------|
| **Name** | `parkmycar-app-full` |
| **Region** | Singapore |
| **Branch** | `feature` |
| **Environment** | **Docker** |

#### **Docker Settings:**

| Setting | Value |
|---------|-------|
| **Dockerfile Path** | `Dockerfile` |
| **Docker Build Context** | `.` |

---

### **Step 4: Environment Variables**

Add these in **Advanced** → **Environment**:

```env
# Database
DATABASE_URL=postgresql://avnadmin:YOUR_AIVEN_PASSWORD_HERE@pg-2e6a6e28-vijayfinforz-082a.h.aivencloud.com:23732/defaultdb?sslmode=require

# Ports
PORT=8000
FRONTEND_PORT=3000

# App Settings
APP_ENV=production
SECRET_KEY=your-super-secret-random-key

# Email (Gmail)
EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=parkingapp65@gmail.com
GMAIL_APP_PASSWORD=lfvgmpdkwdlwzhyw

# Or AWS SES
# EMAIL_PROVIDER=ses
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# SES_SENDER_EMAIL=noreply@parkmycar.com

# API Settings
API_HOST=0.0.0.0
API_PORT=8000

# Reflex Settings
REFLEX_BACKEND_ONLY=false
```

---

### **Step 5: Advanced Settings**

#### **Health Check:**
```
Path: /
Interval: 30 seconds
```

#### **Instance Type:**
- **Free** (for testing)
- **Starter $7/month** (recommended for production)

---

## ⚠️ **Important Notes**

### **1. Port Configuration**

Render assigns a dynamic PORT. Reflex needs to:
- Backend: Use `$PORT` (Render's assigned port)
- Frontend: Internal (accessed via Render proxy)

### **2. Build Time**

Full app build takes longer:
- Installing Node.js: ~2 min
- Installing Python packages: ~2 min
- Building Reflex frontend: ~3 min
- **Total: ~7-10 minutes**

### **3. Memory Requirements**

Full app needs more RAM:
- **Minimum:** 1GB RAM
- **Recommended:** 2GB RAM (Starter plan or higher)

---

## 🎯 **After Deployment**

Your app will be available at:
```
https://parkmycar-app-full.onrender.com
```

### **Access Points:**

| Service | URL |
|---------|-----|
| **Frontend (UI)** | https://parkmycar-app-full.onrender.com |
| **API Docs** | https://parkmycar-app-full.onrender.com/api/docs |
| **Health** | https://parkmycar-app-full.onrender.com/health |

---

## 🔧 **Alternative: Two Separate Services**

### **Option A: Single Service (Current Plan)**
- ✅ Simpler setup
- ✅ One deployment
- ⚠️ Higher resource usage

### **Option B: Separate Frontend + Backend**

Deploy two services:

1. **Backend (API)** - Already deployed! ✅
   - https://parkmycar-api.onrender.com

2. **Frontend (Static Site)**
   - Build Reflex frontend locally
   - Deploy to Render Static Site
   - Point to API URL

---

## 📊 **Recommended Approach**

Since your **API is already deployed** and working:

### **Keep API Separate + Deploy Frontend**

1. ✅ **API:** `parkmycar-api.onrender.com` (already live)
2. 🆕 **Frontend:** Deploy Reflex UI separately

**Benefits:**
- ✅ API scales independently
- ✅ Frontend scales independently
- ✅ Lower costs (separate free tiers)
- ✅ Easier debugging

---

## 🎨 **Frontend-Only Deployment Option**

If you want to keep the API separate and deploy just the UI:

### **1. Build Frontend Locally:**
```bash
reflex export
```

### **2. Deploy to Render Static Site:**
- Service Type: **Static Site**
- Build Command: `reflex export`
- Publish Directory: `.web/_static`

### **3. Configure API URL:**
```env
# In frontend .env
NEXT_PUBLIC_API_URL=https://parkmycar-api.onrender.com
```

---

## 💡 **What Would You Like?**

### **Option 1: Deploy Full App (All-in-One)**
- Single service with UI + API
- Simpler but more resources
- Use the `Dockerfile` we just created

### **Option 2: Keep API Separate, Deploy UI Only**
- Frontend connects to existing API
- More scalable
- Lower costs

### **Option 3: Keep Current Setup**
- API-only (already working)
- Access via Swagger UI
- No separate frontend deployment

---

## 🚀 **Quick Start (Option 1)**

```bash
# 1. Push Dockerfile
git add Dockerfile
git commit -m "Add full app Dockerfile"
git push origin feature

# 2. Create new Render service:
# - Name: parkmycar-app-full
# - Environment: Docker
# - Dockerfile: Dockerfile
# - Add all environment variables

# 3. Deploy!
```

---

## 📞 **Need Help?**

Let me know which option you prefer:
1. Full app (UI + API in one service)
2. Separate frontend deployment
3. Keep current API-only setup

I'll guide you through the specific steps!
