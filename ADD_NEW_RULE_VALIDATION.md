# ✅ ADD NEW RULE - VALIDATION ON NEXT STEP BUTTON IMPLEMENTED!

## Feature: Auto-Booking Rule Creation

The "Add New Rule" feature allows users to schedule parking bookings automatically.  
Now includes **comprehensive validation at each step!**

---

## Wizard Steps

### **Step 1: Location & Days**
- Select parking location
- Choose days of the week (Mon-Sun)

### **Step 2: Time & Duration**
- Select time
- Set duration (hours)

### **Step 3: Vehicle & Phone**
- Enter vehicle number
- Enter phone number

### **Step 4: Slot Selection**
- Choose parking slot

---

## Validation Implemented

### **Step 1 Validation (Location & Days)**

When clicking "Next Step":
- ✅ Validates location is selected
- ✅ Validates at least one day is selected

**Error Messages:**
- "Please select a parking location"
- "Please select at least one day"

**Validation Method:** `validate_location_and_days()`

---

### **Step 2 Validation (Time & Duration)**

When clicking "Next Step":
- ✅ Validates time is not empty
- ✅ Validates duration is a valid number
- ✅ Validates duration is between 1-24 hours

**Error Messages:**
- "Please select a time"
- "Duration must be at least 1 hour"
- "Duration cannot exceed 24 hours"
- "Please enter a valid duration"

**Validation Method:** `validate_time_and_duration()`

---

### **Step 3 Validation (Vehicle & Phone)**

When clicking "Next Step":
- ✅ Validates vehicle number is not empty
- ✅ Validates vehicle is at least 3 characters
- ✅ Validates phone number is not empty
- ✅ Validates phone has only digits
- ✅ Validates phone is 10-15 digits

**Error Messages:**
- "Vehicle number is required"
- "Vehicle number must be at least 3 characters"
- "Phone number is required"
- "Phone number must contain only digits"
- "Phone number must be at least 10 digits"

**Validation Method:** `validate_vehicle_and_phone()`

---

### **Step 4 Validation (Slot Selection)**

When clicking "Save Rule":
- ✅ Validates a slot is selected

**Error Messages:**
- "Please select a parking slot"

**Validation Method:** `validate_slot()`

---

## How It Works

### Updated `next_rule_step()` Method:

```python
@rx.event
def next_rule_step(self):
    """Move to next step in the wizard - validates current step first"""
    # Validate current step before proceeding
    if self.rule_wizard_step == 1:
        # Step 1: Validate location and days
        if not self.validate_location_and_days():
            return  # Stay on step 1 if validation fails
    
    elif self.rule_wizard_step == 2:
        # Step 2: Validate time and duration
        if not self.validate_time_and_duration():
            return  # Stay on step 2 if validation fails
    
    elif self.rule_wizard_step == 3:
        # Step 3: Validate vehicle and phone
        if not self.validate_vehicle_and_phone():
            return  # Stay on step 3 if validation fails
    
    # If validation passed, move to next step
    if self.rule_wizard_step < 4:
        self.rule_wizard_step += 1
```

---

## User Experience

### ❌ **Invalid Data - Cannot Proceed:**

**Step 1:**
```
1. Don't select a location
2. Click "Next Step"
3. Error shows: "Please select a parking location"
4. Stays on Step 1
5. Must select location to proceed
```

**Step 2:**
```
1. Enter duration as "0"
2. Click "Next Step"
3. Error shows: "Duration must be at least 1 hour"
4. Stays on Step 2
5. Must enter valid duration to proceed
```

**Step 3:**
```
1. Enter vehicle as "AB"
2. Click "Next Step"
3. Error shows: "Vehicle number must be at least 3 characters"
4. Stays on Step 3
5. Must enter valid vehicle to proceed
```

### ✅ **Valid Data - Smooth Flow:**

```
Step 1: Select location + days → Click "Next Step"
  ↓
Step 2: Enter time + duration → Click "Next Step"
  ↓
Step 3: Enter vehicle + phone → Click "Next Step"
  ↓
Step 4: Select slot → Click "Save Rule"
  ↓
Rule created successfully!
```

---

## Validation Error Fields Added

```python
# Validation error messages
error_location: str = ""
error_days: str = ""
error_time: str = ""
error_duration: str = ""
error_vehicle: str = ""
error_phone: str = ""
error_slot: str = ""
```

---

## Validation Methods Added

1. **`validate_location_and_days()`** - Step 1 validation
2. **`validate_time_and_duration()`** - Step 2 validation
3. **`validate_vehicle_and_phone()`** - Step 3 validation
4. **`validate_slot()`** - Step 4 validation

---

## Error Display

Error messages appear in **red text** below the relevant field:

```python
rx.cond(
    SmartDashboardState.error_location != "",
    rx.el.p(
        SmartDashboardState.error_location,
        class_name="text-sm text-red-600 mt-1"
    ),
)
```

---

## Files Modified

1. **`app/pages/smart_dashboard.py`**
   - Added validation error fields
   - Added 4 validation methods
   - Updated `next_rule_step()` to run validation
   -  Added error message displays in Step 1

---

## Test Scenarios

### Test 1: No Location
1. Click "Add New Rule"
2. Don't select a location
3. Click "Next Step"
4. ✅ Error: "Please select a parking location"
5. ✅ Stays on Step 1

### Test 2: No Days
1. Select a location
2. Don't select any days
3. Click "Next Step"
4. ✅ Error: "Please select at least one day"
5. ✅ Stays on Step 1

### Test 3: Invalid Duration
1. Complete Step 1
2. Enter "0" as duration
3. Click "Next Step"
4. ✅ Error: "Duration must be at least 1 hour"
5. ✅ Stays on Step 2

### Test 4: Short Vehicle
1. Complete Steps 1-2
2. Enter "AB" as vehicle
3. Click "Next Step"
4. ✅ Error: "Vehicle number must be at least 3 characters"
5. ✅ Stays on Step 3

### Test 5: All Valid
1. Select location + days
2. Enter time + valid duration
3. Enter valid vehicle + phone
4. Select slot
5. ✅ Rule created successfully

---

## Result

🎉 **"Add New Rule" wizard now has validation on every "Next Step" button!**

Users cannot proceed to the next step without entering valid data.  
Error messages appear immediately when clicking "Next Step" with invalid data.

The app will reload automatically. Try creating a new rule and see the validation in action! 🚀
