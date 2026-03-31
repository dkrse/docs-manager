# Architecture

**Author:** krse

## Overview

Document Manager is a FastAPI web application for managing documents (PDF, DOCX, XLSX, CSV, Markdown, TXT) with user authentication, metadata management, search/filter, and a grid/list UI.

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI (Python 3.12) |
| ORM | SQLAlchemy 2.0 |
| Database | PostgreSQL |
| Auth | JWT (python-jose) in httponly cookies |
| Password hashing | passlib + bcrypt |
| Templates | Jinja2 + Bootstrap 5.3 |
| PDF processing | PyMuPDF (thumbnail generation, text extraction) |
| DOCX processing | python-docx (HTML rendering) |
| XLSX processing | openpyxl (table rendering, text extraction) |
| CSV processing | csv stdlib (table rendering, text extraction) |
| Markdown | markdown (HTML rendering) |
| Deployment | Docker / Docker Compose with `.env` |

## Project Structure

```
/opt/apps/document-manager/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app, startup, router mounting
│   ├── config.py             # Settings from env vars (DB, secret, upload path)
│   ├── database.py           # SQLAlchemy engine, session factory
│   ├── models.py             # User, UserSettings, Document, Favorite ORM models
│   ├── schemas.py            # Pydantic schemas
│   ├── auth.py               # JWT, password hashing, auth dependencies
│   ├── routes/
│   │   ├── auth_routes.py    # Login, logout, change password
│   │   ├── user_routes.py    # Admin user management (CRUD)
│   │   └── document_routes.py # Documents, settings, edit, favorites, sharing, bulk ops
│   ├── templates/            # Jinja2 HTML templates
│   │   ├── base.html         # Layout, navbar, theme support
│   │   ├── login.html
│   │   ├── dashboard.html    # Grid/list view, search, modals (view, edit, upload, settings, password)
│   │   ├── upload.html
│   │   ├── users.html        # Admin user management
│   │   ├── settings.html     # User preferences
│   │   ├── help.html          # Help manual (accordion)
│   │   └── change_password.html
│   └── static/
│       ├── css/              # Bootstrap, Bootstrap Icons, Flatpickr, custom
│       ├── js/               # Bootstrap, Flatpickr
│       └── fonts/            # Bootstrap Icons woff/woff2
├── uploads/                  # Document storage (SHA-256 hash filenames)
│   └── thumbnails/           # PDF page thumbnails (PNG)
├── docs/
├── requirements.txt
├── run.py                    # Uvicorn entry point
├── Dockerfile
├── docker-compose.yml
├── .env                   # Environment variables (not in git)
└── CLAUDE.md
```

## File Storage

Documents are stored on disk using their **SHA-256 content hash** as filename (no extension). This:
- Prevents duplicate files (same content = same hash)
- Decouples storage from original filenames
- Original filename, extension stored in DB

## Authentication Flow

1. User submits credentials to `/login`
2. Rate limiter checks: max 5 failed attempts per IP per 5 minutes
3. Server validates, creates JWT token
4. Token stored in httponly cookie (`access_token`, `secure` flag on HTTPS)
5. Theme preference stored in regular cookie (`theme`)
6. All protected routes use `get_current_user` dependency
7. If `must_change_password` flag set, user is redirected to change password
8. On failure, redirect to `/login`

## Access Control

| Role | Can Upload | Sees Documents | Can Delete | Manage Users |
|------|-----------|----------------|------------|-------------|
| Admin | No | All documents | Any document | Yes |
| User | Yes | Own + public | Own documents | No |

Private documents are visible only to uploader and admin.

## Search

