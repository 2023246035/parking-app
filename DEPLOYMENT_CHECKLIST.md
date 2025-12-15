# ✅ Render Deployment - Quick Checklist

## 📝 Pre-Deployment

- [x] ✅ Dockerfile.api configured for PORT env variable
- [x] ✅ App listens on 0.0.0.0
- [x] ✅ Aiven PostgreSQL connection string ready
- [x] ✅ .gitignore created
- [ ] ⏳ Code pushed to GitHub

---

## 🔐 Environment Variables to Set in Render

Copy these to Render Dashboard → Environment:

```env
DATABASE_URL=postgresql://avnadmin:AVNS_5YJdZbRWiC3tQvycUB5@pg-2e6a6e28-vijayfinforz-082a.h.aivencloud.com:23732/defaultdb?sslmode=require

PORT=8000

APP_ENV=production

SECRET_KEY=CHANGE-THIS-TO-RANDOM-STRING

EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=parkingapp65@gmail.com
GMAIL_APP_PASSWORD=lfvgmpdkwdlwzhyw

FRONTEND_URL=https://your-frontend-domain.com
```

---

## 🚀 Deployment Steps

1. **Push to GitHub**
   ```bash
   git add .
   git commit -m "Ready for Render"
   git push origin main
   ```

2. **Create Render Service**
   - Go to https://dashboard.render.com
   - New + → Web Service
   - Connect GitHub repo
   - Select `parking-app`

3. **Configure**
   - Name: `parkmycar-api`
   - Region: `Singapore`
   - Environment: **Docker**
   - Dockerfile Path: `Dockerfile.api`
   - Build Context: `.`

4. **Add Environment Variables**
   - Copy all env vars above
   - Paste in Render → Advanced → Environment

5. **Deploy**
   - Click "Create Web Service"
   - Wait 3-5 minutes
   - Check logs for success

---

## 🧪 Post-Deployment Testing

```bash
# Replace with your actual Render URL
export API_URL=https://parkmycar-api.onrender.com

# Test health
curl $API_URL/health

# Test parking lots
curl $API_URL/api/parking-lots

# View docs
open $API_URL/api/docs
```

---

## ✅ Success Indicators

In Render logs, you should see:

```
✅ Database initialized
✅ Background scheduler started
INFO: Uvicorn running on http://0.0.0.0:8000
```

Status badge shows: **Live** 🟢

---

## 🎯 Your Deployment URLs

- **API:** https://parkmycar-api.onrender.com
- **Docs:** https://parkmycar-api.onrender.com/api/docs
- **Health:** https://parkmycar-api.onrender.com/health

---

## 📚 Full Guide

See **RENDER_DEPLOYMENT.md** for complete instructions!
