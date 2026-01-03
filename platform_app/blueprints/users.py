"""
Blueprint для роботи з профілями користувачів
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_required, current_user

from platform_app.models.user import UserAccount
from platform_app.models.post import BlogPost
from platform_app.core.database import db

users_bp = Blueprint("users", __name__)


@users_bp.route("/<username>")
def view_profile(username: str):
    """Перегляд профілю користувача"""
    user = UserAccount.query.filter_by(username=username).first_or_404()
    
    posts = (
        BlogPost.query
        .filter_by(author_id=user.id, is_published=True)
        .order_by(BlogPost.published_at.desc())
        .limit(20)
        .all()
    )
    
    total_views = sum(post.view_count for post in posts)
    
    return render_template("users/profile.html", user=user, posts=posts, total_views=total_views)


@users_bp.route("/me", methods=["GET"])
@login_required
def show_my_profile():
    """Мій профіль (редагування)"""
    return render_template("users/edit_profile.html", user=current_user)


@users_bp.route("/me", methods=["POST"])
@login_required
def update_my_profile():
    """Оновлення профілю користувача"""
    full_name = request.form.get("full_name", "").strip() or None
    about = request.form.get("about", "").strip() or None
    
    if full_name and len(full_name) > 150:
        flash("Ім'я занадто довге (максимум 150 символів)", "error")
        return redirect(url_for("users.show_my_profile"))
    
    current_user.full_name = full_name
    current_user.about = about
    
    db.session.commit()
    
    flash("Профіль оновлено", "success")
    return redirect(url_for("users.view_profile", username=current_user.username))


@users_bp.route("/me/posts")
@login_required
def my_posts():
    """Список моїх постів"""
    posts = (
        BlogPost.query
        .filter_by(author_id=current_user.id)
        .order_by(BlogPost.published_at.desc())
        .all()
    )
    
    return render_template("users/my_posts.html", posts=posts)


