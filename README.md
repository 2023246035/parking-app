# 🚀 ParkMyCar API - Docker Deployment

Complete Docker setup for deploying the **FastAPI backend only**.

---

## ✅ What's Included

Your API deployment consists of:

| File | Purpose |
|------|---------|
| `Dockerfile.api` | API container image definition |
| `docker-compose.api.yml` | Service orchestration (API + DB) |
| `app/api/main.py` | Standalone FastAPI application |
| `.env.api` | Environment configuration template |
| `start-api.bat` | Windows quick start script |
| `start-api.sh` | Linux/Mac quick start script |
| `nginx/api-nginx.conf` | API gateway configuration (optional) |
| `init-scripts/01-init.sh` | PostgreSQL initialization |

---

## 🏗️ Architecture

```
┌─────────────────────────────────┐
│    Nginx API Gateway            │
│    (Optional)                   │
│    Port 80/443                  │
└────────────┬────────────────────┘
             │
┌────────────▼────────────────────┐
│    FastAPI Application          │
│    Port 8000                    │
│    • REST API Endpoints         │
│    • Swagger UI                 │
│    • Health Checks              │
└────────────┬────────────────────┘
             │
     ┌───────┴────────┐
     │                │
┌────▼─────┐   ┌─────▼────┐
│PostgreSQL│   │  Redis   │
│Port 5432 │   │Port 6379 │
│(Required)│   │(Optional)│
└──────────┘   └──────────┘
```

---

## 🚀 Quick Start (3 Steps)

### **Step 1: Configure Environment**

```powershell
# Windows
copy .env.api .env
notepad .env
```

```bash
# Linux/Mac
cp .env.api .env
nano .env
```

**Update these critical values:**
```env
POSTGRES_PASSWORD=your_secure_password_here
SECRET_KEY=your_random_secret_key_here
FRONTEND_URL=http://your-frontend-domain.com
```

### **Step 2: Start the API**

**Windows:**
```powershell
.\start-api.bat
```

**Linux/Mac:**
```bash
chmod +x start-api.sh
./start-api.sh
```

**Or use Docker Compose directly:**
```bash
docker-compose -f docker-compose.api.yml up -d
```

### **Step 3: Verify It's Working**

```bash
# Check health
curl http://localhost:8000/health

# Open API documentation in browser
# http://localhost:8000/api/docs
```

---

## 📍 Access Points

| Endpoint | URL | Description |
|----------|-----|-------------|
| **API Base** | http://localhost:8000 | Root endpoint |
| **Swagger UI** | http://localhost:8000/api/docs | Interactive API documentation |
| **ReDoc** | http://localhost:8000/api/redoc | Alternative documentation |
| **Health Check** | http://localhost:8000/health | Service health status |
| **OpenAPI Schema** | http://localhost:8000/api/openapi.json | API specification |
| **Database** | localhost:5432 | PostgreSQL (direct access) |

---

## 🎯 Available API Endpoints

### **Parking Lots**
- `GET /api/parking-lots` - List all parking lots
  - Query params: `?location=X&search=Y`
- `GET /api/parking-lots/{id}` - Get specific parking lot
- `PUT /api/parking-lots/{id}/availability` - Update availability

### **Bookings**
- `GET /api/bookings` - Get user bookings
  - Query params: `?user_email=X&status_filter=Y`
- `POST /api/bookings` - Create new booking
- `POST /api/bookings/{id}/cancel` - Cancel booking

### **Health & Status**
- `GET /health` - Health check endpoint
- `GET /ping` - Simple ping endpoint
- `GET /` - API information

---

## 🛠️ Common Commands

### **Service Management**

```bash
# Start API
docker-compose -f docker-compose.api.yml up -d

# Stop API
docker-compose -f docker-compose.api.yml down

# View logs (all services)
docker-compose -f docker-compose.api.yml logs -f

# View API logs only
docker-compose -f docker-compose.api.yml logs -f api

# Check status
docker-compose -f docker-compose.api.yml ps

# Restart API
docker-compose -f docker-compose.api.yml restart api

# Rebuild and restart
docker-compose -f docker-compose.api.yml up -d --build api
```

### **Database Operations**

