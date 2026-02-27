from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from app.database import engine, SessionLocal
from app.models import Base, User
from app.auth import hash_password
from app.routes import auth_routes, user_routes, document_routes

app = FastAPI(title="Document Manager")

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
            admin = User(username="admin", hashed_password=hash_password("admin"), is_admin=True)
            db.add(admin)
            db.commit()
    finally:
        db.close()
