"""
Модель користувача системи
"""
from datetime import datetime
from typing import Optional

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from platform_app.core.database import db


class UserAccount(db.Model, UserMixin):
    """Акаунт користувача платформи"""
    
    __tablename__ = "user_accounts"
    
    # Основні поля
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(255), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    
    # Додаткова інформація
    full_name = db.Column(db.String(150), nullable=True)
    about = db.Column(db.Text, nullable=True)
    avatar_url = db.Column(db.String(500), nullable=True)
    
    # Метадані
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    registered_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    last_login = db.Column(db.DateTime, nullable=True)
    
    # Зв'язки
    posts = db.relationship(
        "BlogPost",
        backref="author",
        lazy="dynamic",
        cascade="all, delete-orphan",
        order_by="desc(BlogPost.published_at)"
    )
    
    def __repr__(self) -> str:
        return f"<UserAccount {self.username}>"
    
    def set_password(self, password: str) -> None:
        """Встановлює хеш пароля"""
        self.password_hash = generate_password_hash(password)
    
    def verify_password(self, password: str) -> bool:
        """Перевіряє правильність пароля"""
        return check_password_hash(self.password_hash, password)
    
    def get_display_name(self) -> str:
        """Повертає ім'я для відображення"""
        return self.full_name or self.username


