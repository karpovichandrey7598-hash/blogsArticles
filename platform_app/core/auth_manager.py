"""
Менеджер автентифікації користувачів
"""
from flask import Flask
from flask_login import LoginManager

login_manager = LoginManager()


def init_auth(app: Flask) -> None:
    """Ініціалізує систему автентифікації"""
    login_manager.init_app(app)
    login_manager.login_view = "auth.show_login"
    login_manager.login_message = "Будь ласка, увійдіть для доступу до цієї сторінки."
    login_manager.login_message_category = "info"
    
    # Завантажувач користувача
    @login_manager.user_loader
    def load_user(user_id: str):
        from platform_app.models.user import UserAccount
        from platform_app.core.database import db
        try:
            return db.session.get(UserAccount, int(user_id))
        except (ValueError, TypeError):
            return None


