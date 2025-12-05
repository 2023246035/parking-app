# Gmail SMTP Setup Guide for Free OTP Email Sending

## Overview
This guide explains how to set up **FREE** email sending using Gmail SMTP for your ParkingApp's forgot password OTP feature.

## Prerequisites
- A Gmail account (free)
- Access to Google Account settings

## Step 1: Create Gmail App Password

### Important Notes:
- **DO NOT** use your regular Gmail password
- You need to create a special "App Password" for security
- 2-Step Verification must be enabled on your Google Account

### Instructions:

1. **Enable 2-Step Verification** (if not already enabled):
   - Go to https://myaccount.google.com/security
   - Find "2-Step Verification" and click it
   - Follow the prompts to set it up (usually with your phone number)

2. **Generate App Password**:
   - Go to https://myaccount.google.com/apppasswords
   - Or navigate: Google Account → Security → 2-Step Verification → App passwords
   - You may need to sign in again
   - Under "Select app", choose **"Mail"**
   - Under "Select device", choose **"Other (Custom name)"**
   - Enter a name like: "ParkingApp OTP"
   - Click **"Generate"**
   - Google will show you a 16-character password (example: `abcd efgh ijkl mnop`)
   - **Copy this password immediately** - you won't be able to see it again!

## Step 2: Update Your .env File

Open your `.env` file in the project root directory and add these lines:

```env
# Email Configuration - Use Gmail (FREE)
EMAIL_PROVIDER=gmail

# Gmail SMTP Settings
GMAIL_SENDER_EMAIL=your.email@gmail.com
GMAIL_APP_PASSWORD=abcdefghijklmnop
```

### Replace:
- `your.email@gmail.com` → Your actual Gmail address
- `abcdefghijklmnop` → The 16-character app password (remove spaces)

### Example:
```env
EMAIL_PROVIDER=gmail
GMAIL_SENDER_EMAIL=parkingapp2024@gmail.com
GMAIL_APP_PASSWORD=xmfp qwer tyui asdf
```

## Step 3: Restart Your Application

After updating the `.env` file, restart your Reflex application:

```bash
# Stop the current server (Ctrl+C)
# Then restart:
python -m reflex run
```

## Step 4: Test the Feature

1. Go to your app's login page
2. Click "Forgot Password?"
3. Enter an email address
4. Click "Send OTP"
5. Check the email inbox for the OTP code

## Troubleshooting

### "Authentication Failed" Error
- **Cause**: Wrong email or app password
- **Solution**: 
  - Double-check your email address in `.env`
  - Regenerate the app password and update `.env`
  - Make sure there are no spaces in the app password

### "Less Secure App Access" Message
- **Cause**: You used your regular password instead of app password
- **Solution**: Create and use an App Password (see Step 1)

### No Email Received
1. **Check spam folder** - sometimes OTP emails go to spam
2. **Verify email address** - make sure you entered it correctly
3. **Check app logs** - look for error messages in the terminal
4. **Gmail sending limits** - Gmail has daily limits (~500 emails/day for free accounts)

### Still Using Console Mode?
- Check that `EMAIL_PROVIDER=gmail` in your `.env` file
- Make sure the `.env` file is in the project root directory
- Restart the application after changing `.env`

## Security Best Practices

1. ✅ **Never commit .env to Git** - it contains sensitive credentials
2. ✅ **Use App Passwords** - never use your main Gmail password
3. ✅ **Revoke unused App Passwords** - go to https://myaccount.google.com/apppasswords
4. ✅ **Monitor usage** - check your Gmail sent folder occasionally

## Gmail Sending Limits (Free Account)

- **Per day**: ~500 emails
- **Per recipient**: Limited to prevent spam
- **Rate limiting**: If you hit limits, Gmail will temporarily block sending

For production apps with high volume, consider:
- Gmail Business/Workspace (paid, higher limits)
- AWS SES (already supported in the code)
- SendGrid, Mailgun, or other email services

## Email Template

The OTP email includes:
- Professional HTML design with gradient header
- Large, easy-to-read OTP code
- 2-minute expiration notice
- Security warning
- Both HTML and plain text versions (for compatibility)

## Switching Email Providers

To switch between providers, just change `EMAIL_PROVIDER` in `.env`:

```env
# For development/testing (no email sent, just console output):
EMAIL_PROVIDER=console

# For Gmail SMTP (FREE):
EMAIL_PROVIDER=gmail

# For AWS SES (requires AWS account):
EMAIL_PROVIDER=ses
```

## FAQ

**Q: Is Gmail SMTP really free?**
A: Yes! Gmail allows free SMTP access for personal use with reasonable limits.

**Q: Can I use a different email service?**
A: Yes! The code supports AWS SES. You can also add other SMTP providers similarly.

**Q: What if I don't have Gmail?**
A: You can create a free Gmail account at https://mail.google.com

**Q: Can I use my company/custom domain email?**
A: If your email uses Gmail/G Suite backend, yes. Otherwise, you'd need to add SMTP support for that provider.

## Support

If you encounter issues:
1. Check the application logs in your terminal
2. Verify all credentials in `.env`
3. Test with a different email address
4. Review the troubleshooting section above

---

**Last Updated**: December 2024
**Supported Email Providers**: Gmail SMTP, AWS SES, Console (dev mode)
