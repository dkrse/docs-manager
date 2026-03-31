import os
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User, Document, UserSettings, Favorite
from app.auth import require_admin, hash_password

router = APIRouter(prefix="/admin")
templates = Jinja2Templates(directory="app/templates")


@router.get("/users", response_class=HTMLResponse)
async def list_users(request: Request, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    users = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse("users.html", {"request": request, "user": current_user, "users": users, "error": None, "success": None})


@router.post("/users/add", response_class=HTMLResponse)
async def add_user(
    request: Request,
    username: str = Form(...),
    password: str = Form(...),
    is_admin: bool = Form(False),
    current_user: User = Depends(require_admin),
    db: Session = Depends(get_db),
):
    existing = db.query(User).filter(User.username == username).first()
    users = db.query(User).order_by(User.id).all()
    ctx = {"request": request, "user": current_user, "users": users, "error": None, "success": None}
    if existing:
        ctx["error"] = f"Username '{username}' already exists"
        return templates.TemplateResponse("users.html", ctx)
    new_user = User(username=username, hashed_password=hash_password(password), is_admin=is_admin)
    db.add(new_user)
    db.commit()
    ctx["success"] = f"User '{username}' created"
    ctx["users"] = db.query(User).order_by(User.id).all()
    return templates.TemplateResponse("users.html", ctx)


@router.post("/users/{user_id}/delete")
async def delete_user(user_id: int, current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user and user.id != current_user.id:
        # Delete user's favorites
        db.query(Favorite).filter(Favorite.user_id == user.id).delete()
        # Delete user's documents and files
        docs = db.query(Document).filter(Document.uploaded_by == user.id).all()
        for doc in docs:
            if os.path.exists(doc.file_path):
                os.remove(doc.file_path)
            if doc.thumbnail_path and os.path.exists(doc.thumbnail_path):
                os.remove(doc.thumbnail_path)
            db.delete(doc)
        # Delete user settings
        db.query(UserSettings).filter(UserSettings.user_id == user.id).delete()
        db.delete(user)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)


@router.post("/users/{user_id}/reset-password")
async def reset_password(user_id: int, new_password: str = Form(...), current_user: User = Depends(require_admin), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        user.hashed_password = hash_password(new_password)
        db.commit()
    return RedirectResponse(url="/admin/users", status_code=302)
