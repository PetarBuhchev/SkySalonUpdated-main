# Email Setup Instructions - Quick Guide

## Current Status
Your email is currently set to **console mode**, which means emails are printed to the console instead of being sent.

## Quick Fix (Choose One Method)

### Method 1: Use the Setup Script (Easiest)

1. **Run the PowerShell script:**
   ```powershell
   .\set_email_credentials.ps1
   ```

2. **Follow the prompts:**
   - Enter your Gmail address
   - Enter your Gmail App Password (see below if you don't have one)

3. **Restart your Django server**

### Method 2: Manual Setup with .env File

1. **Get your Gmail App Password** (see instructions below)

2. **Create a `.env` file** in the project root with:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

3. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

4. **Restart your Django server**

### Method 3: Set Environment Variables (Temporary)

**Before starting the server**, run in PowerShell:
```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="your-16-char-app-password"
$env:DEFAULT_FROM_EMAIL="your-email@gmail.com"

# Then start server
python manage.py runserver
```

**Note:** This only works for the current terminal session. Use Method 1 or 2 for permanent setup.

---

## How to Get Gmail App Password

### You Need:
1. **Gmail account**
2. **2-Step Verification enabled**
3. **App Password** (16 characters)

### Steps:

1. **Go to Google Account Security:**
   - Visit: https://myaccount.google.com/security

2. **Enable 2-Step Verification** (if not already):
   - Find "2-Step Verification" under "Signing in to Google"
   - Follow the prompts to enable it

3. **Generate App Password:**
   - On the same Security page, find "App passwords"
   - Click "App passwords"
   - Select "Mail" as the app
   - Select "Other (Custom name)" as device
   - Enter "Django Salon" as the name
   - Click "Generate"
   - **Copy the 16-character password** (looks like: `abcd efgh ijkl mnop`)

4. **Use the App Password:**
   - Use this 16-character password (remove spaces)
   - **NOT your regular Gmail password**

---

## Verify It's Working

After setup, check the email backend:

```powershell
python manage.py shell -c "from django.conf import settings; print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)"
```

**Should show:** `django.core.mail.backends.smtp.EmailBackend`

**If it shows:** `django.core.mail.backends.console.EmailBackend` - the setup didn't work, try again.

---

## Test Email

1. **Create a test booking** with an email address
2. **Check your email** (and spam folder)
3. **Or run the test script:**
   ```bash
   python test_email.py
   ```

---

## Troubleshooting

### "Authentication failed"
- Make sure you're using an **App Password**, not your regular password
- Verify 2-Step Verification is enabled
- Check that the password was copied correctly (16 characters, no spaces)

### "Still using console backend"
- Make sure you **restarted the Django server** after setting up
- Check that `.env` file exists and has correct values
- Verify `python-dotenv` is installed: `pip install python-dotenv`

### "Emails not arriving"
- Check spam folder
- Verify the email address is correct
- Check Django logs: `logs/app.log`
- Make sure EMAIL_BACKEND is set to SMTP (not console)

---

## Need Help?

If you provide me with:
1. Your Gmail address
2. Your Gmail App Password

I can help you set it up directly!




