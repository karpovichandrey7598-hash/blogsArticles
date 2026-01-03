"""
Конфігурація застосунку
"""
import os
from typing import Optional


def _get_database_url() -> str:
    """Отримує URL бази даних з оточення та нормалізує його"""
    db_url = os.getenv("DATABASE_URL", "sqlite:///blog_platform.db")
    
    # Нормалізація для PostgreSQL (Render використовує postgres://)
    if db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql+psycopg://", 1)
    elif db_url.startswith("postgresql://") and "+psycopg" not in db_url:
        db_url = db_url.replace("postgresql://", "postgresql+psycopg://", 1)
    
    return db_url


class AppConfig:
    """Налаштування застосунку"""
    
    # Безпека
    SECRET_KEY: str = os.getenv("SECRET_KEY", "change-this-secret-key-in-production")
    
    # База даних
    SQLALCHEMY_DATABASE_URI: str = _get_database_url()
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False
    SQLALCHEMY_ECHO: bool = False
    
    # Flask налаштування
    TESTING: bool = False
    DEBUG: bool = os.getenv("FLASK_DEBUG", "False").lower() == "true"
    
    # Пагінація
    POSTS_PER_PAGE: int = 12


