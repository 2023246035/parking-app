"""
Test script to verify Gmail SMTP OTP email sending
Run this after configuring your .env file with Gmail credentials
"""
import os
import sys

# Add the app directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.email_service import send_otp_email, EMAIL_PROVIDER, GMAIL_SENDER_EMAIL

def test_email_sending():
    """Test the email sending functionality"""
    
    print("\n" + "="*60)
    print("EMAIL SERVICE TEST")
    print("="*60)
    
    # Show current configuration
    print(f"\n📧 Current Email Provider: {EMAIL_PROVIDER}")
    
    if EMAIL_PROVIDER == "gmail":
        if GMAIL_SENDER_EMAIL:
            print(f"   Gmail Sender: {GMAIL_SENDER_EMAIL}")
            print(f"   Status: ✅ Configured")
        else:
            print("   Status: ❌ Not configured")
            print("\n⚠️  Please configure GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD in .env")
            print("   See GMAIL_SETUP_GUIDE.md for instructions")
            return
    elif EMAIL_PROVIDER == "console":
        print("   Status: ⚠️  Development mode (console only)")
    elif EMAIL_PROVIDER == "ses":
        print("   Status: AWS SES configured")
    
    # Get test email
    print("\n" + "-"*60)
    test_email = input("Enter email address to test OTP sending: ").strip()
    
    if not test_email or "@" not in test_email:
        print("❌ Invalid email address")
        return
    
    # Generate test OTP
    test_otp = "123456"
    
    print(f"\n📤 Sending test OTP to: {test_email}")
    print(f"   OTP Code: {test_otp}")
    print(f"   Provider: {EMAIL_PROVIDER}")
    print("\n   Please wait...")
    
    # Send the email
    success = send_otp_email(test_email, test_otp)
    
    print("\n" + "="*60)
    if success:
        print("✅ SUCCESS! OTP email sent successfully")
        print(f"\n📬 Check the inbox of: {test_email}")
        print("   (Also check spam/junk folder)")
        if EMAIL_PROVIDER == "console":
            print("\n   Note: In console mode, email is only printed above")
    else:
        print("❌ FAILED to send OTP email")
        print("\n   Troubleshooting:")
        print("   1. Check your .env configuration")
        print("   2. Verify Gmail App Password is correct")
        print("   3. Check terminal logs for error details")
        print("   4. See GMAIL_SETUP_GUIDE.md for help")
    print("="*60 + "\n")

if __name__ == "__main__":
    try:
        test_email_sending()
    except KeyboardInterrupt:
        print("\n\n❌ Test cancelled by user\n")
    except Exception as e:
        print(f"\n❌ Error during test: {e}\n")
        import traceback
        traceback.print_exc()
