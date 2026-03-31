import os
import secrets
import sys
from pathlib import Path

DATABASE_URL = os.environ.get("DATABASE_URL", "")
if not DATABASE_URL:
    print("FATAL: DATABASE_URL not set in environment.", file=sys.stderr)
    sys.exit(1)

SECRET_KEY = os.environ.get("SECRET_KEY", "")
if not SECRET_KEY:
    SECRET_KEY = secrets.token_hex(32)
    print("WARNING: SECRET_KEY not set in environment. Generated random key. Sessions will not survive restarts.", file=sys.stderr)

ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ.get("ACCESS_TOKEN_EXPIRE_MINUTES", "480"))
UPLOAD_DIR = Path(os.environ.get("UPLOAD_DIR", "/opt/apps/document-manager/uploads"))
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

MAX_UPLOAD_SIZE = int(os.environ.get("MAX_UPLOAD_SIZE", str(100 * 1024 * 1024)))  # 100MB default
