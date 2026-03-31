import time
from collections import defaultdict
from fastapi import APIRouter, Depends, Request, Form
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session
from app.database import get_db
from app.models import User
from app.auth import verify_password, create_access_token, get_current_user, hash_password
from app.models import UserSettings

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

# Rate limiting: max 5 failed attempts per IP per 5 minutes
_login_attempts: dict[str, list[float]] = defaultdict(list)
_RATE_LIMIT_MAX = 5
_RATE_LIMIT_WINDOW = 300  # seconds


def _check_rate_limit(ip: str) -> bool:
    now = time.time()
    attempts = _login_attempts[ip]
    _login_attempts[ip] = [t for t in attempts if now - t < _RATE_LIMIT_WINDOW]
    return len(_login_attempts[ip]) >= _RATE_LIMIT_MAX


def _record_failed_attempt(ip: str):
    _login_attempts[ip].append(time.time())


@router.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request, "error": None})


@router.post("/login", response_class=HTMLResponse)
async def login(request: Request, username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    client_ip = request.client.host if request.client else "unknown"
    if _check_rate_limit(client_ip):
        return templates.TemplateResponse("login.html", {"request": request, "error": "Too many login attempts. Try again in a few minutes."})
    user = db.query(User).filter(User.username == username).first()
    if not user or not verify_password(password, user.hashed_password):
        _record_failed_attempt(client_ip)
        return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
    token = create_access_token({"sub": user.username})
    response = RedirectResponse(url="/", status_code=302)
    is_https = request.url.scheme == "https" or request.headers.get("x-forwarded-proto") == "https"
    response.set_cookie("access_token", token, httponly=True, samesite="lax", secure=is_https)
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
    if len(new_password) < 8:
        ctx["error"] = "Password must be at least 8 characters"
        return templates.TemplateResponse("change_password.html", ctx)
    current_user.hashed_password = hash_password(new_password)
    current_user.must_change_password = False
    db.commit()
    ctx["success"] = "Password changed successfully"
    return templates.TemplateResponse("change_password.html", ctx)


@router.post("/api/change-password", response_class=JSONResponse)
async def api_change_password(
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    form = await request.form()
    current_password = form.get("current_password", "")
    new_password = form.get("new_password", "")
    confirm_password = form.get("confirm_password", "")
    if not verify_password(current_password, current_user.hashed_password):
        return JSONResponse({"ok": False, "error": "Current password is incorrect"})
    if new_password != confirm_password:
        return JSONResponse({"ok": False, "error": "New passwords do not match"})
    if len(new_password) < 4:
        return JSONResponse({"ok": False, "error": "Password must be at least 8 characters"})
    current_user.hashed_password = hash_password(new_password)
    current_user.must_change_password = False
    db.commit()
    return JSONResponse({"ok": True})
