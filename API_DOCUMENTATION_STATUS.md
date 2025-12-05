# API Documentation - Current Status

## Summary

The `/docs` endpoint is **not available** in the current Reflex setup due to framework limitations.

---

## Why `/docs` Doesn't Work

### Reflex Architecture
Reflex 0.8.x uses a **state-based architecture** with WebSocket communication, not traditional REST APIs:

- **Frontend ↔ Backend**: WebSocket connections
- **State Management**: Automatic sync via Reflex events
- **FastAPI**: Used internally but not directly accessible

### The Challenge
```python
# This doesn't work in Reflex 0.8.x:
app.api.include_router(api_router)  # ❌ app.api doesn't exist

# Neither does this:
app._app.include_router(api_router)  # ❌ app._app doesn't exist
```

---

## What We Have

### ✅ API Route Functions (Internal Use)
The file `app/api/routes.py` contains useful functions:

```python
- get_parking_lots(location, search)
- get_parking_lot(lot_id)
- update_availability(lot_id, available_spots)
- get_bookings(user_email, status_filter)
- create_booking(data)
- cancel_booking(booking_id)
```

These can be **called internally** from Reflex states, but are **not exposed as REST endpoints**.

---

## Alternatives for API Access

### Option 1: Use Reflex Events (Recommended)
**Current approach** - already working:

```python
# In your Reflex state
@rx.event
async def load_parking_lots(self):
    with rx.session() as session:
        lots = session.exec(select(ParkingLot)).all()
        self.parking_lots = [lot.to_dict() for lot in lots]
```

**Pros:**
- ✅ Works perfectly with Reflex
- ✅ Automatic UI updates
- ✅ Built-in state management

**Cons:**
- ❌ Not accessible from external apps (mobile, etc.)

---

### Option 2: Separate FastAPI App
Create a **standalone FastAPI app** alongside Reflex:

**File: `api_server.py`**
```python
from fastapi import FastAPI
from app.api.routes import router

api_app = FastAPI(title="Parking App API")
api_app.include_router(router)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(api_app, host="0.0.0.0", port=8001)
```

**Run both servers:**
```bash
# Terminal 1 - Reflex app
python -m reflex run

# Terminal 2 - API server
python api_server.py
```

**Access:**
- Reflex App: `http://localhost:3000`
- API Docs: `http://localhost:8001/docs`

**Pros:**
- ✅ Full Swagger UI
- ✅ External API access
- ✅ Independent scaling

**Cons:**
- ❌ Two separate servers
- ❌ More complex deployment

---

### Option 3: Upgrade Reflex
Newer versions of Reflex might have better FastAPI integration:

```bash
pip install --upgrade reflex
```

Check Reflex docs for API support in newer versions.

---

### Option 4: Custom Middleware
Access Reflex's internal FastAPI app through middleware (advanced):

**Not recommended** - breaks encapsulation and may break on updates.

---

## What's Working Right Now

Even though `/docs` isn't available, these features are **fully functional**:

### ✅ 1. Booking Validation
- Complete field validation
- Error messages at each step
- Test at: `http://localhost:3000/listings`

### ✅ 2. Add New Rule Validation
- Wizard with step-by-step validation
- Test at: `http://localhost:3000/smart-dashboard`

### ✅ 3. Share Feature
- Copy booking details to clipboard
- Test at: `http://localhost:3000/bookings`

### ✅ 4. All CRUD Operations
- Create bookings
- Read bookings
- Update bookings
- Cancel bookings
- All work through Reflex events

---

## Recommendation

### For Current Project:
**Stick with Reflex events** - they work perfectly for your web app.

### If You Need External API Access:
Consider **Option 2** (Separate FastAPI App):
- Minimal code changes
- Clean separation
- Full Swagger documentation

---

## Next Steps

Would you like me to:

1. **Create a separate FastAPI server** for API access?
2. **Focus on the working features** (validation, share, etc.)?
3. **Explore other Reflex versions** for better API support?

Let me know your preference! 🚀
