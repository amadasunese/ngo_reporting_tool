# NGO Reporting Tool (Flask)

A lightweight NGO/M&E reporting tool with:
- Projects
- Strategic Objectives (SO1, SO2...)
- Indicators
- Activities (optional link to indicator)
- Attendance/Reach (Male/Female)
- Period reach report (by SO + by Indicator)

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Initialize DB (Flask-Migrate)

```bash
export FLASK_APP=app.py
flask db init
flask db migrate -m "init"
flask db upgrade
```

## Run

```bash
python app.py
```

Open:
- http://127.0.0.1:5000/

## CSRF (Flask-WTF)

CSRF protection is enabled globally using `CSRFProtect`.
All POST forms include a hidden `csrf_token`.
