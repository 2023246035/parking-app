"""Email Service for sending OTP and other notifications via AWS SES."""
import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email provider configuration
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "console")  # 'console' or 'ses'

# AWS SES Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@parkmycar.com")


def send_otp_email_console(email: str, otp_code: str) -> bool:
    """Log OTP to console for development."""
    try:
        print("\n" + "=" * 60)
        print(f"📧 EMAIL TO: {email}")
        print(f"📋 SUBJECT: ParkMyCar - Password Reset OTP")
        print("-" * 60)
        print(f"Your OTP code is: {otp_code}")
        print(f"This code will expire in 2 minutes.")
        print(f"")
        print(f"If you didn't request this, please ignore this email.")
        print("=" * 60 + "\n")

        logging.info(f"OTP email sent to {email} (logged to console)")
        return True

    except Exception as e:
        logging.exception(f"Error logging OTP to console: {e}")
        return False


def send_otp_email_ses(email: str, otp_code: str) -> bool:
    """Send OTP email using AWS SES."""
    try:
        import boto3
        from botocore.exceptions import ClientError

        # Validate AWS credentials
        if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
            logging.error("AWS credentials not configured. Please set AWS_ACCESS_KEY_ID and AWS_SECRET_ACCESS_KEY in .env file")
            return False

        # Create SES client
        ses_client = boto3.client(
            'ses',
            region_name=AWS_REGION,
            aws_access_key_id=AWS_ACCESS_KEY_ID,
            aws_secret_access_key=AWS_SECRET_ACCESS_KEY
        )

        # Email subject
        subject = "ParkMyCar - Password Reset OTP"

        # Email body (HTML)
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .otp-box {{ background: white; border: 2px solid #0ea5e9; border-radius: 8px; padding: 20px; text-align: center; margin: 20px 0; }}
                .otp-code {{ font-size: 32px; font-weight: bold; color: #0ea5e9; letter-spacing: 8px; font-family: 'Courier New', monospace; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                .warning {{ background: #fef3c7; border-left: 4px solid #f59e0b; padding: 12px; margin: 20px 0; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 ParkMyCar</h1>
                    <p>Password Reset Request</p>
                </div>
                <div class="content">
                    <h2>Hello,</h2>
                    <p>You requested to reset your password. Use the OTP code below to proceed:</p>
                    
                    <div class="otp-box">
                        <p style="margin: 0; color: #6b7280; font-size: 14px;">Your OTP Code</p>
                        <p class="otp-code">{otp_code}</p>
                        <p style="margin: 0; color: #6b7280; font-size: 12px;">Valid for 2 minutes</p>
                    </div>
                    
                    <p>Enter this code on the password reset page to continue.</p>
                    
                    <div class="warning">
                        <strong>⚠️ Security Notice:</strong> If you didn't request this password reset, please ignore this email. Your password will remain unchanged.
                    </div>
                    
                    <p>Thank you,<br><strong>ParkMyCar Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. Please do not reply.</p>
                    <p>&copy; 2024 ParkMyCar Systems. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """

        # Email body (Plain text fallback)
        text_body = f"""
ParkMyCar - Password Reset OTP

Hello,

You requested to reset your password. Use the OTP code below to proceed:

Your OTP Code: {otp_code}
Valid for: 2 minutes

Enter this code on the password reset page to continue.

SECURITY NOTICE: If you didn't request this password reset, please ignore this email. Your password will remain unchanged.

Thank you,
ParkMyCar Team

---
This is an automated email. Please do not reply.
© 2024 ParkMyCar Systems. All rights reserved.
        """

        # Send email
        response = ses_client.send_email(
            Source=SES_SENDER_EMAIL,
            Destination={
                'ToAddresses': [email]
            },
            Message={
                'Subject': {
                    'Data': subject,
                    'Charset': 'UTF-8'
                },
                'Body': {
                    'Text': {
                        'Data': text_body,
                        'Charset': 'UTF-8'
                    },
                    'Html': {
                        'Data': html_body,
                        'Charset': 'UTF-8'
                    }
                }
            }
        )

        logging.info(f"OTP email sent successfully to {email} via AWS SES. MessageId: {response['MessageId']}")
        return True

    except ClientError as e:
        error_code = e.response['Error']['Code']
        error_message = e.response['Error']['Message']
        logging.error(f"AWS SES error ({error_code}): {error_message}")
        
        if error_code == 'MessageRejected':
            logging.error(f"Email {email} or sender {SES_SENDER_EMAIL} not verified in AWS SES")
        
        return False

    except Exception as e:
        logging.exception(f"Error sending OTP email via AWS SES: {e}")
        return False


def send_otp_email(email: str, otp_code: str) -> bool:
    """
    Send OTP code to the user's email.
    Uses AWS SES if configured, otherwise logs to console.
    """
    if EMAIL_PROVIDER == "ses":
        logging.info(f"Sending OTP via AWS SES to {email}")
        return send_otp_email_ses(email, otp_code)
    else:
        logging.info(f"Sending OTP via console to {email}")
        return send_otp_email_console(email, otp_code)
