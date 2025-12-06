
from dotenv import load_dotenv
import os
import smtplib
from email.mime.text import MIMEText

# Load env vars
load_dotenv()

email = os.getenv("GMAIL_SENDER_EMAIL")
password = os.getenv("GMAIL_APP_PASSWORD")
provider = os.getenv("EMAIL_PROVIDER")

print(f"Provider: {provider}")
print(f"Email: {email}")
print(f"Password Check: {'Found' if password else 'Missing'} ({len(password) if password else 0} chars)")

if provider != 'gmail':
    print("Provider is not gmail. Skipping test.")
    exit()

if not email or not password:
    print("Missing credentials.")
    exit()

try:
    print("Attempting connection to smtp.gmail.com:587...")
    server = smtplib.SMTP('smtp.gmail.com', 587)
    server.starttls()
    print("Logging in...")
    server.login(email, password)
    print("[SUCCESS] Login successful!")
    server.quit()
except Exception as e:
    print(f"[FAILED] {e}")
    exit(1)