- Live search (debounced 300ms, no Enter required)
- **Full-text search**: searches inside document content (PDF, DOCX, MD, TXT)
- Diacritics-insensitive (unicode normalization NFKD) — both metadata and content
- Searches across: filename, description, notes, hashtags, **document content**
- Content extracted on upload via `extract_text()` helper, stored normalized (lowercase, no diacritics) in `Document.content` column
- Existing documents backfilled on startup
- LIKE wildcard characters (`%`, `_`) escaped in search queries
- Filters: category, file type (.pdf/.docx/.xlsx/.csv/.md/.txt)
- Sort: random (default), upload date, document date, file size, name, type, modified
- List view column sorting: name, type, size, created, modified (server-side, stable across pages)

## User Settings

Per-user preferences stored in `user_settings` table:
- Page size (documents per page)
- Default sort order
- Hidden hashtags (comma-separated, documents with these tags are filtered out)
- Theme (light/dark)
- Show/hide tile controls (edit, download, delete buttons)

## Document Viewing

- **PDF**: served via iframe from `/v/{hash}/pdf`
- **Markdown**: rendered to HTML via Python `markdown` library
- **TXT**: displayed in `<pre>` tag with word-wrap
- **DOCX**: converted to HTML via `python-docx` (headings, formatting, tables)
- **XLSX**: rendered as HTML tables (one per sheet) via `openpyxl`
- **CSV**: rendered as HTML table via `csv` stdlib
- **Open in new tab**: full-page document view via hash-based URL
- Document URLs use daily-rotating HMAC hashes (not sequential IDs)
- All rendered output sanitized against XSS (HTML escaped, script tags stripped)

## Favorites

- Users can star/bookmark any document
- Stored in `favorites` table (user_id, document_id)
- Filter view to show only favorites
- Toggle via star icon on grid tiles or list rows

## Public Sharing

- Document owner can generate a public share link (`share_token`)
- Accessible at `/shared/{token}/view` (view) and `/shared/{token}` (download)
- No authentication required for shared links
- Toggle on/off from document view modal

## Bulk Operations

- Checkbox selection on grid tiles and list rows (with "select all" in list view)
- Bulk delete (with confirmation)
- Bulk ZIP download (streams ZIP with original filenames)

## Grid / List View

- **Grid view**: thumbnail tiles with filename label below (outside tile border), action buttons
- **List view**: table with columns: checkbox, favorite, name, type, size, created, modified, actions
- **Column sorting**: click any column header (Name, Type, Size, Created, Modified) to sort
  - Sorting is server-side — works across all pages, not just the current page
  - Click again to toggle ascending/descending (arrow indicator in header)
  - Independent from the filter panel sort dropdown
  - Changing the dropdown sort resets column sort and vice versa
  - Stable sort with secondary ordering by document ID (no reordering when paging)
- View preference persisted in localStorage

## Search Context

- Detail button appears when search has results
- Opens modal showing each matching document with:
  - Filename and file type
  - First matching line with search term highlighted
  - Field where match was found (content, filename, description, etc.)

## Security

- **Configuration**: secrets (DATABASE_URL, SECRET_KEY) loaded from `.env` file, never hardcoded
- **CSRF**: origin/referer-based middleware blocks cross-origin state-changing requests
- **XSS**: all rendered content (DOCX, Markdown, XLSX, CSV) HTML-escaped; script/iframe tags stripped
- **LIKE injection**: SQL wildcard characters (`%`, `_`) escaped in all ILIKE queries
- **Upload limits**: streaming upload with configurable MAX_UPLOAD_SIZE (default 100MB)
- **Path traversal**: all file operations validated against UPLOAD_DIR
- **Rate limiting**: login limited to 5 failed attempts per IP per 5 minutes
- **Password policy**: minimum 8 characters; default admin forced to change on first login
- **Auth cookie**: `httponly`, `samesite=lax`, `secure` flag auto-set on HTTPS
- **Bulk limits**: bulk delete/zip capped at 200 documents per request
- **User deletion**: cascades to documents, files on disk, favorites, and settings
- **Temp files**: bulk ZIP temp files cleaned up via background task after response
- **DB pool**: configured with `pool_pre_ping=True` to handle stale connections
