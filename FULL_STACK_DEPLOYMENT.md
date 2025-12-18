
# 🚀 Host Full ParkMyCar App on Render (Free Tier)

This guide explains how to deploy the **Full Application** (Frontend + Backend) to Render using your existing **Aiven PostgreSQL** database.

---

## 📋 1. Prerequisites

1.  **GitHub Repo**: Ensure your code is pushed to GitHub.
2.  **Aiven Database**: You have your `DATABASE_URL` from Aiven.
    *   Format: `postgresql://user:password@host:port/defaultdb?sslmode=require`

---

## 🛠️ 2. Configure Render Web Service

We will deploy a single Docker container that runs both the specific Reflex frontend and the FastAPI backend.

### **Step 2.1: Create Service**
1.  Log in to [Render Dashboard](https://dashboard.render.com/).
2.  Click **New +** → **Web Service**.
3.  Connect your GitHub repository (`parking-app`).

### **Step 2.2: Settings**
Fill in the details as follows:

| Field | Value |
|-------|-------|
| **Name** | `parkmycar-full` (or any name) |
| **Region** | `Singapore` (Closest to you/Aiven) |
| **Branch** | `main` |
| **Runtime** | **Docker** |
| **Build Context** | `.` (current directory) |
| **Dockerfile Path** | `Dockerfile` (⚠️ NOT `Dockerfile.api`) |
| **Instance Type** | **Free** |

---

## 🔑 3. Environment Variables

Click **"Advanced"** → **"Add Environment Variable"**. Add these exact variables:

| Variable | Value | Description |
|----------|-------|-------------|
| `DATABASE_URL` | `postgresql://...` | **Required.** Your Aiven connection string. |
| `PORT` | `3000` | **Crucial.** Tells Render to route traffic to the Frontend. |
| `API_URL` | `https://parkmycar-full.onrender.com` | **Required.** usage: `https://<your-app-name>.onrender.com`. Points frontend to backend. |
| `REFLEX_ENV` | `prod` | Sets Reflex to production mode. |

**Optional but Recommended:**
| Variable | Value | Description |
|----------|-------|-------------|
| `SECRET_KEY` | `(random string)` | Security key for sessions. |
| `GMAIL_SENDER_EMAIL` | `...` | For sending notifications. |
| `GMAIL_APP_PASSWORD` | `...` | App password for Gmail. |

---

## 🚀 4. Memory Optimization (Done for you!)
We have updated the `Dockerfile` to use a **Multi-Stage Build**.
1.  **Stage 1 (Builder)**: Compiles the frontend and installs dependencies. This uses the build server's resources, not the runtime memory.
2.  **Stage 2 (Runner)**: Only runs the final lightweight application.

This ensures your app runs smoothly within Render's **512 MB Free Tier** limit. You don't need to do anything extra!

---

## 🧪 5. Verification

Once "Live":
1.  **Visit URL**: `https://parkmycar-full.onrender.com`
2.  **Check Logs**:
    *   You should see `Reflex app running in production mode`.
    *   "Database initialized".
    *   "Background scheduler started".

---

## 🔄 Updating
*   Just **git push** to main. Render will automatically rebuild and redeploy.
