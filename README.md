# Document Manager

**Author:** krse

Web application for managing PDF, DOCX, Markdown, and Text documents with user authentication, metadata, search/filter, and tile-based UI.

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
- **Tile-based UI**: compact document grid with thumbnails
- **Live search**: diacritics-insensitive, no Enter key needed
- **Filters**: category, file type, sort (date, size, random)
- **Metadata**: category, hashtags, description, notes, document date
- **Edit metadata**: inline modal editor
- **Duplicate detection**: SHA-256 content hash
- **User settings**: page size, default sort, hidden hashtags, light/dark theme
- **Access control**: admin/user roles, private documents
- **Offline**: all CSS/JS/fonts served locally
- **Docker ready**: Dockerfile + docker-compose.yml

## Documentation

- [Architecture](docs/architecture.md)
- [Diagrams](docs/diagrams.md)
- [Changelog](docs/changelog.md)

## Port

Application runs on port **5214**.
