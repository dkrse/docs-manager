import os
from pathlib import Path

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:dexxxx1@192.168.1.189/documents")
SECRET_KEY = os.environ.get("SECRET_KEY", "a7f3b9c1d4e8f2a5b6c7d8e9f0a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/opt/apps/document-manager/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
