# Sky Salon and Beauty

A Django-based booking site with staff portfolios and a calendar for direct booking.

## Requirements
- Python 3.10+
- pip
- Git (for version control)

## Setup
```bash
python -m venv .venv
. .venv/Scripts/activate  # Windows PowerShell
pip install -r requirements.txt  # If not present, see below
```

If `requirements.txt` is not present, install minimal deps:
```bash
pip install django==5.0.6 pillow==10.3.0
```

## Run
```bash
python manage.py migrate
python manage.py runserver
```
Open `http://127.0.0.1:8000/`.

## Admin (optional)
```bash
python manage.py createsuperuser
```

## Git & GitHub
1. Initialize:
```bash
git init
git add .
git commit -m "Initial commit"
```
2. Create an empty repo on GitHub.
3. Push:
```bash
git branch -M main
git remote add origin https://github.com/<your-user>/<your-repo>.git
git push -u origin main
```

## Notes
- `.gitignore` excludes `db.sqlite3`, `media/`, envs, and editor files.
- Calendar prevents past dates; click a slot to prefill booking.
- Worker pages live at `/workers/<id>/`.


