"""
Платформа для блогів/статей - головний модуль застосунку
"""
from flask import Flask

from platform_app.core.config import AppConfig
from platform_app.core.database import init_database
from platform_app.core.auth_manager import init_auth
from platform_app.blueprints import register_blueprints


def create_application() -> Flask:
    """Створює та налаштовує Flask застосунок"""
    app = Flask(__name__, template_folder="templates", static_folder="static")
    
    # Завантаження конфігурації
    app.config.from_object(AppConfig)
    
    # Ініціалізація розширень
    init_database(app)
    init_auth(app)
    
    # Реєстрація blueprint'ів
    register_blueprints(app)
    
    # Створення таблиць БД при першому запуску
    with app.app_context():
        from platform_app.core.database import db
        db.create_all()
    
    return app


