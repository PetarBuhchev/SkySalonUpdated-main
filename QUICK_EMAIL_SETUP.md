# Quick Email Setup - Fix "Emails Not Sending" Issue

## Problem
Emails work in the test script but not when booking from the website. This is because the Django server is using the **console email backend** which just prints emails to the console instead of sending them.

## Solution

You need to set environment variables **before starting the Django server**. Here's how:

### Option 1: PowerShell (Recommended for Windows)

1. **Set environment variables:**
   ```powershell
   $env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
   $env:EMAIL_HOST_USER="your-email@gmail.com"
   $env:EMAIL_HOST_PASSWORD="your-16-char-app-password"
   $env:DEFAULT_FROM_EMAIL="your-email@gmail.com"
   ```

2. **Then start the server:**
   ```powershell
   python manage.py runserver
   ```

### Option 2: Use the Setup Script

Run the PowerShell setup script:
```powershell
.\setup_email_windows.ps1
```

Then start the server in the **same PowerShell window**:
```powershell
python manage.py runserver
```

### Option 3: Create a .env file (Persistent)

1. **Install python-dotenv:**
   ```bash
   pip install python-dotenv
   ```

2. **Create a `.env` file** in the project root:
   ```
   EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
   EMAIL_HOST_USER=your-email@gmail.com
   EMAIL_HOST_PASSWORD=your-16-char-app-password
   DEFAULT_FROM_EMAIL=your-email@gmail.com
   ```

3. **Start the server:**
   ```bash
   python manage.py runserver
   ```

## Verify It's Working

After setting the environment variables, check the email backend:

```powershell
python manage.py shell -c "from django.conf import settings; print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)"
```

You should see:
```
EMAIL_BACKEND: django.core.mail.backends.smtp.EmailBackend
```

If you see `console.EmailBackend`, the environment variables aren't set correctly.

## Important Notes

- **Environment variables must be set BEFORE starting the server**
- If you close the terminal/restart the server, you need to set them again (unless using .env file)
- The test script works because it sets variables when it runs
- The Django server needs variables set in the same session where you start it

## Getting Gmail App Password

1. Go to https://myaccount.google.com/security
2. Enable 2-Step Verification
3. Go to "App passwords"
4. Generate one for "Mail"
5. Copy the 16-character password




