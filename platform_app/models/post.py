"""
Модель блог-поста
"""
from datetime import datetime
from typing import Optional

from platform_app.core.database import db


class BlogPost(db.Model):
    """Блог-пост на платформі"""
    
    __tablename__ = "blog_posts"
    
    # Основні поля
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(300), nullable=False)
    slug = db.Column(db.String(350), unique=True, nullable=False, index=True)
    content = db.Column(db.Text, nullable=False)
    summary = db.Column(db.Text, nullable=True)  # Короткий опис для превью
    
    # Автор та статус
    author_id = db.Column(db.Integer, db.ForeignKey("user_accounts.id"), nullable=False, index=True)
    is_published = db.Column(db.Boolean, default=True, nullable=False)
    
    # Метадані
    published_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False, index=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)
    view_count = db.Column(db.Integer, default=0, nullable=False)
    
    # SEO та додатково
    tags = db.Column(db.String(500), nullable=True)  # Через кому
    featured_image = db.Column(db.String(500), nullable=True)
    
    def __repr__(self) -> str:
        return f"<BlogPost {self.slug}>"
    
    def increment_views(self) -> None:
        """Збільшує лічильник переглядів"""
        self.view_count += 1
        db.session.commit()
    
    @staticmethod
    def generate_slug(title: str) -> str:
        """Генерує slug з заголовка"""
        import re
        slug = title.lower()
        slug = re.sub(r'[^\w\s-]', '', slug)
        slug = re.sub(r'[-\s]+', '-', slug)
        return slug[:350]
    
    def get_tags_list(self) -> list:
        """Повертає список тегів"""
        if not self.tags:
            return []
        return [tag.strip() for tag in self.tags.split(",") if tag.strip()]


