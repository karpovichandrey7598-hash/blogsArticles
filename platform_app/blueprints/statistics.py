"""
Blueprint для статистики та візуалізації
"""
from flask import Blueprint, render_template
from flask_login import login_required, current_user
from sqlalchemy import func, coalesce
from datetime import datetime, timedelta

from platform_app.models.post import BlogPost
from platform_app.models.user import UserAccount
from platform_app.core.database import db

stats_bp = Blueprint("stats", __name__, url_prefix="/stats")


@stats_bp.route("/")
@login_required
def dashboard():
    """Панель статистики користувача"""
    user_posts = BlogPost.query.filter_by(author_id=current_user.id).all()
    
    # Загальна статистика
    total_posts = len(user_posts)
    total_views = sum(post.view_count for post in user_posts)
    ai_generated_count = sum(1 for post in user_posts if post.ai_generated)
    
    # Статистика по днях (останні 30 днів)
    days_data = {}
    for i in range(30):
        date = (datetime.utcnow() - timedelta(days=i)).date()
        days_data[date.isoformat()] = 0
    
    for post in user_posts:
        date_key = post.published_at.date().isoformat()
        if date_key in days_data:
            days_data[date_key] += 1
    
    # Найпопулярніші пости
    top_posts = sorted(user_posts, key=lambda p: p.view_count, reverse=True)[:5]
    
    # Статистика використання ШІ
    ai_usage = {
        "with_ai": ai_generated_count,
        "without_ai": total_posts - ai_generated_count,
    }
    
    # Статистика по місяцях
    monthly_data = {}
    for post in user_posts:
        month_key = post.published_at.strftime("%Y-%m")
        if month_key not in monthly_data:
            monthly_data[month_key] = {"posts": 0, "views": 0}
        monthly_data[month_key]["posts"] += 1
        monthly_data[month_key]["views"] += post.view_count
    
    return render_template(
        "statistics/dashboard.html",
        total_posts=total_posts,
        total_views=total_views,
        ai_generated_count=ai_generated_count,
        days_data=days_data,
        top_posts=top_posts,
        ai_usage=ai_usage,
        monthly_data=monthly_data,
    )


@stats_bp.route("/global")
def global_stats():
    """Глобальна статистика платформи"""
    total_users = UserAccount.query.count()
    total_posts = BlogPost.query.filter_by(is_published=True).count()
    total_views = db.session.query(func.sum(BlogPost.view_count)).scalar() or 0
    ai_posts = BlogPost.query.filter_by(ai_generated=True, is_published=True).count()
    
    # Найпопулярніші пости
    popular_posts = (
        BlogPost.query
        .filter_by(is_published=True)
        .order_by(BlogPost.view_count.desc())
        .limit(10)
        .all()
    )
    
    # Найактивніші автори
    active_authors = (
        db.session.query(
            UserAccount,
            func.count(BlogPost.id).label("post_count"),
            func.sum(BlogPost.view_count).label("total_views")
        )
        .join(BlogPost, UserAccount.id == BlogPost.author_id)
        .filter(BlogPost.is_published == True)
        .group_by(UserAccount.id)
        .order_by(func.count(BlogPost.id).desc())
        .limit(10)
        .all()
    )
    
    return render_template(
        "statistics/global.html",
        total_users=total_users,
        total_posts=total_posts,
        total_views=total_views,
        ai_posts=ai_posts,
        popular_posts=popular_posts,
        active_authors=active_authors,
    )

