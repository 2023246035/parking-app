"""Email Service for sending OTP and other notifications via AWS SES."""
import logging
import os
from typing import Optional
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Email provider configuration
EMAIL_PROVIDER = os.getenv("EMAIL_PROVIDER", "console")  # 'console', 'ses', or 'gmail'

# AWS SES Configuration
AWS_REGION = os.getenv("AWS_REGION", "us-east-1")
AWS_ACCESS_KEY_ID = os.getenv("AWS_ACCESS_KEY_ID")
AWS_SECRET_ACCESS_KEY = os.getenv("AWS_SECRET_ACCESS_KEY")
SES_SENDER_EMAIL = os.getenv("SES_SENDER_EMAIL", "noreply@parkmycar.com")

# Gmail SMTP Configuration (FREE)
GMAIL_SENDER_EMAIL = os.getenv("GMAIL_SENDER_EMAIL")  # Your Gmail address
GMAIL_APP_PASSWORD = os.getenv("GMAIL_APP_PASSWORD")  # Gmail App Password (not regular password)


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


def send_otp_email_gmail(email: str, otp_code: str) -> bool:
    """Send OTP email using Gmail SMTP (FREE)."""
    try:
        import smtplib
        from email.mime.multipart import MIMEMultipart
        from email.mime.text import MIMEText

        # Validate Gmail credentials
        if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
            logging.error("Gmail credentials not configured. Please set GMAIL_SENDER_EMAIL and GMAIL_APP_PASSWORD in .env file")
            return False

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

        # Create message
        message = MIMEMultipart('alternative')
        message['From'] = GMAIL_SENDER_EMAIL
        message['To'] = email
        message['Subject'] = subject

        # Attach both plain text and HTML versions
        part1 = MIMEText(text_body, 'plain')
        part2 = MIMEText(html_body, 'html')
        message.attach(part1)
        message.attach(part2)

        # Connect to Gmail SMTP server
        with smtplib.SMTP('smtp.gmail.com', 587) as server:
            server.starttls()  # Upgrade to secure connection
            server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
            server.send_message(message)

        logging.info(f"OTP email sent successfully to {email} via Gmail SMTP")
        return True

    except smtplib.SMTPAuthenticationError as e:
        logging.error(f"Gmail SMTP authentication failed. Please check your email and app password: {e}")
        return False

    except smtplib.SMTPException as e:
        logging.error(f"SMTP error occurred: {e}")
        return False

    except Exception as e:
        logging.exception(f"Error sending OTP email via Gmail: {e}")
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
    Supports multiple providers: Gmail (FREE), AWS SES, or console logging.
    """
    if EMAIL_PROVIDER == "gmail":
        logging.info(f"Sending OTP via Gmail SMTP to {email}")
        return send_otp_email_gmail(email, otp_code)
    elif EMAIL_PROVIDER == "ses":
        logging.info(f"Sending OTP via AWS SES to {email}")
        return send_otp_email_ses(email, otp_code)
    else:
        logging.info(f"Sending OTP via console to {email}")
        return send_otp_email_console(email, otp_code)


def send_refund_rejection_email(email: str, booking_id: str, reason: str, user_name: str = "User") -> bool:
    """
    Send refund rejection notification email to user.
    Works with Gmail, AWS SES, or console mode based on EMAIL_PROVIDER.
    """
    try:
        # Email subject
        subject = "ParkMyCar - Refund Request Update"
        
        # Email body (HTML)
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f9fafb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .info-box {{ background: white; border-left: 4px solid #dc2626; padding: 20px; margin: 20px 0; border-radius: 4px; }}
                .reason-box {{ background: #fef2f2; border: 1px solid #fecaca; padding: 15px; margin: 20px 0; border-radius: 8px; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                .btn {{ display: inline-block; padding: 12px 24px; background: #2563eb; color: white; text-decoration: none; border-radius: 8px; margin-top: 20px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 ParkMyCar</h1>
                    <p>Refund Request Update</p>
                </div>
                <div class="content">
                    <h2>Hello {user_name},</h2>
                    <p>We've reviewed your refund request for booking <strong>{booking_id}</strong>.</p>
                    
                    <div class="info-box">
                        <h3 style="margin-top: 0; color: #dc2626;">Refund Request Status: Declined</h3>
                        <p>Unfortunately, we're unable to process your refund request at this time.</p>
                    </div>
                    
                    <div class="reason-box">
                        <strong>Reason for Decline:</strong>
                        <p style="margin: 10px 0 0 0;">{reason}</p>
                    </div>
                    
                    <p>If you have any questions or concerns about this decision, please don't hesitate to contact our support team.</p>
                    
                    <p style="margin-top: 30px;">Best regards,<br><strong>ParkMyCar Support Team</strong></p>
                </div>
                <div class="footer">
                    <p>This is an automated email. For support, please contact us through the app.</p>
                    <p>&copy; 2024 ParkMyCar Systems. All rights reserved.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Email body (Plain text fallback)
        text_body = f"""
