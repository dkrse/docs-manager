import os
import hashlib
from datetime import datetime
from fastapi import APIRouter, Depends, Request, Form, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, FileResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from sqlalchemy import or_, func
from app.database import get_db
from app.models import User, Document, UserSettings
from app.auth import get_current_user
from app.config import UPLOAD_DIR
import unicodedata
import fitz  # PyMuPDF
import markdown as md
from docx import Document as DocxDocument

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

THUMBNAILS_DIR = UPLOAD_DIR / "thumbnails"
THUMBNAILS_DIR.mkdir(parents=True, exist_ok=True)

ALLOWED_EXTENSIONS = {".pdf", ".md", ".txt", ".docx"}

FILE_TYPE_ICONS = {
    ".pdf": "bi-file-earmark-pdf text-danger",
    ".md": "bi-file-earmark-text text-info",
    ".txt": "bi-file-earmark-text text-secondary",
    ".docx": "bi-file-earmark-word text-primary",
}


def extract_text(file_path: str, extension: str) -> str:
    """Extract plain text content from a document file."""
    ext = extension.lower()
    try:
        if ext == ".pdf":
            doc = fitz.open(file_path)
            text = "\n".join(page.get_text() for page in doc)
            doc.close()
            return text
        elif ext == ".docx":
            doc = DocxDocument(file_path)
            parts = [para.text for para in doc.paragraphs]
            for table in doc.tables:
                for row in table.rows:
                    for cell in row.cells:
                        parts.append(cell.text)
            return "\n".join(parts)
        elif ext in (".md", ".txt"):
            with open(file_path, "r", encoding="utf-8", errors="replace") as f:
                return f.read()
    except Exception:
        return ""
    return ""


def remove_diacritics(s: str) -> str:
    nfkd = unicodedata.normalize('NFKD', s)
    return ''.join(c for c in nfkd if not unicodedata.combining(c))


def generate_thumbnail(pdf_path: str, page_num: int, thumb_path: str):
    doc = fitz.open(pdf_path)
    page_idx = max(0, min(page_num - 1, len(doc) - 1))
    page = doc[page_idx]
    mat = fitz.Matrix(2, 2)
    pix = page.get_pixmap(matrix=mat)
    pix.save(thumb_path)
    doc.close()


def get_user_settings(user: User, db: Session) -> UserSettings:
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    if not settings:
        settings = UserSettings(user_id=user.id)
        db.add(settings)
        db.commit()
        db.refresh(settings)
    return settings


def docx_to_html(file_path: str) -> str:
    doc = DocxDocument(file_path)
    html_parts = []
    for para in doc.paragraphs:
        style = para.style.name.lower() if para.style else ""
        text = para.text
        if not text.strip():
            html_parts.append("<br>")
            continue
        if "heading 1" in style:
            html_parts.append(f"<h1>{text}</h1>")
        elif "heading 2" in style:
            html_parts.append(f"<h2>{text}</h2>")
        elif "heading 3" in style:
            html_parts.append(f"<h3>{text}</h3>")
        elif "heading" in style:
            html_parts.append(f"<h4>{text}</h4>")
        else:
            # Build rich text from runs
            runs_html = ""
            for run in para.runs:
                t = run.text
                if not t:
                    continue
                if run.bold:
                    t = f"<strong>{t}</strong>"
                if run.italic:
                    t = f"<em>{t}</em>"
                if run.underline:
                    t = f"<u>{t}</u>"
                runs_html += t
            if runs_html:
                html_parts.append(f"<p>{runs_html}</p>")
            else:
                html_parts.append(f"<p>{text}</p>")

    # Tables
    for table in doc.tables:
        html_parts.append("<table class='table table-bordered table-sm'>")
        for i, row in enumerate(table.rows):
            html_parts.append("<tr>")
            tag = "th" if i == 0 else "td"
            for cell in row.cells:
                html_parts.append(f"<{tag}>{cell.text}</{tag}>")
            html_parts.append("</tr>")
        html_parts.append("</table>")

    return "\n".join(html_parts)


