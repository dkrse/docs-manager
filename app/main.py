from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware
from app.database import engine, SessionLocal
from app.models import Base, User, Document
from app.auth import hash_password
from app.routes.document_routes import extract_text, remove_diacritics
from app.routes import auth_routes, user_routes, document_routes

app = FastAPI(title="Document Manager")


class CSRFMiddleware(BaseHTTPMiddleware):
    """Block state-changing requests from foreign origins."""
    SAFE_METHODS = {"GET", "HEAD", "OPTIONS"}

    async def dispatch(self, request: Request, call_next):
        if request.method not in self.SAFE_METHODS:
            origin = request.headers.get("origin", "")
            referer = request.headers.get("referer", "")
            host = request.headers.get("host", "")
            if origin:
                origin_host = origin.split("//", 1)[-1].split("/")[0]
                if origin_host != host:
                    return JSONResponse({"detail": "CSRF rejected"}, status_code=403)
            elif referer:
                referer_host = referer.split("//", 1)[-1].split("/")[0]
                if referer_host != host:
                    return JSONResponse({"detail": "CSRF rejected"}, status_code=403)
        return await call_next(request)


app.add_middleware(CSRFMiddleware)

app.mount("/static", StaticFiles(directory="app/static"), name="static")

app.include_router(auth_routes.router)
app.include_router(user_routes.router)
app.include_router(document_routes.router)


@app.on_event("startup")
def startup():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        admin = db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin = User(username="admin", hashed_password=hash_password("admin"), is_admin=True, must_change_password=True)
            db.add(admin)
            db.commit()
        # Backfill content for existing documents
        docs = db.query(Document).filter(
            (Document.content == None) | (Document.content == "")
        ).all()
        for doc in docs:
            try:
                text = extract_text(doc.file_path, doc.file_extension or "")
                if text:
                    doc.content = remove_diacritics(text.lower())
            except Exception:
                pass
        if docs:
            db.commit()
    finally:
        db.close()
