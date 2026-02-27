# CLAUDE.md

## Project Overview

Document Manager - FastAPI web app for managing documents (PDF, DOCX, MD, TXT) with PostgreSQL, Jinja2 templates, Bootstrap 5.3.

## Key Commands

```bash
# Run locally (dev with reload)
source venv/bin/activate
RELOAD=true python run.py

# Run locally (production)
source venv/bin/activate
python run.py

# Docker
docker compose up -d --build

# Recreate DB tables (destructive - drops all data)
python -c "from app.database import engine; from app.models import Base; Base.metadata.drop_all(bind=engine); Base.metadata.create_all(bind=engine)"
```

## Architecture

- **Backend**: FastAPI + SQLAlchemy + Jinja2
- **DB**: PostgreSQL at 192.168.1.189, database `documents`, user `postgres`, password `dexxxx1`
- **Port**: 5214
- **Auth**: JWT in httponly cookie, bcrypt passwords
- **File storage**: SHA-256 hash as filename (no extension on disk), originals in DB
- **Config**: `app/config.py` reads from environment variables

## Project Structure

```
app/
  main.py           - FastAPI app, startup (creates admin user)
  config.py          - Settings from env vars
  database.py        - SQLAlchemy engine/session
  models.py          - User, UserSettings, Document
  auth.py            - JWT, password hashing, get_current_user dependency
  routes/
    auth_routes.py    - login, logout, change password
    user_routes.py    - admin user CRUD
    document_routes.py - documents, API, settings, edit metadata, viewers
  templates/          - Jinja2 (base, dashboard, upload, login, users, settings, change_password)
  static/             - Local CSS/JS/fonts (Bootstrap, Icons, Flatpickr)
uploads/              - Document files + thumbnails/
```

## Important Patterns

- **Diacritics-free search**: `unicodedata.normalize('NFKD', s)` - removes accents for Slovak text
- **Duplicate prevention**: SHA-256 content hash checked before upload
- **Theme**: Bootstrap 5.3 `data-bs-theme` set via cookie at page load (no flash)
- **Tile grid**: flexbox with fixed 144px tile width, not Bootstrap grid
- **File viewers**: PDF via iframe, MD/TXT/DOCX rendered to HTML via `/document/{id}/render`
- **bcrypt version**: pinned to 4.0.1 (passlib incompatible with bcrypt 5.x)

## Business Rules

- Admin can see all documents, manage users, but CANNOT upload
- Regular users see own + public documents
- Private documents visible only to uploader and admin
- Default admin: admin/admin (created on startup if not exists)
- No duplicate files (same SHA-256 = rejected)

## Common Tasks

### Add new file type support
1. Add extension to `ALLOWED_EXTENSIONS` in `document_routes.py`
2. Add icon mapping in `FILE_TYPE_ICONS` dict
3. Add rendering logic in `render_document()` route
4. Add option in dashboard `fileTypeFilter` select

### Modify tile appearance
- CSS in `app/static/css/style.css`
- Tile HTML in `renderDocuments()` JS function in `dashboard.html`

### Add new user setting
1. Add column to `UserSettings` in `models.py`
2. Add form field in `settings.html`
3. Handle in `save_settings()` route
4. Use via `get_user_settings()` where needed
