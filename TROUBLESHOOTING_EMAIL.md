# Email Troubleshooting

## Authentication Error

If you're getting an authentication error, check these:

### 1. Verify App Password Format
The App Password should be **16 characters**. It might have spaces in it like: `hzhh onfi pyju kuf`

**Try both formats:**
- With spaces: `hzhh onfi pyju kuf`
- Without spaces: `hzhhonfipyjukuf`

### 2. Regenerate App Password
If authentication fails, the App Password might be incorrect:

1. Go to: https://myaccount.google.com/security
2. Click "App passwords"
3. Delete the old "Django Salon" password
4. Generate a new one
5. Copy the new 16-character password
6. Update `start_server.ps1` or `start_server.bat` with the new password

### 3. Verify 2-Step Verification
Make sure 2-Step Verification is enabled:
- Go to: https://myaccount.google.com/security
- Check that "2-Step Verification" shows as "On"

### 4. Check Gmail Account
- Make sure you can log into: skysalonskysalonandbeauty@gmail.com
- Verify the account is active and not locked

## Update Password in Scripts

If you get a new App Password, update these files:

**start_server.ps1** - Line with `$env:EMAIL_HOST_PASSWORD`
**start_server.bat** - Line with `set EMAIL_HOST_PASSWORD`

## Test Again

After updating, restart the server and test:
```powershell
.\start_server.ps1
```

Then create a test booking with an email address.



