# 🚀 Deploy ParkMyCar API to Render

Complete guide to deploy your Dockerized FastAPI backend to Render with Aiven PostgreSQL.

---

## ✅ Pre-Deployment Checklist

Your app is **already Render-ready**! ✓

- ✅ **Dockerfile configured** - Uses `PORT` env variable
- ✅ **Listens on 0.0.0.0** - Ready for cloud deployment
- ✅ **Aiven PostgreSQL** - Database already in cloud
- ✅ **Health checks** - `/health` endpoint active
- ✅ **No localhost references** - Uses environment variables

---

## 🔐 1. Get Your Aiven Database Details

From your Aiven Console → PostgreSQL service → **Connection Information**:

```
Host: pg-2e6a6e28-vijayfinforz-082a.h.aivencloud.com
Port: 23732
Database: defaultdb
User: avnadmin
Password: AVNS_5YJdZbRWiC3tQvycUB5
```

**Your DATABASE_URL:**
```
postgresql://avnadmin:AVNS_5YJdZbRWiC3tQvycUB5@pg-2e6a6e28-vijayfinforz-082a.h.aivencloud.com:23732/defaultdb?sslmode=require
```

⚠️ **NEVER commit this to Git!**

---

## 📂 2. Push to GitHub

If you haven't already:

```bash
# Initialize git (if needed)
git init

# Create .gitignore (important!)
echo ".env
.env.*
__pycache__
*.pyc
.venv
reflex.db
.web
.states" > .gitignore

# Add all files
git add .

# Commit
git commit -m "Ready for Render deployment"

# Create GitHub repo and push
git remote add origin https://github.com/YOUR_USERNAME/parking-app.git
git branch -M main
git push -u origin main
```

---

## 🌐 3. Deploy on Render

### **Step 1: Create New Web Service**

