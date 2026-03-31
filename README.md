# Document Manager

**Author:** krse
**License:** MIT

Web application for managing PDF, DOCX, Markdown, and Text documents with user authentication, metadata, search/filter, and tile-based UI.

## License

MIT License

Copyright (c) 2025 krse

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

## Quick Start

### Docker (recommended)

```bash
docker compose up -d --build
```

App runs at http://localhost:5214

### Local

```bash
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
python run.py
```

For development with auto-reload:
```bash
RELOAD=true python run.py
```

## Configuration

Environment variables (or defaults in `app/config.py`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql://postgres:dexxxx1@192.168.1.189/documents` | PostgreSQL connection |
| `SECRET_KEY` | (hardcoded) | JWT signing key |
| `UPLOAD_DIR` | `/opt/apps/document-manager/uploads` | File storage path |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `480` | Session duration |
| `RELOAD` | `false` | Enable uvicorn auto-reload |

## Default Login

- **Username:** `admin`
- **Password:** `admin`

Admin account is created automatically on first startup.

## Features

- **Multi-format support**: PDF, DOCX, Markdown, TXT
- **In-browser viewing**: PDF viewer, Markdown/DOCX/TXT renderers
- **Grid/List view**: toggle between thumbnail grid and detailed sortable table view
- **Full-text search**: searches inside document content (PDF, DOCX, MD, TXT)
- **Search context**: detail button shows first matching line per document with highlighting
- **Live search**: diacritics-insensitive, no Enter key needed
- **Column sorting**: click list view headers (Name, Type, Size, Created, Modified) to sort across all pages
- **Filters**: category, file type, sort, favorites, date ranges
- **Multi-file upload**: upload multiple files at once with progress bar
- **Favorites**: star/bookmark documents, filter by favorites
- **Public sharing**: generate shareable links for documents (no login required)
- **Bulk operations**: select multiple documents, bulk delete or ZIP download
- **Metadata**: category, hashtags, description, notes, document date
- **Edit metadata**: inline modal editor
- **Duplicate detection**: SHA-256 content hash
- **User settings**: page size, default sort, hidden hashtags, light/dark theme, show/hide tile controls
- **Modal-based UI**: upload, settings, change password all in modals on dashboard
- **Secure document URLs**: daily-rotating hash-based URLs for document viewing
- **Access control**: admin/user roles, private documents
- **Offline**: all CSS/JS/fonts served locally
- **Help manual**: in-app user guide accessible via navbar
- **Docker ready**: Dockerfile + docker-compose.yml

## Documentation

- [Architecture](docs/architecture.md)
- [Diagrams](docs/diagrams.md)
- [Changelog](docs/changelog.md)
- [Pricing Analysis](docs/price.md)

## Port

Application runs on port **5214**.
