import os
from datetime import timedelta

class Config():
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-only-change-me")
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///hbntory.db"
    )
    JWT_EXPIRES = timedelta(hours=10)