```bash
# Access PostgreSQL shell
docker-compose -f docker-compose.api.yml exec postgres psql -U parkmycar_user -d parkmycar

# Backup database
docker-compose -f docker-compose.api.yml exec -T postgres pg_dump -U parkmycar_user parkmycar > backup.sql

# Restore database
docker-compose -f docker-compose.api.yml exec -T postgres psql -U parkmycar_user parkmycar < backup.sql

# Check database health
docker-compose -f docker-compose.api.yml exec postgres pg_isready -U parkmycar_user
```

### **Container Access**

```bash
# Access API container shell
docker-compose -f docker-compose.api.yml exec api bash

# Run Python commands
docker-compose -f docker-compose.api.yml exec api python -c "from app.db.init_db import init_db; init_db()"
```

---

## 🔧 Configuration Options

### **Basic Setup** (API + PostgreSQL)
```bash
docker-compose -f docker-compose.api.yml up -d
```

### **With Redis Caching**
```bash
docker-compose -f docker-compose.api.yml --profile cache up -d
```

### **With Nginx API Gateway** (Production)
```bash
docker-compose -f docker-compose.api.yml --profile gateway up -d
```

### **Full Setup** (All Services)
```bash
docker-compose -f docker-compose.api.yml --profile cache --profile gateway up -d
```

---

## 🌐 CORS Configuration

The API is pre-configured to accept requests from:
- `http://localhost:3000`
- `http://localhost:3001`
- `http://localhost:5173` (Vite default)
- Custom domain via `FRONTEND_URL` environment variable

**To modify CORS settings**, edit `app/api/main.py`:

```python
allow_origins=[
    "https://your-frontend.com",
    "https://www.your-frontend.com",
    os.getenv("FRONTEND_URL", "*")
]
```

---

## 🧪 Testing the API

### **Using Swagger UI** (Recommended)

1. Open browser: http://localhost:8000/api/docs
2. Explore all available endpoints
3. Test them interactively
4. View request/response schemas

### **Using curl**

```bash
# Get all parking lots
curl http://localhost:8000/api/parking-lots

# Get specific lot
curl http://localhost:8000/api/parking-lots/1

# Create booking
curl -X POST http://localhost:8000/api/bookings \
  -H "Content-Type: application/json" \
  -d '{
    "user_email": "user@example.com",
    "lot_id": 1,
    "start_date": "2025-01-01",
    "start_time": "09:00",
    "duration_hours": 2,
    "total_price": 10.00
  }'

# Check health
curl http://localhost:8000/health
```

### **Using Python requests**

```python
import requests

# Get parking lots
response = requests.get('http://localhost:8000/api/parking-lots')
print(response.json())

# Health check
response = requests.get('http://localhost:8000/health')
print(response.json())

# Create booking
booking_data = {
    "user_email": "user@example.com",
    "lot_id": 1,
    "start_date": "2025-01-01",
    "start_time": "09:00",
    "duration_hours": 2,
    "total_price": 10.00
}
response = requests.post('http://localhost:8000/api/bookings', json=booking_data)
print(response.json())
```

---

## 🔒 Security Configuration

### **Environment Variables**

Update these in `.env` before production deployment:

```env
# Database (REQUIRED)
POSTGRES_PASSWORD=strong_password_here

# Application (REQUIRED)
SECRET_KEY=random_secret_key_here

# CORS (REQUIRED for production)
FRONTEND_URL=https://your-frontend-domain.com

# Email (if using AWS SES)
EMAIL_PROVIDER=ses
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
```

### **Security Checklist**

- [ ] ✅ Change `POSTGRES_PASSWORD` to strong password
- [ ] ✅ Generate random `SECRET_KEY`
- [ ] ✅ Set specific `FRONTEND_URL` (not `*`)
- [ ] ✅ Configure AWS SES credentials
- [ ] ✅ Set `EMAIL_PROVIDER=ses` for production
- [ ] ✅ Enable HTTPS with SSL certificates (if using Nginx)
- [ ] ✅ Never commit `.env` file to version control
- [ ] ✅ Configure firewall rules
- [ ] ✅ Set up monitoring and logging

### **Rate Limiting** (via Nginx)

When using the Nginx gateway:
- General API: 60 requests/minute
- Bookings: 10 requests/minute
- Auth endpoints: 5 requests/minute

