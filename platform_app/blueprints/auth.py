"""
Blueprint для автентифікації користувачів
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash
from flask_login import login_user, logout_user, login_required, current_user

from platform_app.models.user import UserAccount
from platform_app.core.database import db

auth_bp = Blueprint("auth", __name__)


@auth_bp.route("/login", methods=["GET"])
def show_login():
    """Відображення форми входу"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("auth/login.html")


@auth_bp.route("/login", methods=["POST"])
def process_login():
    """Обробка входу користувача"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    username = request.form.get("username", "").strip()
    password = request.form.get("password", "")
    
    if not username or not password:
        flash("Заповніть всі поля", "error")
        return redirect(url_for("auth.show_login"))
    
    user = UserAccount.query.filter_by(username=username).first()
    
    if not user or not user.verify_password(password):
        flash("Невірне ім'я користувача або пароль", "error")
        return redirect(url_for("auth.show_login"))
    
    if not user.is_active:
        flash("Ваш акаунт деактивовано", "error")
        return redirect(url_for("auth.show_login"))
    
    login_user(user)
    flash(f"Вітаємо, {user.get_display_name()}!", "success")
    return redirect(url_for("main.home"))


@auth_bp.route("/register", methods=["GET"])
def show_register():
    """Відображення форми реєстрації"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    return render_template("auth/register.html")


@auth_bp.route("/register", methods=["POST"])
def process_register():
    """Обробка реєстрації нового користувача"""
    if current_user.is_authenticated:
        return redirect(url_for("main.home"))
    
    username = request.form.get("username", "").strip()
    email = request.form.get("email", "").strip().lower()
    password = request.form.get("password", "")
    password_confirm = request.form.get("password_confirm", "")
    full_name = request.form.get("full_name", "").strip() or None
    
    # Валідація
    errors = []
    
    if not username or len(username) < 3:
        errors.append("Ім'я користувача має бути мінімум 3 символи")
    
    if not email or "@" not in email:
        errors.append("Введіть коректний email")
    
    if not password or len(password) < 6:
        errors.append("Пароль має бути мінімум 6 символів")
    
    if password != password_confirm:
        errors.append("Паролі не співпадають")
    
    # Перевірка унікальності
    if UserAccount.query.filter_by(username=username).first():
        errors.append("Користувач з таким ім'ям вже існує")
    
    if UserAccount.query.filter_by(email=email).first():
        errors.append("Користувач з таким email вже існує")
    
    if errors:
        for error in errors:
            flash(error, "error")
        return redirect(url_for("auth.show_register"))
    
    # Створення користувача
    new_user = UserAccount(
        username=username,
        email=email,
        full_name=full_name
    )
    new_user.set_password(password)
    
    db.session.add(new_user)
    db.session.commit()
    
    login_user(new_user)
    flash("Реєстрація успішна! Вітаємо на платформі!", "success")
    return redirect(url_for("main.home"))


@auth_bp.route("/logout", methods=["POST"])
@login_required
def process_logout():
    """Вихід користувача"""
    logout_user()
    flash("Ви успішно вийшли з акаунта", "info")
    return redirect(url_for("main.home"))


