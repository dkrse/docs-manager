# Changelog

**Author:** krse

## v1.1.0 - Full-Text Search & Help

### Full-Text Search
- Search inside document content (PDF, DOCX, MD, TXT), not just metadata
- Text extracted on upload via `extract_text()` helper using PyMuPDF, python-docx, and file read
- Content stored normalized (lowercase, no diacritics) in `Document.content` column
- Diacritics-insensitive — e.g. searching "faktura" finds "Faktúra" inside documents
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
- Slovak-localized date picker (Flatpickr)

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
