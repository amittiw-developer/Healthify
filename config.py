import os

try:
    from dotenv import load_dotenv
except ImportError:
    def load_dotenv():
        return False

load_dotenv()


class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "change-this-secret-key")

    _db_url = os.getenv("SUPABASE_DB_URL") or os.getenv("DATABASE_URL") or ""
    if not _db_url or "[" in _db_url or "YOUR-PASSWORD" in _db_url:
        _db_url = "sqlite:///healthify.db"

    SQLALCHEMY_DATABASE_URI = _db_url
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = "Lax"
    PERMANENT_SESSION_LIFETIME = 60 * 60 * 24 * 7
