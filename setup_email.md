# Email Setup Guide for Gmail

This guide will help you configure Gmail to send booking confirmation emails.

## Step 1: Enable 2-Step Verification

1. Go to your Google Account: https://myaccount.google.com/
2. Click on **Security** in the left sidebar
3. Under "Signing in to Google", find **2-Step Verification**
4. Follow the prompts to enable 2-Step Verification (if not already enabled)

## Step 2: Generate an App Password

1. Go back to **Security** settings
2. Under "Signing in to Google", find **App passwords** (you may need to search for it)
3. If you don't see "App passwords", make sure 2-Step Verification is enabled first
4. Click on **App passwords**
5. Select **Mail** as the app
6. Select **Other (Custom name)** as the device
7. Enter "Django Salon Booking" as the name
8. Click **Generate**
9. **Copy the 16-character password** (it will look like: `abcd efgh ijkl mnop`)

## Step 3: Configure Environment Variables

### Option A: Using .env file (Recommended)

1. Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```

2. Edit `.env` and add your Gmail credentials:
   ```
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

3. Install python-dotenv to load .env file:
   ```bash
   pip install python-dotenv
   ```

4. Update `salon_site/settings.py` to load .env file (see below)

### Option B: Set Environment Variables Directly

**Windows PowerShell:**
```powershell
$env:EMAIL_HOST_USER="your-email@gmail.com"
$env:EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"
$env:DEFAULT_FROM_EMAIL="your-email@gmail.com"
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
```

**Windows Command Prompt:**
```cmd
set EMAIL_HOST_USER=your-email@gmail.com
set EMAIL_HOST_PASSWORD=abcd efgh ijkl mnop
set DEFAULT_FROM_EMAIL=your-email@gmail.com
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
```

**Linux/Mac:**
```bash
export EMAIL_HOST_USER="your-email@gmail.com"
export EMAIL_HOST_PASSWORD="abcd efgh ijkl mnop"
export DEFAULT_FROM_EMAIL="your-email@gmail.com"
export EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
```

## Step 4: Test Email Configuration

Run the Django development server:
```bash
python manage.py runserver
```

Create a test booking with an email address. You should receive a confirmation email!

## Troubleshooting

### "Authentication failed" error
- Make sure you're using an **App Password**, not your regular Gmail password
- Verify 2-Step Verification is enabled
- Check that the App Password was copied correctly (no spaces needed)

### "Less secure app access" error
- Gmail no longer supports "less secure apps"
- You **must** use App Passwords with 2-Step Verification enabled

### Emails not sending
- Check that `EMAIL_BACKEND` is set to `django.core.mail.backends.smtp.EmailBackend`
- Verify `EMAIL_USE_TLS=1` is set
- Check the Django logs in `logs/app.log` for error messages




