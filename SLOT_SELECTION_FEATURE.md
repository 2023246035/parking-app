# Smart Dashboard Slot Selection Feature

## Overview
This feature allows users to select a preferred parking slot when creating auto-booking rules in the Smart Dashboard. The system will automatically check for slot availability and notify users if their preferred slot is taken by someone else.

## What Was Implemented

### 1. Database Changes
- **Added `slot_id` column** to the `bookingrule` table
- Migration script: `migrate_booking_rule_slot.py`
- Column type: TEXT (Optional)

### 2. UI Enhancements

#### Rule Creation Modal
- Added **"Preferred Slot"** input field with autocomplete
- Available slots: A1-A5, B1-B5 (can be expanded)
- Field is **mandatory** - validation ensures a slot is selected before saving

#### Rule Display Card
- Added **Slot information** row showing the preferred slot
- Displayed with parking icon and orange highlight
- Shows: "Slot: A1" (example)

### 3. Auto-Booking Logic

#### Conflict Detection
When the system processes auto-booking rules:
1. Checks if the preferred slot exists in the rule
2. Queries the database for any existing bookings on:
   - Same parking lot
   - Same date (tomorrow)
   - Same time
   - Same slot
   - Status != "Cancelled"
3. If a conflict is found:
   - **Skips creating the booking**
   - Shows warning toast: "Skipped [Location]: Slot [X] unavailable."
   - Continues processing other rules

#### Booking Creation
If no conflict:
- Creates booking with the user's preferred `slot_id`
- Falls back to "AUTO-A1" if no slot is specified

### 4. Validation
All fields in the auto-booking rule are now mandatory:
- ✅ Location
- ✅ Days (at least one)
- ✅ Time
- ✅ Duration
- ✅ Vehicle Number
- ✅ Phone Number
- ✅ **Preferred Slot** (NEW)

## User Experience

### Creating a Rule
1. Click "New Rule" in Smart Dashboard
2. Fill in all details including vehicle, phone, **and preferred slot**
3. Select slot from dropdown (e.g., "A1", "B1")
4. Save the rule

### Auto-Booking Behavior
**Scenario 1: Slot Available**
- ✅ System creates booking automatically
- ✅ User receives success notification
- ✅ Booking appears in "My Bookings"

**Scenario 2: Slot Taken**
- ⚠️ System detects conflict
- ⚠️ User receives warning: "Skipped [Location]: Slot A1 unavailable."
- ⚠️ No booking is created
- 💡 User can manually book a different slot or wait for next day

### Viewing Rules
- All created rules display the preferred slot
- Easy to see at a glance which slot each rule will try to book

## Technical Details

### Files Modified
1. `app/db/models.py`
   - Added `slot_id` field to `BookingRule` model

2. `app/pages/smart_dashboard.py`
   - Updated `Rule` Pydantic model
   - Added `form_slot` state variable
   - Added `available_slots` list
   - Implemented conflict detection in `process_rules`
   - Added slot validation in `save_rule`
   - Updated UI with slot input field
   - Added slot display to rule cards

3. `migrate_booking_rule_slot.py` (NEW)
   - Database migration script

### Conflict Detection Query
```python
slot_conflict = session.exec(
    select(DBBooking)
    .where(DBBooking.lot_id == lot.id)
    .where(DBBooking.start_date == tomorrow_date_str)
    .where(DBBooking.start_time == rule.time)
    .where(DBBooking.slot_id == rule.slot_id)
    .where(DBBooking.status != "Cancelled")
).first()
```

## Benefits
1. **Consistency**: Users can always book their preferred spot
2. **Transparency**: Clear notifications when slots are unavailable
3. **Conflict Avoidance**: Prevents double-booking of the same slot
4. **Better Planning**: Users know in advance which slot they'll get

## Future Enhancements
- Dynamic slot loading based on selected parking lot
- Real-time slot availability display
- Alternative slot suggestion if preferred is taken
- Historical slot usage analytics
