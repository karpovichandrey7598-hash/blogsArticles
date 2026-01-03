"""
Головна сторінка та загальні маршрути
"""
from flask import Blueprint, render_template

from platform_app.models.post import BlogPost
from platform_app.core.database import db
from platform_app.core.config import AppConfig

main_bp = Blueprint("main", __name__)


@main_bp.route("/")
def home():
    """Головна сторінка зі списком останніх постів"""
    posts = (
        BlogPost.query
        .filter_by(is_published=True)
        .order_by(BlogPost.published_at.desc())
        .limit(AppConfig.POSTS_PER_PAGE)
        .all()
    )
    
    return render_template("main/home.html", posts=posts)


@main_bp.route("/about")
def about():
    """Сторінка про платформу"""
    return render_template("main/about.html")