ParkMyCar - Refund Request Update

Hello {user_name},

We've reviewed your refund request for booking {booking_id}.

REFUND REQUEST STATUS: DECLINED

Unfortunately, we're unable to process your refund request at this time.

REASON FOR DECLINE:
{reason}

If you have any questions or concerns about this decision, please don't hesitate to contact our support team.

Best regards,
ParkMyCar Support Team

---
This is an automated email. For support, please contact us through the app.
© 2024 ParkMyCar Systems. All rights reserved.
        """
        
        # Send based on provider
        if EMAIL_PROVIDER == "gmail":
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
                logging.error("Gmail credentials not configured")
                return False
            
            message = MIMEMultipart('alternative')
            message['From'] = GMAIL_SENDER_EMAIL
            message['To'] = email
            message['Subject'] = subject
            
            part1 = MIMEText(text_body, 'plain')
            part2 = MIMEText(html_body, 'html')
            message.attach(part1)
            message.attach(part2)
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                server.send_message(message)
            
            logging.info(f"Refund rejection email sent to {email} via Gmail")
            return True
            
        elif EMAIL_PROVIDER == "ses":
            import boto3
            from botocore.exceptions import ClientError
            
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logging.error("AWS credentials not configured")
                return False
            
            ses_client = boto3.client(
                'ses',
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID,
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            response = ses_client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logging.info(f"Refund rejection email sent to {email} via AWS SES")
            return True
            
        else:
            # Console mode
            print("\n" + "="*60)
            print(f"📧 REFUND REJECTION EMAIL TO: {email}")
            print(f"📋 SUBJECT: {subject}")
            print("-"*60)
            print(f"User: {user_name}")
            print(f"Booking: {booking_id}")
            print(f"Reason: {reason}")
            print("="*60 + "\n")
            logging.info(f"Refund rejection email logged to console for {email}")
            return True
            
    except Exception as e:
        logging.exception(f"Error sending refund rejection email: {e}")
        return False


def send_booking_reminder_email(email: str, booking_details: dict) -> bool:
    """
    Send booking reminder email (1 hour before).
    """
    try:
        subject = "⏰ Reminder: Your Parking Booking Starts in 1 Hour"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #f59e0b 0%, #d97706 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #fffbeb; padding: 30px; border-radius: 0 0 10px 10px; }}
                .details-box {{ background: white; border: 1px solid #fcd34d; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 Upcoming Booking</h1>
                    <p>Starts in approximately 1 hour</p>
                </div>
                <div class="content">
                    <h2>Hello {booking_details.get('user_name', 'Customer')},</h2>
                    <p>This is a friendly reminder about your parking reservation today.</p>
                    
                    <div class="details-box">
                        <p><strong>📍 Location:</strong> {booking_details['lot_name']}</p>
                        <p><strong>🕒 Time:</strong> {booking_details['start_time']} - {booking_details['end_time']}</p>
                        <p><strong>🚗 Vehicle:</strong> {booking_details['vehicle_number']}</p>
                        <p><strong>🔢 Slot:</strong> {booking_details['slot_id']}</p>
                    </div>
                    
                    <p>Drive safely!</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Reminder: Your Booking Starts in 1 Hour

Hello {booking_details.get('user_name', 'Customer')},

This is a friendly reminder about your parking reservation today.

Location: {booking_details['lot_name']}
Time: {booking_details['start_time']} - {booking_details['end_time']}
Vehicle: {booking_details['vehicle_number']}
Slot: {booking_details['slot_id']}

Drive safely!

---
ParkMyCar Systems
        """

        if EMAIL_PROVIDER == "gmail":
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
                logging.error("Gmail credentials not configured")
                return False
            
            message = MIMEMultipart('alternative')
            message['From'] = GMAIL_SENDER_EMAIL
            message['To'] = email
            message['Subject'] = subject
            
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                server.send_message(message)
            
            logging.info(f"Reminder email sent to {email} via Gmail")
            return True
            
        elif EMAIL_PROVIDER == "ses":
            import boto3
            from botocore.exceptions import ClientError
            
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logging.error("AWS credentials not configured")
                return False
            
            ses_client = boto3.client(
                'ses', 
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            ses_client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logging.info(f"Reminder email sent to {email} via SES")
            return True
            
        else:
            print("\n" + "="*60)
            print(f"⏰ REMINDER EMAIL TO: {email}")
            print(f"📋 SUBJECT: {subject}")
            print("-"*60)
            print(text_body)
            print("="*60 + "\n")
            return True

    except Exception as e:
        logging.exception(f"Error sending reminder email: {e}")
        return False


def send_booking_confirmation_email(email: str, booking_details: dict) -> bool:
    """
    Send booking confirmation email immediately after booking.
    """
    try:
        subject = "✅ Booking Confirmed: Your Spot is Reserved!"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #ecfdf5; padding: 30px; border-radius: 0 0 10px 10px; }}
                .details-box {{ background: white; border: 1px solid #6ee7b7; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                .highlight {{ color: #059669; font-weight: bold; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>🚗 Booking Confirmed!</h1>
                    <p>Your parking spot is secured.</p>
                </div>
                <div class="content">
                    <h2>Hello {booking_details.get('user_name', 'Customer')},</h2>
                    <p>Great news! Your parking reservation has been successfully confirmed.</p>
                    
                    <div class="details-box">
                        <p><strong>📍 Location:</strong> {booking_details['lot_name']}</p>
                        <p><strong>📅 Date:</strong> {booking_details['start_date']}</p>
                        <p><strong>🕒 Time:</strong> {booking_details['start_time']} ({booking_details['duration']} hours)</p>
                        <p><strong>🔢 Slot:</strong> <span class="highlight">{booking_details['slot_id']}</span></p>
                        <p><strong>🚗 Vehicle:</strong> {booking_details['vehicle_number']}</p>
                        <p><strong>💰 Total Price:</strong> ${booking_details['total_price']:.2f}</p>
                        <p><strong>💳 Payment Status:</strong> {booking_details.get('payment_status', 'Paid')}</p>
                    </div>
                    
                    <p>Please arrive on time to ensure a smooth parking experience.</p>
                    <p>Need to cancel? You can do so from the "My Bookings" section in the app.</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                    <p>Thank you for choosing us!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Booking Confirmed!

Hello {booking_details.get('user_name', 'Customer')},

Great news! Your parking reservation has been successfully confirmed.

DETAILS:
Location: {booking_details['lot_name']}
Date: {booking_details['start_date']}
Time: {booking_details['start_time']} ({booking_details['duration']} hours)
Slot: {booking_details['slot_id']}
Vehicle: {booking_details['vehicle_number']}
Total Price: ${booking_details['total_price']:.2f}

Please arrive on time. You can view or cancel your booking in the app.

Thank you,
ParkMyCar Systems
        """

        if EMAIL_PROVIDER == "gmail":
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
                logging.error("Gmail credentials not configured")
                return False
            
            message = MIMEMultipart('alternative')
            message['From'] = GMAIL_SENDER_EMAIL
            message['To'] = email
            message['Subject'] = subject
            
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                server.send_message(message)
            
            logging.info(f"Confirmation email sent to {email} via Gmail")
            return True
            
        elif EMAIL_PROVIDER == "ses":
            import boto3
            from botocore.exceptions import ClientError
            
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logging.error("AWS credentials not configured")
                return False
            
            ses_client = boto3.client(
                'ses', 
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            ses_client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logging.info(f"Confirmation email sent to {email} via SES")
            return True
            
        else:
            print("\n" + "="*60)
            print(f"✅ BOOKING CONFIRMATION EMAIL TO: {email}")
            print(f"📋 SUBJECT: {subject}")
            print("-"*60)
            print(text_body)
            print("="*60 + "\n")
            return True

    except Exception as e:
        logging.exception(f"Error sending confirmation email: {e}")
        return False


def send_cancellation_confirmation_email(email: str, booking_details: dict) -> bool:
    """
    Send booking cancellation confirmation email.
    """
    try:
        subject = "🔴 Booking Cancelled - Confirmation"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #dc2626 0%, #991b1b 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #fef2f2; padding: 30px; border-radius: 0 0 10px 10px; }}
                .details-box {{ background: white; border-left: 4px solid #dc2626; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
                .refund-notice {{ background: #dbeafe; border: 1px solid #3b82f6; padding: 15px; margin: 20px 0; border-radius: 8px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Booking Cancelled</h1>
                    <p>Your reservation has been cancelled</p>
                </div>
                <div class="content">
                    <h2>Hello {booking_details.get('user_name', 'Customer')},</h2>
                    <p>Your booking has been successfully cancelled as requested.</p>
                    
                    <div class="details-box">
                        <h3 style="margin-top: 0;">Cancelled Booking Details:</h3>
                        <p><strong>Location:</strong> {booking_details['lot_name']}</p>
                        <p><strong>Date:</strong> {booking_details['start_date']}</p>
                        <p><strong>Time:</strong> {booking_details['start_time']}</p>
                        <p><strong>Slot:</strong> {booking_details['slot_id']}</p>
                        <p><strong>Vehicle:</strong> {booking_details['vehicle_number']}</p>
                        <p><strong>Booking Amount:</strong> ${booking_details['total_price']:.2f}</p>
                    </div>
                    
                    <div class="refund-notice">
                        <strong>Refund Information:</strong>
                        <p style="margin: 10px 0 0 0;">
                            {booking_details.get('refund_message', 'If applicable, your refund will be processed within 5-7 business days.')}
                        </p>
                    </div>
                    
                    <p>We're sorry to see you cancel! We hope to serve you again in the future.</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                    <p>Need help? Contact support through the app.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Booking Cancelled

Hello {booking_details.get('user_name', 'Customer')},

Your booking has been successfully cancelled as requested.

CANCELLED BOOKING DETAILS:
Location: {booking_details['lot_name']}
Date: {booking_details['start_date']}
Time: {booking_details['start_time']}
Slot: {booking_details['slot_id']}
Vehicle: {booking_details['vehicle_number']}
Booking Amount: ${booking_details['total_price']:.2f}

REFUND INFORMATION:
{booking_details.get('refund_message', 'If applicable, your refund will be processed within 5-7 business days.')}

We're sorry to see you cancel! We hope to serve you again in the future.

---
ParkMyCar Systems
        """

        return _send_email(email, subject, html_body, text_body)
        
    except Exception as e:
        logging.exception(f"Error sending cancellation email: {e}")
        return False


def send_refund_approval_email(email: str, refund_details: dict) -> bool:
    """
    Send refund approval notification email.
    """
    try:
        subject = "Refund Approved - Processing Payment"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #ecfdf5; padding: 30px; border-radius: 0 0 10px 10px; }}
                .details-box {{ background: white; border-left: 4px solid #10b981; padding: 20px; border-radius: 8px; margin: 20px 0; }}
                .amount-box {{ background: #dbeafe; border: 2px solid #3b82f6; padding: 20px; margin: 20px 0; border-radius: 8px; text-align: center; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Refund Approved!</h1>
                    <p>Your refund request has been approved</p>
                </div>
                <div class="content">
                    <h2>Hello {refund_details.get('user_name', 'Customer')},</h2>
                    <p>Great news! Your refund request has been approved and is being processed.</p>
                    
                    <div class="amount-box">
                        <h3 style="margin-top: 0; color: #3b82f6;">Refund Amount</h3>
                        <p style="font-size: 28px; font-weight: bold; color: #10b981; margin: 10px 0;">${refund_details['refund_amount']:.2f}</p>
                    </div>
                    
                    <div class="details-box">
                        <h3 style="margin-top: 0;">Booking Details:</h3>
                        <p><strong>Booking ID:</strong> {refund_details['booking_id']}</p>
                        <p><strong>Original Booking Date:</strong> {refund_details.get('booking_date', 'N/A')}</p>
                        <p><strong>Original Amount:</strong> ${refund_details.get('original_amount', 0):.2f}</p>
                    </div>
                    
                    <p><strong>Processing Timeline:</strong></p>
                    <p>Your refund will be credited to your original payment method within <strong>5-7 business days</strong>.</p>
                    
                    <p>Thank you for your patience!</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                    <p>Questions? Contact support through the app.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Refund Approved

Hello {refund_details.get('user_name', 'Customer')},

Great news! Your refund request has been approved and is being processed.

REFUND AMOUNT: ${refund_details['refund_amount']:.2f}

BOOKING DETAILS:
Booking ID: {refund_details['booking_id']}
Original Booking Date: {refund_details.get('booking_date', 'N/A')}
Original Amount: ${refund_details.get('original_amount', 0):.2f}

PROCESSING TIMELINE:
Your refund will be credited to your original payment method within 5-7 business days.

Thank you for your patience!

---
ParkMyCar Systems
        """

        return _send_email(email, subject, html_body, text_body)
        
    except Exception as e:
        logging.exception(f"Error sending refund approval email: {e}")
        return False


def send_welcome_email(email: str, user_details: dict) -> bool:
    """
    Send welcome email after successful registration.
    """
    try:
        subject = "Welcome to ParkMyCar - Get Started!"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #0ea5e9 0%, #2563eb 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #f0f9ff; padding: 30px; border-radius: 0 0 10px 10px; }}
                .feature-box {{ background: white; padding: 15px; margin: 15px 0; border-radius: 8px; border-left: 4px solid #0ea5e9; }}
                .cta-button {{ display: inline-block; padding: 15px 30px; background: #0ea5e9; color: white; text-decoration: none; border-radius: 8px; margin-top: 20px; font-weight: bold; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Welcome to ParkMyCar!</h1>
                    <p>Your parking just got smarter</p>
                </div>
                <div class="content">
                    <h2>Hello {user_details.get('full_name', 'there')}!</h2>
                    <p>Thank you for joining ParkMyCar! We're excited to help you find and book parking spots with ease.</p>
                    
                    <h3>What You Can Do:</h3>
                    
                    <div class="feature-box">
                        <strong>Find Parking</strong>
                        <p style="margin: 5px 0 0 0;">Search for available parking spots near your destination.</p>
                    </div>
                    
                    <div class="feature-box">
                        <strong>Book in Advance</strong>
                        <p style="margin: 5px 0 0 0;">Reserve your spot ahead of time and skip the hassle.</p>
                    </div>
                    
                    <div class="feature-box">
                        <strong>Smart Auto-Booking</strong>
                        <p style="margin: 5px 0 0 0;">Set up rules to automatically book your regular parking spots.</p>
                    </div>
                    
                    <div class="feature-box">
                        <strong>Manage Bookings</strong>
                        <p style="margin: 5px 0 0 0;">View, modify, or cancel your reservations anytime.</p>
                    </div>
                    
                    <p style="margin-top: 30px;">Need help? Our support team is here for you!</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                    <p>Happy Parking!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Welcome!

Hello {user_details.get('full_name', 'there')}!

Thank you for joining ParkMyCar! We're excited to help you find and book parking spots with ease.

WHAT YOU CAN DO:

* Find Parking
  Search for available parking spots near your destination.

* Book in Advance
  Reserve your spot ahead of time and skip the hassle.

* Smart Auto-Booking
  Set up rules to automatically book your regular parking spots.

* Manage Bookings
  View, modify, or cancel your reservations anytime.

Need help? Our support team is here for you!

---
ParkMyCar Systems
Happy Parking!
        """

        return _send_email(email, subject, html_body, text_body)
        
    except Exception as e:
        logging.exception(f"Error sending welcome email: {e}")
        return False


def send_payment_success_email(email: str, payment_details: dict) -> bool:
    """
    Send payment success confirmation email.
    """
    try:
        subject = "Payment Successful - Receipt Enclosed"
        
        # HTML Body
        html_body = f"""
        <html>
        <head>
            <style>
                body {{ font-family: 'Arial', sans-serif; line-height: 1.6; color: #333; }}
                .container {{ max-width: 600px; margin: 0 auto; padding: 20px; }}
                .header {{ background: linear-gradient(135deg, #10b981 0%, #059669 100%); color: white; padding: 30px; text-align: center; border-radius: 10px 10px 0 0; }}
                .content {{ background: #ecfdf5; padding: 30px; border-radius: 0 0 10px 10px; }}
                .receipt-box {{ background: white; border: 2px solid #10b981; padding: 25px; border-radius: 8px; margin: 20px 0; }}
                .amount-highlight {{ font-size: 32px; font-weight: bold; color: #10b981; text-align: center; margin: 20px 0; }}
                .footer {{ text-align: center; margin-top: 20px; color: #6b7280; font-size: 12px; }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Payment Successful!</h1>
                    <p>Thank you for your payment</p>
                </div>
                <div class="content">
                    <h2>Hello {payment_details.get('user_name', 'Customer')},</h2>
                    <p>Your payment has been processed successfully!</p>
                    
                    <div class="amount-highlight">${payment_details['amount']:.2f}</div>
                    
                    <div class="receipt-box">
                        <h3 style="margin-top: 0; text-align: center;">Payment Receipt</h3>
                        <hr style="border: none; border-top: 1px solid #e5e7eb; margin: 15px 0;">
                        <p><strong>Transaction ID:</strong> {payment_details.get('transaction_id', 'N/A')}</p>
                        <p><strong>Date & Time:</strong> {payment_details.get('payment_date', 'N/A')}</p>
                        <p><strong>Payment Method:</strong> {payment_details.get('payment_method', 'Card')}</p>
                        <p><strong>Booking ID:</strong> {payment_details.get('booking_id', 'N/A')}</p>
                        <p><strong>Amount Paid:</strong> ${payment_details['amount']:.2f}</p>
                        <p><strong>Status:</strong> <span style="color: #10b981; font-weight: bold;">PAID</span></p>
                    </div>
                    
                    <p>This email serves as your payment receipt. Please keep it for your records.</p>
                    <p>Your parking spot is now confirmed and ready for you!</p>
                </div>
                <div class="footer">
                    <p>ParkMyCar Systems</p>
                    <p>Safe travels!</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        text_body = f"""
ParkMyCar - Payment Successful

Hello {payment_details.get('user_name', 'Customer')},

Your payment has been processed successfully!

PAYMENT RECEIPT
================
Transaction ID: {payment_details.get('transaction_id', 'N/A')}
Date & Time: {payment_details.get('payment_date', 'N/A')}
Payment Method: {payment_details.get('payment_method', 'Card')}
Booking ID: {payment_details.get('booking_id', 'N/A')}
Amount Paid: ${payment_details['amount']:.2f}
Status: PAID

This email serves as your payment receipt. Please keep it for your records.

Your parking spot is now confirmed and ready for you!

---
ParkMyCar Systems
Safe travels!
        """

        return _send_email(email, subject, html_body, text_body)
        
    except Exception as e:
        logging.exception(f"Error sending payment success email: {e}")
        return False


def _send_email(email: str, subject: str, html_body: str, text_body: str) -> bool:
    """
    Helper function to send email via configured provider.
    """
    try:
        if EMAIL_PROVIDER == "gmail":
            import smtplib
            from email.mime.multipart import MIMEMultipart
            from email.mime.text import MIMEText
            
            if not GMAIL_SENDER_EMAIL or not GMAIL_APP_PASSWORD:
                logging.error("Gmail credentials not configured")
                return False
            
            message = MIMEMultipart('alternative')
            message['From'] = GMAIL_SENDER_EMAIL
            message['To'] = email
            message['Subject'] = subject
            
            message.attach(MIMEText(text_body, 'plain'))
            message.attach(MIMEText(html_body, 'html'))
            
            with smtplib.SMTP('smtp.gmail.com', 587) as server:
                server.starttls()
                server.login(GMAIL_SENDER_EMAIL, GMAIL_APP_PASSWORD)
                server.send_message(message)
            
            logging.info(f"Email sent to {email} via Gmail")
            return True
            
        elif EMAIL_PROVIDER == "ses":
            import boto3
            from botocore.exceptions import ClientError
            
            if not AWS_ACCESS_KEY_ID or not AWS_SECRET_ACCESS_KEY:
                logging.error("AWS credentials not configured")
                return False
            
            ses_client = boto3.client(
                'ses', 
                region_name=AWS_REGION,
                aws_access_key_id=AWS_ACCESS_KEY_ID, 
                aws_secret_access_key=AWS_SECRET_ACCESS_KEY
            )
            
            ses_client.send_email(
                Source=SES_SENDER_EMAIL,
                Destination={'ToAddresses': [email]},
                Message={
                    'Subject': {'Data': subject, 'Charset': 'UTF-8'},
                    'Body': {
                        'Text': {'Data': text_body, 'Charset': 'UTF-8'},
                        'Html': {'Data': html_body, 'Charset': 'UTF-8'}
                    }
                }
            )
            
            logging.info(f"Email sent to {email} via SES")
            return True
            
        else:
            # Console mode
            print("\n" + "="*60)
            print(f"EMAIL TO: {email}")
            print(f"SUBJECT: {subject}")
            print("-"*60)
            print(text_body)
            print("="*60 + "\n")
            return True
            
    except Exception as e:
        logging.exception(f"Error sending email: {e}")
        return False