1. Go to [Render Dashboard](https://dashboard.render.com/)
2. Click **"New +"** → **"Web Service"**
3. Connect your GitHub repository
4. Select your `parking-app` repository

---

### **Step 2: Configure Service**

#### **Basic Settings:**

| Field | Value |
|-------|-------|
| **Name** | `parkmycar-api` |
| **Region** | `Singapore` (closest to Aiven) |
| **Branch** | `main` |
| **Root Directory** | Leave empty |
| **Environment** | **Docker** |

---

#### **Docker Settings:**

| Setting | Value |
|---------|-------|
| **Dockerfile Path** | `Dockerfile.api` |
| **Docker Build Context Directory** | `.` (root) |
| **Instance Type** | Free (or Starter for better performance) |

---

### **Step 3: Environment Variables (CRITICAL!)**

Click **"Advanced"** → **"Add Environment Variable"**

Add these **exact variables**:

```env
# Database (REQUIRED)
DATABASE_URL=postgresql://avnadmin:AVNS_5YJdZbRWiC3tQvycUB5@pg-2e6a6e28-vijayfinforz-082a.h.aivencloud.com:23732/defaultdb?sslmode=require

# Render Port (Auto-configured)
PORT=8000

# App Settings
APP_ENV=production
SECRET_KEY=your-super-secret-random-key-change-this-in-production

# Email (Gmail or SES)
EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=parkingapp65@gmail.com
GMAIL_APP_PASSWORD=lfvgmpdkwdlwzhyw

# Alternative: AWS SES
# EMAIL_PROVIDER=ses
# AWS_REGION=us-east-1
# AWS_ACCESS_KEY_ID=your-key
# AWS_SECRET_ACCESS_KEY=your-secret
# SES_SENDER_EMAIL=noreply@yourdomain.com

# CORS (Optional - for custom frontend)
FRONTEND_URL=https://your-frontend-domain.com

# API Settings (Optional)
API_HOST=0.0.0.0
API_PORT=8000
```

**Important Notes:**
- ✅ Use your **actual Aiven DATABASE_URL** from step 1
- ✅ Generate a **strong SECRET_KEY** (use a password generator)
- ✅ Port is auto-assigned by Render, but setting PORT=8000 is fine
- ⚠️ **Never share these values publicly!**

---

### **Step 4: Health Check (Optional but Recommended)**

| Setting | Value |
|---------|-------|
| **Health Check Path** | `/health` |
| **Health Check Interval** | 30 seconds |

---

### **Step 5: Deploy!**

1. Review all settings
2. Click **"Create Web Service"**
3. Render will:
   - Clone your repo
   - Build Docker image (takes 3-5 minutes)
   - Start container
   - Run health checks
   - Assign public URL

---

## 📊 4. Monitor Deployment

### **Watch Build Logs:**

In Render dashboard, you'll see:

```
==> Cloning from GitHub...
==> Building Docker image...
==> Building...
==> Successfully built image
==> Starting service...
INFO:     Started server process
INFO:     Waiting for application startup
✅ Database initialized
✅ Background scheduler started
INFO:     Application startup complete
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### **Deployment Status:**

- **Building** → Image is being created
- **Live** → ✅ Deployment successful!
- **Deploy failed** → Check logs for errors

---

## 🧪 5. Test Your API

Your API will be available at:
```
https://parkmycar-api.onrender.com
```

### **Test Endpoints:**

```bash
# Health check
curl https://parkmycar-api.onrender.com/health

# API docs
https://parkmycar-api.onrender.com/api/docs

# Test parking lots
curl https://parkmycar-api.onrender.com/api/parking-lots

# Test bookings
curl https://parkmycar-api.onrender.com/api/bookings?user_email=test@example.com
```

---

## ✅ 6. Verify Database Connection

Check logs for:

```
✅ Database initialized
🤖 Auto-booking Scheduler started (every 10 minutes)
📅 Notification Scheduler started (every 5 minutes)
```

This confirms:
- ✅ Connected to Aiven PostgreSQL
- ✅ Database tables created
- ✅ Background schedulers running

---

## 🔄 7. Auto-Deploy (Recommended)

Enable automatic deployments:

1. Go to **Settings** → **Build & Deploy**
2. Enable **"Auto-Deploy"**
3. Select branch: `main`

Now every push to `main` triggers deployment!

```bash
# Future updates:
git add .
git commit -m "Update API"
git push

# Render automatically:
# 1. Detects push
# 2. Rebuilds Docker image
# 3. Deploys new version
# 4. Zero downtime!
```

---

## 🛡️ 8. Security Best Practices

### **Environment Variables:**
- ✅ Store all secrets in Render environment variables
- ✅ Never commit `.env` files
- ✅ Use strong SECRET_KEY
- ✅ Enable SSL on Aiven (already done with `sslmode=require`)

### **CORS:**
```python
# In your .env or Render env vars:
FRONTEND_URL=https://your-actual-frontend.com

# Not: FRONTEND_URL=*
```

### **Firewall (Optional):**
Aiven allows all IPs by default. To restrict:
1. Go to Aiven Console → Security
2. Add Render's outbound IPs
3. Or whitelist your app's domain

---

## 📈 9. Monitoring & Logs

### **View Logs:**
- Render Dashboard → Your Service → **Logs** tab
- Real-time streaming
- Filter by level (INFO, ERROR, etc.)

### **Metrics:**
-Render Dashboard → **Metrics** tab
- CPU usage
- Memory usage
- Request count
- Response times

### **Health Checks:**
- Automatic every 30 seconds
- If fails 3 times → restart container
- Email notifications available

---

## 🚨 10. Troubleshooting

### **❌ Build Fails:**

**Error:** `Missing requirements.txt`
```bash
# Ensure requirements.txt is in root directory
ls requirements.txt
git add requirements.txt
git commit -m "Add requirements"
git push
```

**Error:** `Docker build failed`
```bash
# Test locally first:
docker build -f Dockerfile.api -t test-api .
docker run -p 8000:8000 --env-file .env test-api
```

---

### **❌ Database Connection Timeout:**

**Check:**
1. DATABASE_URL is correct in Render env vars
2. Includes `?sslmode=require`
3. Password has no special characters needing encoding

**Fix:**
```env
# If password has special chars:
postgresql://user:p%40ssw%24rd@host:port/db

# URL encode: @ → %40, $ → %24, etc.
```

---

### **❌ App Crashes on Startup:**

**Check Logs for:**
```
ERROR: Database connection failed
ERROR: Missing environment variable
ERROR: Port already in use
```

**Common fixes:**
- Add missing env vars in Render
- Verify Aiven DB is running
- Check SECRET_KEY is set

---

### **❌ Health Check Failing:**

**Symptoms:**
- Container keeps restarting
- Status shows "Unhealthy"

**Fix:**
```bash
# Test health endpoint locally:
curl http://localhost:8000/health

# Should return:
{"status":"healthy","service":"ParkMyCar API","version":"1.0.0"}

# If fails locally, check:
# 1. Health endpoint exists
# 2. App starts successfully
# 3. No import errors
```

---

## 🎯 11. Production Checklist

Before going live:

- [ ] ✅ Strong SECRET_KEY generated
- [ ] ✅ DATABASE_URL verified
- [ ] ✅ Email provider configured (Gmail or SES)
- [ ] ✅ CORS restricted to your frontend domain
- [ ] ✅ Health checks passing
- [ ] ✅ Auto-deploy enabled
- [ ] ✅ Metrics/monitoring active
- [ ] ✅ Test all API endpoints
- [ ] ✅ Verify background schedulers work
- [ ] ✅ Database backups enabled (Aiven auto-backups)

---

## 🌐 12. Custom Domain (Optional)

### **Add Custom Domain:**

1. Buy domain (e.g., on Namecheap)
2. In Render: Settings → Custom Domains
3. Add: `api.yourdomain.com`
4. Configure DNS:
   ```
   Type: CNAME
   Name: api
   Value: parkmycar-api.onrender.com
   ```
5. SSL auto-configured!

**Result:**
```
https://api.yourdomain.com
```

---

## 🎉 13. You're Live!

### **Your API is now:**

✅ **Deployed** on Render  
✅ **Connected** to Aiven PostgreSQL  
✅ **Auto-deploying** on every push  
✅ **Monitored** with health checks  
✅ **Secured** with HTTPS  
✅ **Scalable** (upgrade plan as needed)  
✅ **Running** 24/7 in production  

### **Access Points:**

- **API Base:** https://parkmycar-api.onrender.com
- **API Docs:** https://parkmycar-api.onrender.com/api/docs
- **Health:** https://parkmycar-api.onrender.com/health
- **Dashboard:** https://dashboard.render.com

---

## 📚 14. Next Steps

1. **Test thoroughly** - Use Swagger UI
2. **Connect frontend** - Point to your Render URL
3. **Monitor logs** - Watch for errors
4. **Plan scaling** - Upgrade if needed
5. **Set up alerts** - Email notifications
6. **Document API** - Share docs link

---

## 💡 Quick Reference

### **Render Dashboard:**
https://dashboard.render.com

### **Deployment Commands:**
```bash
# Update and deploy:
git add .
git commit -m "Update"
git push  # Auto-deploys!

# Manual redeploy:
# Dashboard → Manual Deploy → Deploy latest commit
```

### **Environment Variables:**
```bash
# Update in Render:
# Dashboard → Environment → Add/Edit
# Changes trigger rebuild
```

### **View Logs:**
```bash
# In Render dashboard or via API:
curl https://api.render.com/v1/services/YOUR_SERVICE_ID/logs
```

---

## 🎊 Success!

Your **ParkMyCar API** is now deployed to production!

**Architecture:**
```
Users/Apps
    ↓ HTTPS
Render (Docker)
    ↓ SSL
Aiven PostgreSQL
```

**Features:**
- ✅ Auto-scaling
- ✅ Auto-SSL
- ✅ Auto-backups (Aiven)
- ✅ Auto-deploy
- ✅ Health monitoring
- ✅ Background jobs running

**Happy deploying! 🚀**

---

**Need help?**
- Render Docs: https://render.com/docs
- Aiven Docs: https://aiven.io/docs
- Check logs in Render dashboard
