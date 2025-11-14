# Core Django Starter

This repository now ships a lightweight Django starter configured with a `core_project` site and a default `main_app` that exposes a `/ping` health-check endpoint. It is meant to demonstrate how to provision Django in the Codex execution environment with SQLite, migrations, and app registration pre-wired.

## Requirements
- Python 3.11+
- `pip`
- Internet access (or an alternate package source) to install Django 5.x and its dependencies.

## Initial setup
```bash
python -m venv .venv
source .venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt  # installs Django and supporting libraries
python manage.py migrate         # applies initial SQLite migrations
python manage.py runserver 0.0.0.0:8000
```

> **Note:** If your environment restricts access to PyPI, provide a local wheelhouse or mirror so `pip install -r requirements.txt` can succeed.

## Project layout
```
core_project/
    __init__.py
    asgi.py
    settings.py
    urls.py
    wsgi.py
main_app/
    __init__.py
    admin.py
    apps.py
    migrations/
    models.py
    urls.py
    views.py
manage.py
requirements.txt
```

### Settings highlights
- `INSTALLED_APPS` already includes `main_app` alongside the default Django contrib apps.
- SQLite is the default database via `db.sqlite3` at the repository root.
- `ALLOWED_HOSTS` is set to `"*"` for convenience during local development; tighten this before deploying.

## Default routes
| Method | Path   | Description         |
| ------ | ------ | ------------------- |
| GET    | `/ping` | Health check; returns `{ "message": "pong" }` |

The `ping` view lives in `main_app/views.py` and is wired through `main_app/urls.py`, which is then included by `core_project/urls.py`.

## Running checks & migrations
Once Django is installed, you can run:
```bash
python manage.py check
python manage.py migrate
```

These commands ensure the settings are valid and that the SQLite schema is up to date.

## Extending the starter
- Add models to `main_app/models.py` and run `python manage.py makemigrations main_app` to create migrations.
- Register new URL patterns inside `main_app/urls.py` or add additional apps and include their URL configs from `core_project/urls.py`.
- Swap SQLite for Postgres or another backend by editing the `DATABASES` block in `core_project/settings.py`.

This scaffold provides a clean baseline for building out the vendor-management functionality or any other Django-based service.
