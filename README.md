# Training & Placement Cell Management System

This refactor converts the original single-file Flask app into a modular, production-style Flask project.

## Folder Structure

```text
project/
├── app/
│   ├── __init__.py              # App factory, extension setup, blueprint registration
│   ├── extensions.py            # SQLAlchemy, Flask-Login, CSRF, bcrypt
│   ├── decorators/              # RBAC decorators
│   ├── errors/                  # Error handlers
│   ├── forms/                   # Flask-WTF validation forms
│   ├── models/                  # SQLAlchemy ORM models
│   ├── routes/                  # Blueprints by role/module
│   ├── services/                # Business logic
│   ├── static/css/              # App CSS
│   ├── templates/
│   │   ├── admin/
│   │   ├── auth/
│   │   ├── company/
│   │   ├── layouts/
│   │   ├── student/
│   │   └── tpo/
│   └── utils/                   # Upload helpers
├── config.py                    # Environment-based config
├── run.py                       # Main entrypoint
├── app.py                       # Compatibility entrypoint
├── requirements.txt
└── .env                         # Local environment values
```

## Setup

```powershell
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
flask --app run.py init-db
flask --app run.py upgrade-db
flask --app run.py create-admin
flask --app run.py create-tpo
flask --app run.py run
```

Set `ADMIN_USERNAME`, `ADMIN_EMAIL`, `ADMIN_PASSWORD`, `TPO_USERNAME`, `TPO_EMAIL`, and `TPO_PASSWORD` in `.env` before running the account creation commands.

If you are using the old raw-SQL database, run `flask --app run.py upgrade-db` after `init-db`. `create_all()` does not alter existing MySQL tables, so this command adds the missing ORM columns and copies legacy values.

## Architecture Decisions

Blueprints separate auth, student, admin, TPO, and main routes so each module owns a small routing surface. The app factory in `app/__init__.py` makes configuration, testing, and deployment cleaner than global app initialization.

SQLAlchemy models replace raw SQL. This prevents SQL injection by using parameterized ORM queries, gives clear relationships, and removes tuple-index template access.

Flask-Login stores the authenticated user in a controlled session. Role decorators (`admin_required`, `student_required`, `tpo_required`) combine `login_required` with a role check, blocking direct URL access and privilege escalation.

Flask-WTF provides validation and CSRF protection. All state-changing operations use POST forms with CSRF tokens, including application approval, rejection, selection, logout, and student apply actions.

Services hold business rules such as eligibility checks, duplicate-application prevention, already-placed student restrictions, interview scheduling, and notification creation. Routes stay short and easier to reason about.

Templates inherit from shared layouts. `layouts/base.html` defines assets, `layouts/auth.html` handles login/registration cards, and `layouts/dashboard.html` provides the sidebar shell. Role-specific sidebar partials remove repeated HTML.

Uploads are restricted to PDFs, renamed with UUIDs, passed through `secure_filename`, and capped by `MAX_CONTENT_LENGTH`.

## ORM Relationships

`User` stores login credentials and role. A student user has one `StudentProfile`.

`Company` has many `PlacementDrive` records. A drive has many `Application` records.

`StudentProfile` has many `Application` records. Each application belongs to one drive and can have many interviews.

`Notification` belongs to a student `User`, so messages remain tied to the authenticated account.

## Authentication and RBAC Flow

Students register through `/register`, then log in through `/login`. Admin and TPO accounts are created through CLI commands, not public forms. Each login route only accepts users with the correct role.

After login, Flask-Login loads the user by ID. Dashboard routes call the relevant decorator. If the role does not match, the request returns `403`.

## Blueprint Routing Flow

`run.py` calls `create_app()`. The app factory initializes extensions, registers Blueprints, error handlers, CLI commands, and logging. Each Blueprint contributes routes:

- `auth`: register, login, logout
- `student`: dashboard, profile, resume upload, drives, applications, notifications, interviews
- `admin`: dashboard, student management, reports
- `tpo`: dashboard, drive creation, applications, approvals, interview scheduling
- `main`: home redirect

## Security Improvements

Secrets and DB credentials now come from `.env`. Passwords use bcrypt. CSRF protection is enabled. RBAC blocks unauthorized dashboards. Admin/TPO accounts are not created from public routes. SQL injection risk is reduced through ORM queries. File upload validation accepts PDFs only. Duplicate applications are blocked with both service logic and a database uniqueness constraint.
