#!/bin/bash

# 1. Run Migrations
python manage.py migrate

# 2. Create Superuser (only if it doesn't exist)
# Replace these values with your desired login info
export DJANGO_SUPERUSER_USERNAME=petarbuhchev
export DJANGO_SUPERUSER_PASSWORD=11012006pb
export DJANGO_SUPERUSER_EMAIL=petarbuhchev@outlook.om

# The "|| true" ensures the script doesn't crash if the user already exists
python manage.py createsuperuser --noinput || true

# 3. Collect Static Files
python manage.py collectstatic --noinput

# 4. Start the Server (with the performance fixes we discussed)
gunicorn --bind=0.0.0.0:8000 --workers 4 --timeout 600 salon_site.wsgi