Configure in `nginx/api-nginx.conf`

---

## 📊 Monitoring & Health Checks

### **Health Check Endpoint**

```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "healthy",
  "service": "ParkMyCar API",
  "version": "1.0.0"
}
```

### **Service Status**

```bash
# Check all services
docker-compose -f docker-compose.api.yml ps

# View resource usage
docker stats parkmycar-api
docker stats parkmycar-api-db
```

### **Database Health**

```bash
docker-compose -f docker-compose.api.yml exec postgres pg_isready -U parkmycar_user
```

---

## 🚨 Troubleshooting

### **API Won't Start**

```bash
# Check logs
docker-compose -f docker-compose.api.yml logs api

# Check database logs
docker-compose -f docker-compose.api.yml logs postgres

# Restart services
docker-compose -f docker-compose.api.yml restart

# Complete reset
docker-compose -f docker-compose.api.yml down -v
docker-compose -f docker-compose.api.yml up -d --build
```

### **Database Connection Issues**

```bash
# Verify database is running
docker-compose -f docker-compose.api.yml ps postgres

# Test connection
docker-compose -f docker-compose.api.yml exec postgres pg_isready -U parkmycar_user

# View database logs
docker-compose -f docker-compose.api.yml logs postgres
```

### **Port Already in Use**

Edit `.env` file:
```env
API_PORT=8001
POSTGRES_PORT=5433
```

Then restart:
```bash
docker-compose -f docker-compose.api.yml down
docker-compose -f docker-compose.api.yml up -d
```

### **CORS Errors**

1. **Update `.env` file:**
   ```env
   FRONTEND_URL=http://your-actual-frontend.com
   ```

2. **Restart API:**
   ```bash
   docker-compose -f docker-compose.api.yml restart api
   ```

---

## 📈 Scaling the API

### **Horizontal Scaling**

```bash
# Run multiple API instances
docker-compose -f docker-compose.api.yml up -d --scale api=3

# With Nginx (automatic load balancing)
docker-compose -f docker-compose.api.yml --profile gateway up -d --scale api=3
```

### **Adding Redis for Caching**

```bash
# Start with Redis
docker-compose -f docker-compose.api.yml --profile cache up -d
```

Implement caching in your code:
```python
import redis
r = redis.Redis(host='redis', port=6379, decode_responses=True)

# Cache example
cached_data = r.get('parking_lots')
if not cached_data:
    # Fetch from database
    r.setex('parking_lots', 300, json.dumps(data))  # Cache for 5 minutes
```

---

## 🔄 Development vs Production

### **Development Mode**

Uncomment in `docker-compose.api.yml`:
```yaml
volumes:
  - ./app:/app/app  # Live code reloading
```

Then:
```bash
docker-compose -f docker-compose.api.yml up -d
```

### **Production Mode**

```bash
# Set production environment
APP_ENV=production docker-compose -f docker-compose.api.yml --profile gateway up -d
```

---

## 📚 Documentation

- **Swagger UI:** http://localhost:8000/api/docs (Interactive)
- **ReDoc:** http://localhost:8000/api/redoc (Clean documentation)
- **OpenAPI Schema:** http://localhost:8000/api/openapi.json

---

## 🎯 Next Steps

1. ✅ **Test locally** - Start with `.\start-api.bat`
2. ✅ **Explore API** - Visit http://localhost:8000/api/docs
3. ✅ **Configure CORS** - Update `FRONTEND_URL` in `.env`
4. ✅ **Connect frontend** - Point your frontend to http://localhost:8000
5. ✅ **Production setup** - Follow security checklist
6. ✅ **Set up monitoring** - Configure logging and alerts
7. ✅ **Automated backups** - Schedule database backups
8. ✅ **Enable HTTPS** - Configure SSL certificates (if using Nginx)

---

## 🎉 Success!

Your **ParkMyCar API** is now containerized and ready to deploy!

**Quick Start:**
```powershell
.\start-api.bat
```

**Access:**
- 📖 **API Docs:** http://localhost:8000/api/docs
- ❤️ **Health:** http://localhost:8000/health

---

**Happy API Development! 🚀**

*For issues, check the troubleshooting section above or review Docker logs.*
