# Email Configuration - READ THIS FIRST!

## ✅ Your Email is Now Configured!

Your Gmail credentials have been set up:
- **Email:** skysalonskysalonandbeauty@gmail.com
- **Backend:** SMTP (real email sending)

## 🚀 How to Start the Server with Email

### Option 1: Use the Startup Script (Easiest)

**PowerShell:**
```powershell
.\start_server.ps1
```

**Command Prompt:**
```cmd
start_server.bat
```

### Option 2: Set Environment Variables Manually

**PowerShell:**
```powershell
$env:EMAIL_BACKEND="django.core.mail.backends.smtp.EmailBackend"
$env:EMAIL_HOST_USER="skysalonskysalonandbeauty@gmail.com"
$env:EMAIL_HOST_PASSWORD="hzhhonfipyjukuf"
$env:DEFAULT_FROM_EMAIL="skysalonskysalonandbeauty@gmail.com"

python manage.py runserver
```

**Command Prompt:**
```cmd
set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
set EMAIL_HOST_USER=skysalonskysalonandbeauty@gmail.com
set EMAIL_HOST_PASSWORD=hzhhonfipyjukuf
set DEFAULT_FROM_EMAIL=skysalonskysalonandbeauty@gmail.com

python manage.py runserver
```

## ⚠️ IMPORTANT

- **You MUST set these environment variables BEFORE starting the server**
- If you start the server without setting them, emails won't work
- Use the startup scripts (`start_server.ps1` or `start_server.bat`) to make it easy

## 🧪 Test Email

After starting the server with email configured:

1. **Create a booking** with an email address
2. **Check the email inbox** (and spam folder)
3. **Or run the test script:**
   ```bash
   python test_email_now.py
   ```

## ✅ Verify It's Working

Check the email backend:
```powershell
python manage.py shell -c "from django.conf import settings; print('EMAIL_BACKEND:', settings.EMAIL_BACKEND)"
```

**Should show:** `django.core.mail.backends.smtp.EmailBackend`

**If it shows:** `django.core.mail.backends.console.EmailBackend` - you didn't set the environment variables before starting the server.

## 📧 What Happens Now

When someone makes a booking with an email address:
1. ✅ Booking is saved
2. ✅ Confirmation email is sent to their email
3. ✅ Email includes a cancellation link
4. ✅ They can cancel their booking via the link

---

**Remember:** Always use `start_server.ps1` or `start_server.bat` to start the server, or set the environment variables manually first!



