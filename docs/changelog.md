# Changelog

**Author:** krse

## v2.1.0 - Security Hardening, XLSX/CSV Support & Fixes

### New File Format Support
- **XLSX** (Excel) — rendered as HTML tables (one per sheet), full-text search in cell content
- **CSV** — rendered as HTML table, full-text search in content
- New file type icons and filter options for XLSX and CSV

### Security Hardening
- **Secrets moved to `.env` file** — DATABASE_URL and SECRET_KEY no longer hardcoded in source
- **CSRF protection** — origin/referer-based middleware blocks cross-origin POST requests
- **XSS prevention** — all DOCX/XLSX/CSV/Markdown output HTML-escaped; script/iframe tags stripped
- **LIKE injection prevention** — SQL wildcards (`%`, `_`) escaped in all search and filter queries
- **Login rate limiting** — max 5 failed attempts per IP per 5 minutes
- **Path traversal protection** — all file operations validated against UPLOAD_DIR
- **Forced password change** — default admin must change password on first login
- **Secure cookie flag** — auto-set when HTTPS detected
- **Password policy** — minimum increased to 8 characters
- **Streaming upload** — files streamed to temp file (not loaded into RAM), with configurable MAX_UPLOAD_SIZE
- **Bulk operation limits** — capped at 200 items per request
- **Bulk ZIP cleanup** — temp files deleted after response via background task
- **User deletion cascade** — deleting a user removes their documents, files, favorites, and settings
- **DB connection pool** — configured with pool_pre_ping, pool_size, max_overflow
- **Dockerfile** — uploads directory permissions tightened from 777 to 755

### Other Improvements
- List view Created column now shows date and time
- List view row numbers option in Settings
- Local timezone support (TZ environment variable)
- N+1 query optimization — batch user lookups and bulk operations use IN() queries
- `.env` file support in docker-compose.yml
- File storage moved to external HDD via bind mount (`/mnt/data/media/document-manager/uploads/`)
- Docker volume replaced with bind mount for direct HDD access

---

## v2.0.0 - Major UI Overhaul & New Features

### Grid / List View
- Toggle between thumbnail grid and detailed table view
- Grid view: tiles with thumbnail/icon, filename label below (outside border)
- List view: table with name, type, size, created date, modified date, action buttons
- Column sorting: click headers (Name, Type, Size, Created, Modified) to sort server-side across all pages
- Ascending/descending toggle with arrow indicators
- Stable sort (secondary by ID) — no reordering when paging
- "Select all" checkbox in list view header
- View preference persisted in localStorage

### Multi-file Upload
- Upload multiple files at once from the upload modal
- Progress bar with per-file status
- Uses new JSON API endpoint (`POST /api/upload`)

### Favorites / Bookmarks
- Star/unstar documents via icon on tiles and list rows
- Filter by favorites only in filter panel
- Stored in dedicated `favorites` table

### Public Sharing
- Generate shareable links for documents (no login required)
- Share button in document view modal with copy-to-clipboard
- Public view (`/shared/{token}/view`) and download (`/shared/{token}`)
- Toggle share on/off per document

### Bulk Operations
- Checkbox selection on each document (grid and list)
- Bulk delete with confirmation
- Bulk ZIP download (original filenames)

### Secure Document URLs
- Document viewing uses daily-rotating HMAC hash URLs (`/v/{hash}/pdf`)
- Hash changes every day, prevents URL guessing
- O(1) hash resolution (no iteration)

### Search Context Details
- Info button appears next to search when results found
- Modal shows each matching document with first matching line highlighted
- Shows which field matched (content, filename, description, etc.)

### Modal-based UI
- Upload, Settings, Change Password moved to modals on dashboard
- No more page navigation for common actions
- Navbar links open modals on dashboard, fallback to pages elsewhere

### Settings Enhancements
- Show/hide tile controls (edit, download, delete) per user
- All settings accessible via JSON API (`GET/POST /api/settings`)
- Change password via JSON API (`POST /api/change-password`)

### Other Improvements
- Open document in full page (new tab) from view modal
- `updated_at` column on documents (tracks metadata edits)
- `share_token` column for public sharing
- Centered search bar in toolbar
- Increased spacing between tiles (16px gap)

---

## v1.1.0 - Full-Text Search & Help

### Full-Text Search
- Search inside document content (PDF, DOCX, MD, TXT), not just metadata
- Text extracted on upload via `extract_text()` helper using PyMuPDF, python-docx, and file read
- Content stored normalized (lowercase, no diacritics) in `Document.content` column
- Diacritics-insensitive — e.g. searching "resume" finds "Résumé" inside documents
- Existing documents backfilled automatically on startup

### Help Manual
- New `/help` page with accordion-style user manual
- Covers: overview, uploading, dashboard, search & filters, settings, visibility, admin features, password change
- Accessible via `?` icon in the navigation bar

---

## v1.0.0 - Initial Release

### Core Features
- FastAPI web application with Jinja2 templates + Bootstrap 5.3
- PostgreSQL database with SQLAlchemy ORM
- JWT authentication via httponly cookies
- Default admin account (admin/admin) created on startup

### User Management
- Admin can create, delete users and reset passwords
- Users can change their own password
- Role-based access: admin and regular user

### Document Management
- Upload PDF, DOCX, Markdown (.md), Text (.txt) files
- Files stored as SHA-256 hash (no extension on disk)
- Duplicate detection via content hash
- PDF thumbnail generation (configurable page number)
- Metadata: category, hashtags, description, notes, document date, private flag
- Edit metadata via modal dialog
- Delete document (removes file + thumbnail + DB record)
- Download with original filename

### Document Viewing
- PDF: native browser PDF viewer via iframe
- Markdown: rendered to HTML (tables, fenced code support)
- Text: displayed in preformatted block
- DOCX: converted to HTML (headings, bold/italic/underline, tables)
- All viewers open in modal dialog

### Search & Filter
- Live search without Enter key (300ms debounce)
- Diacritics-insensitive search (unicode NFKD normalization)
- Searches: filename, description, notes, hashtags
- Filter by category (dropdown)
- Filter by file type (PDF, DOCX, MD, TXT)
- Sort by: random, upload date, document date, file size (asc/desc)
- Pagination with configurable page size

### UI
- Compact tile-based document grid (144px wide tiles, flexbox layout)
- Tile shows: thumbnail/icon, filename, date, file size, action buttons
- File type icons: PDF (red), DOCX (blue), MD (cyan), TXT (gray)
- Light/dark theme (Bootstrap 5.3 data-bs-theme, per-user setting)
- All assets local (works offline) - Bootstrap CSS/JS, Icons, Flatpickr
- Date picker (Flatpickr)

### User Settings
- Documents per page (5-100)
- Default sort order
- Hidden hashtags (documents with specified tags are filtered out)
- Theme (light/dark)

### Access Control
- Admin sees all documents, cannot upload
- Regular users see own documents + public documents
- Private documents visible only to uploader and admin
- Owner or admin can delete/edit documents

### Deployment
- Docker support (Dockerfile + docker-compose.yml)
- Environment variables for configuration (DATABASE_URL, SECRET_KEY, UPLOAD_DIR)
- Persistent volume for uploads
