"""
Blueprint для роботи з блог-постами
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, abort
from flask_login import login_required, current_user
from sqlalchemy import or_

from platform_app.models.post import BlogPost
from platform_app.models.user import UserAccount
from platform_app.core.database import db
from platform_app.core.config import AppConfig

posts_bp = Blueprint("posts", __name__)


@posts_bp.route("/")
def list_posts():
    """Список всіх опублікованих постів з пагінацією"""
    page = request.args.get("page", 1, type=int)
    search_query = request.args.get("q", "").strip()
    
    query = BlogPost.query.filter_by(is_published=True)
    
    if search_query:
        query = query.filter(
            or_(
                BlogPost.title.ilike(f"%{search_query}%"),
                BlogPost.content.ilike(f"%{search_query}%")
            )
        )
    
    posts = query.order_by(BlogPost.published_at.desc()).paginate(
        page=page,
        per_page=AppConfig.POSTS_PER_PAGE,
        error_out=False
    )
    
    return render_template("posts/list.html", posts=posts, search_query=search_query)


@posts_bp.route("/<slug>")
def view_post(slug: str):
    """Перегляд окремого поста"""
    post = BlogPost.query.filter_by(slug=slug, is_published=True).first_or_404()
    
    # Збільшуємо лічильник переглядів
    post.increment_views()
    
    return render_template("posts/view.html", post=post)


@posts_bp.route("/create", methods=["GET"])
@login_required
def show_create():
    """Форма створення нового поста"""
    return render_template("posts/create.html")


@posts_bp.route("/create", methods=["POST"])
@login_required
def process_create():
    """Обробка створення нового поста"""
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    summary = request.form.get("summary", "").strip() or None
    tags = request.form.get("tags", "").strip() or None
    
    if not title or len(title) < 5:
        flash("Заголовок має бути мінімум 5 символів", "error")
        return redirect(url_for("posts.show_create"))
    
    if not content or len(content) < 100:
        flash("Текст поста має бути мінімум 100 символів", "error")
        return redirect(url_for("posts.show_create"))
    
    slug = BlogPost.generate_slug(title)
    
    # Перевірка унікальності slug
    existing = BlogPost.query.filter_by(slug=slug).first()
    if existing:
        slug = f"{slug}-{current_user.id}"
    
    new_post = BlogPost(
        title=title,
        slug=slug,
        content=content,
        summary=summary,
        tags=tags,
        author_id=current_user.id
    )
    
    db.session.add(new_post)
    db.session.commit()
    
    flash("Пост успішно створено!", "success")
    return redirect(url_for("posts.view_post", slug=new_post.slug))


@posts_bp.route("/<slug>/edit", methods=["GET"])
@login_required
def show_edit(slug: str):
    """Форма редагування поста"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    if post.author_id != current_user.id:
        abort(403)
    
    return render_template("posts/edit.html", post=post)


@posts_bp.route("/<slug>/edit", methods=["POST"])
@login_required
def process_edit(slug: str):
    """Обробка редагування поста"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    if post.author_id != current_user.id:
        abort(403)
    
    title = request.form.get("title", "").strip()
    content = request.form.get("content", "").strip()
    summary = request.form.get("summary", "").strip() or None
    tags = request.form.get("tags", "").strip() or None
    
    if not title or len(title) < 5:
        flash("Заголовок має бути мінімум 5 символів", "error")
        return redirect(url_for("posts.show_edit", slug=slug))
    
    if not content or len(content) < 100:
        flash("Текст поста має бути мінімум 100 символів", "error")
        return redirect(url_for("posts.show_edit", slug=slug))
    
    # Оновлюємо slug якщо заголовок змінився
    new_slug = BlogPost.generate_slug(title)
    if new_slug != post.slug:
        existing = BlogPost.query.filter_by(slug=new_slug).first()
        if existing and existing.id != post.id:
            new_slug = f"{new_slug}-{post.id}"
        post.slug = new_slug
    
    post.title = title
    post.content = content
    post.summary = summary
    post.tags = tags
    
    db.session.commit()
    
    flash("Пост успішно оновлено!", "success")
    return redirect(url_for("posts.view_post", slug=post.slug))


@posts_bp.route("/<slug>/delete", methods=["POST"])
@login_required
def process_delete(slug: str):
    """Видалення поста"""
    post = BlogPost.query.filter_by(slug=slug).first_or_404()
    
    if post.author_id != current_user.id:
        abort(403)
    
    db.session.delete(post)
    db.session.commit()
    
    flash("Пост успішно видалено", "success")
    return redirect(url_for("main.home"))


