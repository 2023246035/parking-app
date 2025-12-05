# Analytics Dashboard Implementation

## 🎯 Objective
Implement an Analytics Dashboard for the Admin Portal to visualize key business metrics.

## ✅ Features Implemented

### 1. Analytics State (`app/states/analytics_state.py`)
- **Data Fetching:** Fetches data from `Booking`, `ParkingLot`, and `User` tables.
- **Bookings Chart Data:** Calculates daily bookings for the last 7 days.
- **Revenue Chart Data:** Calculates daily revenue for the last 7 days.
- **Lot Performance:** Calculates occupancy rate, total bookings, and revenue per parking lot.
- **Refund Metrics:** Calculates total refunds, total refund amount, and refund rate.

### 2. Analytics Page (`app/pages/admin_analytics.py`)
- **Charts:** Uses `recharts` to display Line Chart (Bookings) and Bar Chart (Revenue).
- **Performance Table:** Displays detailed statistics for each parking lot, sorted by occupancy.
- **Metrics Cards:** Displays high-level refund statistics.

### 3. Navigation
- Added "Analytics" link to the Admin Navbar in `app/pages/admin_users.py`.

### 4. Routing
- Registered `/admin/analytics` route in `app/app.py`.

## 📊 How to Test
1.  Login as Admin (`admin@parkmycar.com` / `admin123`).
2.  Navigate to the Admin Dashboard.
3.  Click on "Analytics" in the top navigation bar.
4.  Verify the charts and tables display data (you may need to create some bookings first if the DB is fresh).
