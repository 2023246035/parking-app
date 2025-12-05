# Refund Rejection Feature - Implementation Guide

## Overview
This feature allows admins to reject refund requests with a reason, which is automatically sent to the user via email.

## What Was Implemented

### 1. Email Notification System
- **File**: `app/services/email_service.py`
- **Function**: `send_refund_rejection_email()`
- **Features**:
  - Professional HTML email template with red gradient header
  - Clear rejection status and reason display
  - Works with Gmail SMTP, AWS SES, or console mode
  - Includes both HTML and plain text versions

### 2. Admin Rejection Modal
- **File**: `app/pages/admin_refunds.py`
- **Components**:
  - `rejection_modal()` - Modal dialog to collect rejection reason
  - State variables for modal management
  - Text area for detailed reason input
  - Validation to ensure reason is provided

### 3. Updated Admin Workflow
- **Old Flow**: Click "Reject" → Immediate rejection
- **New Flow**: Click "Reject" → Modal opens → Enter reason → Confirm → Email sent to user

### 4. Database Enhancement (Optional)
- **Recommended**: Add `rejection_reason` field to `Booking` model
- **Current**: Reason is stored in audit log details
- **Future**: Can be stored directly on booking record

## How It Works

### Admin Side:
1. Admin reviews pending refund request
2. Clicks "Reject" button
3. Modal opens asking for rejection reason
4. Admin enters detailed reason
5. Clicks "Confirm Rejection"
6. System:
   - Updates booking status to "Rejected"
   - Logs action in audit log with reason
   - Sends email to user with reason
   - Shows success toast notification

### User Side:
1. User receives professional email notification
2. Email contains:
   - Booking ID
   - Clear rejection status
   - Detailed reason for rejection
   - Support contact information
3. User can contact support if needed

## Email Template Preview

**Subject**: ParkMyCar - Refund Request Update

**Content**:
```
🚗 ParkMyCar
Refund Request Update

Hello [User Name],

We've reviewed your refund request for booking BK-123.

┌─────────────────────────────────────┐
│ Refund Request Status: Declined     │
│                                     │
│ Unfortunately, we're unable to      │
│ process your refund request at     │
│ this time.                          │
└─────────────────────────────────────┘

Reason for Decline:
[Admin's detailed reason appears here]

If you have any questions or concerns about this decision,
please don't hesitate to contact our support team.

Best regards,
ParkMyCar Support Team
```

## Testing the Feature

### 1. Test in Console Mode (No Email Setup Required)
```bash
# In .env file:
EMAIL_PROVIDER=console

# Run the app
python -m reflex run

# Steps:
# 1. Create a booking and cancel it (so it has Pending refund)
# 2. Go to Admin → Refunds
# 3. Click "Reject" on a refund
# 4. Enter reason and confirm
# 5. Check terminal for email output
```

### 2. Test with Gmail (Real Email)
```bash
# In .env file:
EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=your_app_password

# Run the app
python -m reflex run

# Steps:
# 1. Click "Reject" on a refund
# 2. Enter reason and confirm
# 3. Check user's email inbox
```

## Database Schema Update (Recommended)

To store rejection_reason directly on the booking:

### Option 1: Add via Alembic Migration
```python
# Create migration file: alembic/versions/xxx_add_rejection_reason.py

from alembic import op
import sqlalchemy as sa

def upgrade():
    op.add_column('booking', 
        sa.Column('rejection_reason', sa.String(), nullable=True)
    )

def downgrade():
    op.drop_column('booking', 'rejection_reason')
```

### Option 2: Manual SQL (SQLite)
```sql
ALTER TABLE booking ADD COLUMN rejection_reason TEXT;
```

### Option 3: Update Model and Reinit DB (Development Only)
```python
# In app/db/models.py, Booking class:
rejection_reason: Optional[str] = Field(default=None)  # Add after line 89

# Then:
rm parking_app.db  # WARNING: Deletes all data!
reflex db init
```

### Update the Code After DB Change
Once the field is added, update `app/pages/admin_refunds.py` line ~128:
```python
# Change from:
# For now, we'll store it in cancellation_reason or add a comment in audit log

# To:
booking.rejection_reason = self.rejection_reason
```

## Configuration

### Email Provider Settings

**Console Mode** (Development):
```env
EMAIL_PROVIDER=console
```

**Gmail SMTP** (Free):
```env
EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=your_16_char_app_password
```

**AWS SES** (Enterprise):
```env
EMAIL_PROVIDER=ses
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=your_key
AWS_SECRET_ACCESS_KEY=your_secret
SES_SENDER_EMAIL=noreply@yourdomain.com
```

## Error Handling

The system handles various error scenarios:

1. **Missing Rejection Reason**: Toast error, modal stays open
2. **Booking Not Found**: Toast error, modal closes
3. **Already Processed**: Toast error, modal closes
4. **Email Send Failure**: Warning toast (rejection still processed)
5. **Database Error**: Error toast, logs exception

## Features

✅ **Required Reason**: Admin must provide reason
✅ **Email Notification**: User receives professional email
✅ **Audit Trail**: Reason stored in audit log
✅ **Multiple Providers**: Gmail, AWS SES, or console
✅ **Error Handling**: Comprehensive error messages
✅ **UI Feedback**: Toast notifications for all actions
✅ **Validation**: Empty reasons are rejected

## Future Enhancements

Possible improvements:

1. **Predefined Reasons**: Dropdown with common reasons
2. **Reason Templates**: Quick-select common explanations
3. **Multi-language**: Email templates in user's language
4. **SMS Notification**: Optional SMS in addition to email
5. **Appeal Process**: Allow users to appeal rejections
6. **Analytics**: Track rejection reasons for insights

## Troubleshooting

### Rejection Modal Not Opening
- Check browser console for errors
- Verify `rejection_modal()` is added to page
- Check state variables are initialized

### Email Not Sent
- Verify EMAIL_PROVIDER in .env
- Check Gmail credentials (if using Gmail)
- Review terminal logs for error messages
- Test with `python test_email.py`

### Database Errors
- If using rejection_reason field, ensure it's added to schema
- Check audit log table exists
- Verify booking exists and has "Pending" status

## Support

For issues or questions:
1. Check terminal logs for detailed error messages
2. Review `GMAIL_SETUP_GUIDE.md` for email configuration
3. Test with console mode first before using real email
4. Verify database schema matches code expectations

---

**Implementation Date**: December  2024
**Status**: ✅ Ready to Use
**Email Support**: Gmail (Free), AWS SES, Console
**Database**: Optional rejection_reason field recommended
