"""
Interactive script to set up Gmail email configuration.
This will help you configure email step by step.
"""
import os
import sys

print("=" * 60)
print("Gmail Email Setup for Django Salon Booking")
print("=" * 60)
print()

# Step 1: Get Gmail address
print("Step 1: Gmail Address")
print("-" * 60)
email = input("Enter your Gmail address (e.g., yourname@gmail.com): ").strip()

if not email or "@gmail.com" not in email.lower():
    print("ERROR: Please enter a valid Gmail address.")
    sys.exit(1)

print()
print("Step 2: Gmail App Password")
print("-" * 60)
print("IMPORTANT: You need a Gmail App Password, NOT your regular password!")
print()
print("To get an App Password:")
print("1. Go to: https://myaccount.google.com/security")
print("2. Make sure '2-Step Verification' is enabled")
print("3. Scroll down to 'App passwords'")
print("4. Click 'App passwords'")
print("5. Select 'Mail' as the app")
print("6. Select 'Other (Custom name)' as device")
print("7. Enter 'Django Salon' as the name")
print("8. Click 'Generate'")
print("9. Copy the 16-character password (it looks like: abcd efgh ijkl mnop)")
print()
app_password = input("Enter your Gmail App Password (16 characters): ").strip()

# Remove spaces if user included them
app_password = app_password.replace(" ", "")

if len(app_password) != 16:
    print(f"WARNING: App password should be 16 characters, you entered {len(app_password)}")
    confirm = input("Continue anyway? (y/n): ").strip().lower()
    if confirm != 'y':
        sys.exit(1)

print()
print("Step 3: Configuration")
print("-" * 60)

# Create .env file content
env_content = f"""# Gmail Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=1
EMAIL_HOST_USER={email}
EMAIL_HOST_PASSWORD={app_password}
DEFAULT_FROM_EMAIL={email}
"""

# Write to .env file
env_file = ".env"
try:
    with open(env_file, "w") as f:
        f.write(env_content)
    print(f"✓ Configuration saved to {env_file}")
except Exception as e:
    print(f"ERROR: Could not write to {env_file}: {e}")
    sys.exit(1)

print()
print("Step 4: Install python-dotenv (if not already installed)")
print("-" * 60)
print("Installing python-dotenv...")
os.system("pip install python-dotenv -q")

print()
print("=" * 60)
print("Setup Complete!")
print("=" * 60)
print()
print("Your email configuration has been saved to .env file.")
print()
print("To use it:")
print("1. Make sure python-dotenv is installed: pip install python-dotenv")
print("2. Restart your Django server")
print("3. The settings will automatically load from .env")
print()
print("To test email sending, run:")
print("  python test_email.py")
print()
print("Or create a test booking with an email address.")
print()




