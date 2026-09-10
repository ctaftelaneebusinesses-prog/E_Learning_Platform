# Craftlanee E-Learning Platform — Developer Setup & Deployment Guide

> How to get the project running locally, from a clean machine to a working dev server.

---

## Table of Contents

1. [Prerequisites](#1-prerequisites)
2. [Get the Code](#2-get-the-code)
3. [Create a Virtual Environment](#3-create-a-virtual-environment)
4. [Install Dependencies](#4-install-dependencies)
5. [Set Up MySQL](#5-set-up-mysql)
6. [Configure Environment Variables (.env)](#6-configure-environment-variables-env)
7. [Run Migrations](#7-run-migrations)
8. [Create an Admin (Superuser) Account](#8-create-an-admin-superuser-account)
9. [Run the Development Server](#9-run-the-development-server)
10. [First Login & Role Approval Workflow](#10-first-login--role-approval-workflow)
11. [Project Structure at a Glance](#11-project-structure-at-a-glance)
12. [Everyday Developer Commands](#12-everyday-developer-commands)
13. [Troubleshooting](#13-troubleshooting)
14. [Production Deployment Notes](#14-production-deployment-notes)

---

## 1. Prerequisites

Install the following on your machine before you start:

| Tool | Version / Notes |
|---|---|
| Python | 3.12+ (project developed against Python 3.12) |
| MySQL Server | 8.0+ (or MariaDB equivalent) — the app connects via PyMySQL |
| Git | Any recent version, to clone/pull the repository |
| pip | Comes with Python — used to install dependencies from `requirements.txt` |
| VS Code | Recommended editor (not required) |

> **Tip:** On Windows, MySQL Workbench or the MySQL installer's bundled command-line client makes step 5 easier.

---

## 2. Get the Code

Clone the repository (or copy the project folder if it isn't in Git yet), then move into the Django project directory — the one containing `manage.py`:

```bash
git clone <repository-url> E_Learning_Platform
cd E_Learning_Platform
```

If you already have the folder locally, just open VS Code in the `E_Learning_Platform` directory (the one next to `manage.py`, `requirements.txt` and the `Procfile`) — that's your project root from here on.

---

## 3. Create a Virtual Environment

Keep this project's dependencies isolated from the rest of your system:

```bash
python -m venv venv
```

Activate it:

```bash
venv\Scripts\activate        # Windows (PowerShell / cmd)
source venv/bin/activate     # macOS / Linux
```

Your terminal prompt should now be prefixed with `(venv)`. In VS Code, select this interpreter via **Ctrl+Shift+P → Python: Select Interpreter → venv**.

---

## 4. Install Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

This installs Django, django-allauth, PyMySQL, ReportLab, openpyxl, Pillow, gunicorn, whitenoise and the rest of the stack listed in `requirements.txt`.

---

## 5. Set Up MySQL

Create an empty database for the project. From a MySQL client:

```sql
CREATE DATABASE e_learning_platform CHARACTER SET utf8mb4;
```

You can name it anything — just make sure the name matches the `DB_NAME` value you set in the `.env` file in the next step. The project does **not** create the database for you; it only creates the tables inside it via migrations.

---

## 6. Configure Environment Variables (.env)

Create a file named `.env` in the project root (same folder as `manage.py`). This file is **git-ignored and must never be committed**. Settings are read via `python-dotenv`, so anything defined here is picked up automatically.

| Variable | Purpose | Example / Default |
|---|---|---|
| `SECRET_KEY` | Django cryptographic signing key | a long random string |
| `DEBUG` | Enables verbose error pages in dev | `True` |
| `ALLOWED_HOSTS` | Comma-separated hostnames the app will serve | blank is fine locally — `localhost`/`127.0.0.1` are auto-added when `DEBUG=True` |
| `DB_NAME` | MySQL database name | `e_learning_platform` |
| `DB_USER` | MySQL username | `root` |
| `DB_PASSWORD` | MySQL password | `your_mysql_password` |
| `DB_HOST` | MySQL host | `localhost` |
| `DB_PORT` | MySQL port | `3306` |
| `OPENROUTER_API_KEY` | Powers the AI Mentor chatbot & AI learning-path suggestions | get a key at openrouter.ai |
| `GOOGLE_CLIENT_ID` | Google OAuth login (django-allauth) | from Google Cloud Console |
| `GOOGLE_CLIENT_SECRET` | Google OAuth login (django-allauth) | from Google Cloud Console |

Minimal working `.env` for local development:

```env
SECRET_KEY=dev-secret-key-change-me
DEBUG=True
DB_NAME=e_learning_platform
DB_USER=root
DB_PASSWORD=your_mysql_password
DB_HOST=localhost
DB_PORT=3306
OPENROUTER_API_KEY=
GOOGLE_CLIENT_ID=
GOOGLE_CLIENT_SECRET=
```

> **Tip:** The app will still start with `OPENROUTER_API_KEY` and the Google keys left blank — you just won't be able to use the AI Mentor or "Continue with Google" until they're filled in.

---

## 7. Run Migrations

Build the database schema (tables for users, courses, quizzes, certificates, chat, etc.):

```bash
python manage.py migrate
```

---

## 8. Create an Admin (Superuser) Account

This gives you access to Django's built-in `/admin/` panel, useful for inspecting data directly:

```bash
python manage.py createsuperuser
```

Follow the prompts for username, email and password.

---

## 9. Run the Development Server

```bash
python manage.py runserver
```

The app will be available at:

```
http://127.0.0.1:8000/
```

Static files (CSS/JS/images) are served automatically in dev mode — you don't need to run `collectstatic` locally; that step is only required for production (see [section 14](#14-production-deployment-notes)).

---

## 10. First Login & Role Approval Workflow

Understanding the account/role system will save confusion the first time you sign up:

1. Go to the **Register** page and create an account, choosing a role (Student or Instructor).
2. New Student/Instructor accounts start in a **PENDING** approval state and cannot access the full dashboard yet.
3. Log into `/admin/` with the superuser you created, or use the Admin dashboard (once an ADMIN-role profile exists) to approve the pending account.
4. To make your own account an Admin, the simplest path is: log into `/admin/`, find your `Profile` record (under `accounts`), and set `role` to `ADMIN` and `approval_status` to `APPROVED` directly.
5. Once approved, log in again — you'll land on the role-appropriate dashboard (Student / Instructor / Admin).

> **Note:** A brand-new profile is also routed through an onboarding flow (age group / theme selection) before it can reach the dashboard — this is enforced by `ProfileCompletionMiddleware`.

---

## 11. Project Structure at a Glance

| App / Folder | What it's for |
|---|---|
| `accounts` | Auth, roles, profiles, approval workflow, onboarding |
| `courses` | Core domain: courses, lessons, quizzes, enrollment, progress, chat, certificates |
| `students` | Student dashboard, catalogue, quiz-taking, certificate download, AI learning path |
| `instructors` | Instructor dashboard: course/lesson/quiz authoring, student analytics |
| `adminpanel` | Admin dashboard: approvals, CRUD, analytics, Excel export |
| `mentor_ai` | AI Mentor chatbot (OpenRouter) |
| `career` | Job-role / skill-readiness matching |
| `messaging` | Admin broadcast announcements |
| `utils` | Shared helpers (e.g. Excel activity logging) |
| `elearning_platform` | Django project settings, root URLs, WSGI entry point |
| `templates` | Shared/base HTML templates |
| `static` | CSS, JS, images (source files) |
| `media` | User-uploaded files (profile/course/lesson images, chat attachments) |
| `manage.py` | Django's command-line entry point |
| `requirements.txt` | Python dependency list |
| `Procfile` | Production start command (see [section 14](#14-production-deployment-notes)) |

---

## 12. Everyday Developer Commands

| Command | What it does |
|---|---|
| `python manage.py runserver` | Start the local dev server |
| `python manage.py makemigrations` | Generate migration files after changing `models.py` |
| `python manage.py migrate` | Apply migrations to the database |
| `python manage.py createsuperuser` | Create a Django admin user |
| `python manage.py shell` | Open an interactive Python shell with Django loaded |
| `python manage.py collectstatic` | Gather static files into `staticfiles/` (production only) |
| `pip freeze > requirements.txt` | Update the dependency list after installing a new package |

---

## 13. Troubleshooting

**`django.db.utils.OperationalError: (2002, ...) can't connect to MySQL server`**
- Make sure MySQL is installed and the service is running
- Double-check `DB_HOST`/`DB_PORT` in `.env` match your MySQL instance

**`Access denied for user ... (using password: YES/NO)`**
- `DB_USER`/`DB_PASSWORD` in `.env` don't match a valid MySQL account, or the account lacks privileges on the database

**`Unknown database 'e_learning_platform'`**
- You skipped [section 5](#5-set-up-mysql) — create the database in MySQL first; migrations only create tables, not the database itself

**`ModuleNotFoundError` after pulling new changes**
- A new dependency was added — re-run `pip install -r requirements.txt` inside your activated venv

**Static files / images not loading**
- In dev (`DEBUG=True`) this should work out of the box; if it doesn't, confirm you're running `runserver` from inside the `E_Learning_Platform` folder

**AI Mentor chatbot not responding**
- `OPENROUTER_API_KEY` is missing or invalid in `.env` — the rest of the app works fine without it

---

## 14. Production Deployment Notes

The project ships with a `Procfile`, which is how it's deployed (Railway/Heroku-style, process-based hosting):

```
web: python manage.py migrate --noinput && python manage.py collectstatic --noinput && gunicorn elearning_platform.wsgi --bind 0.0.0.0:$PORT --log-file -
```

On deploy, this automatically: applies any pending migrations, gathers static files for WhiteNoise to serve, then starts the app under Gunicorn.

Additional environment variables used only in production:

- `DEBUG=False` — never run production with DEBUG on
- `ALLOWED_HOSTS` — comma-separated list of your real domain(s)
- `RAILWAY_PUBLIC_DOMAIN` — auto-detected and appended to `ALLOWED_HOSTS` on Railway
- All the `DB_*` and API key variables from [section 6](#6-configure-environment-variables-env), set to production values

> **Note:** Static files are served directly by WhiteNoise (no separate CDN needed) and uploaded media is stored on local disk — for a multi-instance production deployment, moving media storage to cloud object storage (e.g. S3) is recommended.
