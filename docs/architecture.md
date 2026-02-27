# Architecture

**Author:** krse

## Overview

Document Manager is a FastAPI web application for managing documents (PDF, DOCX, Markdown, TXT) with user authentication, metadata management, search/filter, and a tile-based UI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Auth | JWT (python-jose) in httponly cookies |
| Password hashing | passlib + bcrypt |
| Templates | Jinja2 + Bootstrap 5.3 |
| PDF processing | PyMuPDF (thumbnail generation) |
| DOCX processing | python-docx (HTML rendering) |
| Markdown | markdown (HTML rendering) |
| Deployment | Docker / Docker Compose |

## Project Structure

```
/opt/apps/document-manager/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, startup, router mounting
│   ├── config.py             # Settings from env vars (DB, secret, upload path)
│   ├── database.py           # SQLAlchemy engine, session factory
│   ├── models.py             # User, UserSettings, Document ORM models
│   ├── schemas.py            # Pydantic schemas
│   ├── auth.py               # JWT, password hashing, auth dependencies
│   ├── routes/
│   │   ├── auth_routes.py    # Login, logout, change password
│   │   ├── user_routes.py    # Admin user management (CRUD)
│   │   └── document_routes.py # Documents, settings, edit metadata
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Layout, navbar, theme support
│   │   ├── login.html
│   │   ├── dashboard.html    # Tile grid, search, modals (view + edit)
│   │   ├── upload.html
│   │   ├── users.html        # Admin user management
│   │   ├── settings.html     # User preferences
│   │   └── change_password.html
│   └── static/
│       ├── css/              # Bootstrap, Bootstrap Icons, Flatpickr, custom
│       ├── js/               # Bootstrap, Flatpickr + SK locale
│       └── fonts/            # Bootstrap Icons woff/woff2
├── uploads/                  # Document storage (SHA-256 hash filenames)
│   └── thumbnails/           # PDF page thumbnails (PNG)
├── docs/
├── requirements.txt
├── run.py                    # Uvicorn entry point
├── Dockerfile
├── docker-compose.yml
└── CLAUDE.md
```

## File Storage

Documents are stored on disk using their **SHA-256 content hash** as filename (no extension). This:
- Prevents duplicate files (same content = same hash)
- Decouples storage from original filenames
- Original filename, extension stored in DB

## Authentication Flow

1. User submits credentials to `/login`
2. Server validates, creates JWT token
3. Token stored in httponly cookie (`access_token`)
4. Theme preference stored in regular cookie (`theme`)
5. All protected routes use `get_current_user` dependency
6. On failure, redirect to `/login`

## Access Control

| Role | Can Upload | Sees Documents | Can Delete | Manage Users |
|------|-----------|----------------|------------|-------------|
| Admin | No | All documents | Any document | Yes |
| User | Yes | Own + public | Own documents | No |

Private documents are visible only to uploader and admin.

## Search

- Live search (debounced 300ms, no Enter required)
- Diacritics-insensitive (unicode normalization NFKD)
- Searches across: filename, description, notes, hashtags
- Filters: category, file type (.pdf/.docx/.md/.txt)
- Sort: random (default), upload date, document date, file size

## User Settings

Per-user preferences stored in `user_settings` table:
- Page size (documents per page)
- Default sort order
- Hidden hashtags (comma-separated, documents with these tags are filtered out)
- Theme (light/dark)

## Document Viewing

- **PDF**: served via iframe from `/document/{id}/pdf`
- **Markdown**: rendered to HTML via Python `markdown` library
- **TXT**: displayed in `<pre>` tag with word-wrap
- **DOCX**: converted to HTML via `python-docx` (headings, formatting, tables)
