from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import verify_password, create_access_token, get_current_user, hash_password
from app.models import UserSettings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_access_token({"sub": user.username})
    response = RedirectResponse(url="/", status_code=302)
    response.set_cookie("access_token", token, httponly=True, samesite="lax")
    settings = db.query(UserSettings).filter(UserSettings.user_id == user.id).first()
    theme = settings.theme if settings and settings.theme else "light"
    response.set_cookie("theme", theme, httponly=False, samesite="lax", max_age=31536000)
    return response


@router.get("/logout")
async def logout():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie("access_token")
    return response


@router.get("/change-password", response_class=HTMLResponse)
async def change_password_page(request: Request, current_user: User = Depends(get_current_user)):
    return templates.TemplateResponse("change_password.html", {"request": request, "user": current_user, "error": None, "success": None})


@router.post("/change-password", response_class=HTMLResponse)
async def change_password(
    request: Request,
    current_password: str = Form(...),
    new_password: str = Form(...),
    confirm_password: str = Form(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    ctx = {"request": request, "user": current_user, "error": None, "success": None}
    if not verify_password(current_password, current_user.hashed_password):
        ctx["error"] = "Current password is incorrect"
        return templates.TemplateResponse("change_password.html", ctx)
    if new_password != confirm_password:
        ctx["error"] = "New passwords do not match"
        return templates.TemplateResponse("change_password.html", ctx)
    if len(new_password) < 4:
        ctx["error"] = "Password must be at least 4 characters"
        return templates.TemplateResponse("change_password.html", ctx)
    current_user.hashed_password = hash_password(new_password)
    db.commit()
    ctx["success"] = "Password changed successfully"
    return templates.TemplateResponse("change_password.html", ctx)
