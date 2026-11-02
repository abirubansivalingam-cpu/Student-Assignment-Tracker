# Student Assignment Tracker (Taskwise)

A Django web application for students to organise assignments, due dates, priorities, completion status, and personal progress.

## Included features

- Student registration, sign-in, sign-out, and password change
- Per-student assignment ownership and data isolation
- Create, view, edit, delete, and mark assignments complete/reopen
- Priority levels: Low, Medium, High
- Dashboard totals for all, completed, pending, overdue, and upcoming (next 7 days)
- Completion progress percentage
- Student profile (institution, course, bio)
- CSV and PDF exports
- Responsive dashboard and forms
- 17 automated Django tests

## Requirements

- Python 3.11 or newer (use a version supported by your installed Django release)
- Windows 10/11, macOS, or Linux
- A web browser

SQLite is the default database, so PostgreSQL is not required for a fresh installation. PostgreSQL can be enabled using the optional `requirements-postgresql.txt` file and environment variables.

## Windows setup (Command Prompt)

Open CMD in the extracted project folder and run each command. On a machine without Python 3.14, replace `py -3.14` with `py` if that installed Python version is supported by the selected Django release:

```bat
py -3.14 -m venv .venv
.venv\Scripts\python.exe -m pip install --upgrade pip
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py check
.venv\Scripts\python.exe manage.py test assignments
.venv\Scripts\python.exe manage.py createsuperuser
.venv\Scripts\python.exe manage.py runserver
```

For a guided setup, double-click `start_project.bat`. Alternatively, run the commands above. Open http://127.0.0.1:8000/ and register a student account. The admin site is at http://127.0.0.1:8000/admin/.

> PowerShell note: if script execution blocks `Activate.ps1`, do not activate the environment. Run `.venv\Scripts\python.exe` exactly as shown above.

## Optional PostgreSQL setup

1. Install the PostgreSQL driver:

```bat
.venv\Scripts\python.exe -m pip install -r requirements-postgresql.txt
```

2. Set environment variables in the same CMD window, replacing the database credentials:

```bat
set DB_ENGINE=postgresql
set DB_NAME=student_assignment_db
set DB_USER=postgres
set DB_PASSWORD=YOUR_POSTGRES_PASSWORD
set DB_HOST=localhost
set DB_PORT=5432
```

3. Create the database in PostgreSQL, then run migrations:

```bat
.venv\Scripts\python.exe manage.py migrate
.venv\Scripts\python.exe manage.py runserver
```

## Main URLs

- `/` – sends signed-in users to the dashboard and others to sign-in
- `/register/` – student registration
- `/login/` – sign-in
- `/dashboard/` – student dashboard
- `/assignments/add/` – add an assignment
- `/profile/` – profile details
- `/password/change/` – password change
- `/exports/assignments.csv` – CSV export
- `/exports/assignments.pdf` – PDF export
- `/admin/` – Django administration

## Tests

Run:

```bat
.venv\Scripts\python.exe manage.py test assignments
```

The suite contains 17 tests covering account registration, authentication protection, assignment CRUD, ownership checks, dashboard calculations, profile updates, and CSV/PDF exports.

## Important deployment note

This package is configured for local development. Before deploying publicly, set a unique `DJANGO_SECRET_KEY`, set `DJANGO_DEBUG=0`, configure `DJANGO_ALLOWED_HOSTS`, enable HTTPS/security settings, and use a production WSGI/ASGI server. Do not commit database credentials or secret keys.

## Project structure

```text
config/                  Django project settings and URL configuration
assignments/              Application models, forms, views, migrations, and tests
templates/                HTML templates
static/css/               Responsive visual styles
manage.py                 Django command-line entry point
start_project.bat         Windows setup and launch helper
docs/                     Final project report and presentation
requirements.txt          Core dependencies
requirements-postgresql.txt Optional PostgreSQL driver
```

## Project author

Abiruban Sivalingam – Master of Computer Applications (MCA)