@router.get("/api/documents", response_class=JSONResponse)
async def api_documents(
    request: Request,
    search: str = "",
    category: str = "",
    file_type: str = "",
    sort: str = "",
    page: int = 1,
    doc_date_from: str = "",
    doc_date_to: str = "",
    upload_date_from: str = "",
    upload_date_to: str = "",
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = get_user_settings(current_user, db)
    page_size = settings.page_size or 20
    if not sort:
        sort = settings.default_sort or "random"

    query = db.query(Document)

    if not current_user.is_admin:
        query = query.filter(
            or_(
                Document.uploaded_by == current_user.id,
                Document.is_private == False,
            )
        )

    hidden = settings.hidden_hashtags.strip() if settings.hidden_hashtags else ""
    if hidden:
        hidden_tags = [t.strip().lower() for t in hidden.split(",") if t.strip()]
        for tag in hidden_tags:
            query = query.filter(~func.lower(Document.hashtags).ilike(f"%{tag}%"))

    if search:
        normalized = remove_diacritics(search.lower())
        like = f"%{normalized}%"
        query = query.filter(
            or_(
                func.lower(Document.original_filename).ilike(like),
                func.lower(Document.description).ilike(like),
                func.lower(Document.notes).ilike(like),
                func.lower(Document.hashtags).ilike(like),
                func.lower(Document.content).ilike(like),
            )
        )
    if category:
        query = query.filter(Document.category == category)
    if file_type:
        query = query.filter(Document.file_extension == file_type)

    if doc_date_from:
        try:
            query = query.filter(Document.document_date >= datetime.strptime(doc_date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if doc_date_to:
        try:
            query = query.filter(Document.document_date <= datetime.strptime(doc_date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass
    if upload_date_from:
        try:
            query = query.filter(Document.uploaded_at >= datetime.strptime(upload_date_from, "%Y-%m-%d"))
        except ValueError:
            pass
    if upload_date_to:
        try:
            query = query.filter(Document.uploaded_at <= datetime.strptime(upload_date_to, "%Y-%m-%d").replace(hour=23, minute=59, second=59))
        except ValueError:
            pass

    sort_map = {
        "upload_desc": Document.uploaded_at.desc(),
        "upload_asc": Document.uploaded_at.asc(),
        "date_desc": Document.document_date.desc(),
        "date_asc": Document.document_date.asc(),
        "size_desc": Document.file_size.desc(),
        "size_asc": Document.file_size.asc(),
        "random": func.random(),
    }
    query = query.order_by(sort_map.get(sort, func.random()))

    total = query.count()
    total_pages = max(1, (total + page_size - 1) // page_size)
    page = max(1, min(page, total_pages))
    documents = query.offset((page - 1) * page_size).limit(page_size).all()

    user_cache = {}
    results = []
    for doc in documents:
        if doc.uploaded_by not in user_cache:
            u = db.query(User).filter(User.id == doc.uploaded_by).first()
            user_cache[doc.uploaded_by] = u.username if u else "Unknown"
        results.append({
            "id": doc.id,
            "original_filename": doc.original_filename,
            "file_extension": doc.file_extension or ".pdf",
            "description": doc.description or "",
            "category": doc.category or "",
            "hashtags": doc.hashtags or "",
            "is_private": doc.is_private,
            "uploaded_by": doc.uploaded_by,
            "uploader_name": user_cache[doc.uploaded_by],
            "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d") if doc.uploaded_at else "",
            "has_thumbnail": bool(doc.thumbnail_path),
            "notes": doc.notes or "",
            "file_size": doc.file_size or 0,
            "document_date": doc.document_date.strftime("%Y-%m-%d") if doc.document_date else "",
        })

    return {
        "documents": results,
        "page": page,
        "page_size": page_size,
        "total_pages": total_pages,
        "total": total,
        "is_admin": current_user.is_admin,
        "user_id": current_user.id,
        "sort": sort,
    }


@router.get("/", response_class=HTMLResponse)
async def dashboard(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    all_categories = [r[0] for r in db.query(Document.category).distinct().all() if r[0]]
    settings = get_user_settings(current_user, db)
    return templates.TemplateResponse("dashboard.html", {
        "request": request,
        "user": current_user,
        "categories": all_categories,
        "default_sort": settings.default_sort or "random",
    })


@router.get("/upload", response_class=HTMLResponse)
async def upload_page(request: Request, current_user: User = Depends(get_current_user)):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot upload documents")
    return templates.TemplateResponse("upload.html", {"request": request, "user": current_user, "error": None})


@router.post("/upload", response_class=HTMLResponse)
async def upload_document(
    request: Request,
    file: UploadFile = File(...),
    category: str = Form(""),
    hashtags: str = Form(""),
    description: str = Form(""),
    notes: str = Form(""),
    is_private: bool = Form(False),
    document_date: str = Form(""),
    thumbnail_page: int = Form(1),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    if current_user.is_admin:
        raise HTTPException(status_code=403, detail="Admins cannot upload documents")

    ext = os.path.splitext(file.filename)[1].lower() if file.filename else ""
    if ext not in ALLOWED_EXTENSIONS:
        return templates.TemplateResponse("upload.html", {
            "request": request, "user": current_user,
            "error": f"Allowed file types: {', '.join(ALLOWED_EXTENSIONS)}"
        })

    content = await file.read()
    file_hash = hashlib.sha256(content).hexdigest()

    existing = db.query(Document).filter(Document.content_hash == file_hash).first()
    if existing:
        return templates.TemplateResponse("upload.html", {
            "request": request, "user": current_user,
            "error": f"This file already exists as '{existing.original_filename}'"
        })

    file_path = UPLOAD_DIR / file_hash
    with open(file_path, "wb") as f:
        f.write(content)

    # Generate thumbnail only for PDFs
    thumb_path = None
    if ext == ".pdf":
        thumb_filename = f"{file_hash}.png"
        thumb_path = THUMBNAILS_DIR / thumb_filename
        try:
            generate_thumbnail(str(file_path), thumbnail_page, str(thumb_path))
        except Exception:
            thumb_path = None

    doc_date = None
    if document_date:
        try:
            doc_date = datetime.strptime(document_date, "%Y-%m-%d")
        except ValueError:
            pass

    extracted_text = remove_diacritics(extract_text(str(file_path), ext).lower())

    doc = Document(
        filename=file_hash,
        original_filename=file.filename,
        file_extension=ext,
        file_path=str(file_path),
        file_size=len(content),
        content_hash=file_hash,
        thumbnail_path=str(thumb_path) if thumb_path else None,
        thumbnail_page=thumbnail_page if ext == ".pdf" else 1,
        category=category.strip(),
        hashtags=hashtags.strip(),
        description=description.strip(),
        notes=notes.strip(),
        is_private=is_private,
        uploaded_by=current_user.id,
        document_date=doc_date,
        content=extracted_text,
    )
    db.add(doc)
    db.commit()
    return RedirectResponse(url="/", status_code=302)


@router.get("/document/{doc_id}/thumbnail")
async def get_thumbnail(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if not current_user.is_admin and doc.is_private and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403)
    if doc.thumbnail_path and os.path.exists(doc.thumbnail_path):
        return FileResponse(doc.thumbnail_path, media_type="image/png")
    raise HTTPException(status_code=404)


@router.get("/document/{doc_id}/info", response_class=JSONResponse)
async def document_info(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if not current_user.is_admin and doc.is_private and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403)
    uploader = db.query(User).filter(User.id == doc.uploaded_by).first()
    return {
        "id": doc.id,
        "original_filename": doc.original_filename,
        "file_extension": doc.file_extension or ".pdf",
        "description": doc.description or "",
        "category": doc.category or "",
        "hashtags": doc.hashtags or "",
        "notes": doc.notes or "",
        "is_private": doc.is_private,
        "uploader_name": uploader.username if uploader else "Unknown",
        "uploaded_at": doc.uploaded_at.strftime("%Y-%m-%d %H:%M") if doc.uploaded_at else "",
        "document_date": doc.document_date.strftime("%Y-%m-%d") if doc.document_date else "",
        "file_size": doc.file_size or 0,
    }


@router.get("/document/{doc_id}/download")
async def download_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_admin and doc.is_private and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(doc.file_path, filename=doc.original_filename, media_type="application/octet-stream")


@router.get("/document/{doc_id}/pdf")
async def serve_pdf(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_admin and doc.is_private and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    return FileResponse(doc.file_path, media_type="application/pdf")


@router.get("/document/{doc_id}/render", response_class=HTMLResponse)
async def render_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Render markdown, txt, or docx as HTML for the modal viewer."""
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404)
    if not current_user.is_admin and doc.is_private and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403)

    ext = (doc.file_extension or "").lower()
    body = ""

    if ext == ".md":
        with open(doc.file_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        body = md.markdown(raw, extensions=["tables", "fenced_code", "codehilite"])
    elif ext == ".txt":
        with open(doc.file_path, "r", encoding="utf-8", errors="replace") as f:
            raw = f.read()
        import html
        body = f"<pre style='white-space:pre-wrap; word-wrap:break-word;'>{html.escape(raw)}</pre>"
    elif ext == ".docx":
        try:
            body = docx_to_html(doc.file_path)
        except Exception as e:
            body = f"<p class='text-danger'>Error rendering document: {e}</p>"
    else:
        raise HTTPException(status_code=400, detail="Unsupported format for rendering")

    html_page = f"""<!DOCTYPE html>
<html><head>
<meta charset="utf-8">
<link href="/static/css/bootstrap.min.css" rel="stylesheet">
<style>body {{ padding: 20px; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif; }}
pre {{ background: #f8f9fa; padding: 15px; border-radius: 4px; }}
table {{ margin: 10px 0; }}
img {{ max-width: 100%; }}</style>
</head><body>{body}</body></html>"""
    return HTMLResponse(html_page)


@router.post("/document/{doc_id}/delete")
async def delete_document(doc_id: int, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_admin and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")
    if os.path.exists(doc.file_path):
        os.remove(doc.file_path)
    if doc.thumbnail_path and os.path.exists(doc.thumbnail_path):
        os.remove(doc.thumbnail_path)
    db.delete(doc)
    db.commit()
    return RedirectResponse(url="/", status_code=302)


# --- Edit metadata route ---

@router.post("/document/{doc_id}/edit", response_class=JSONResponse)
async def edit_document_metadata(
    request: Request,
    doc_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    doc = db.query(Document).filter(Document.id == doc_id).first()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    if not current_user.is_admin and doc.uploaded_by != current_user.id:
        raise HTTPException(status_code=403, detail="Access denied")

    form = await request.form()
    doc.category = form.get("category", doc.category or "").strip()
    doc.hashtags = form.get("hashtags", doc.hashtags or "").strip()
    doc.description = form.get("description", doc.description or "").strip()
    doc.notes = form.get("notes", doc.notes or "").strip()
    is_private = form.get("is_private", "")
    doc.is_private = is_private == "true"
    doc_date_str = form.get("document_date", "").strip()
    if doc_date_str:
        try:
            doc.document_date = datetime.strptime(doc_date_str, "%Y-%m-%d")
        except ValueError:
            pass
    else:
        doc.document_date = None
    db.commit()
    return {"ok": True}


# --- Settings routes ---

@router.get("/help", response_class=HTMLResponse)
async def help_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("help.html", {"request": request, "user": current_user})


@router.get("/settings", response_class=HTMLResponse)
async def settings_page(request: Request, current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    settings = get_user_settings(current_user, db)
    return templates.TemplateResponse("settings.html", {
        "request": request, "user": current_user, "settings": settings, "success": None
    })


@router.post("/settings", response_class=HTMLResponse)
async def save_settings(
    request: Request,
    page_size: int = Form(20),
    default_sort: str = Form("random"),
    hidden_hashtags: str = Form(""),
    theme: str = Form("light"),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    settings = get_user_settings(current_user, db)
    settings.page_size = max(5, min(100, page_size))
    settings.default_sort = default_sort
    settings.hidden_hashtags = hidden_hashtags.strip()
    settings.theme = theme if theme in ("light", "dark") else "light"
    db.commit()
    response = templates.TemplateResponse("settings.html", {
        "request": request, "user": current_user, "settings": settings, "success": "Settings saved"
    })
    response.set_cookie("theme", settings.theme, httponly=False, samesite="lax", max_age=31536000)
    return response
