"""
Реєстрація всіх blueprint'ів застосунку
"""
from flask import Flask

from platform_app.blueprints.auth import auth_bp
from platform_app.blueprints.posts import posts_bp
from platform_app.blueprints.users import users_bp
from platform_app.blueprints.statistics import stats_bp


def register_blueprints(app: Flask) -> None:
    """Реєструє всі blueprint'и в застосунку"""
    app.register_blueprint(auth_bp, url_prefix="/auth")
    app.register_blueprint(posts_bp, url_prefix="/posts")
    app.register_blueprint(users_bp, url_prefix="/users")
    app.register_blueprint(stats_bp)
    
    # Головна сторінка
    from platform_app.blueprints.main import main_bp
    app.register_blueprint(main_bp)


