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
        
        # Додаємо нові колонки для ШІ, якщо їх немає (міграція)
        try:
            from sqlalchemy import inspect, text
            inspector = inspect(db.engine)
            
            # Перевіряємо, чи існує таблиця
            if 'blog_posts' in inspector.get_table_names():
                columns = [col['name'] for col in inspector.get_columns('blog_posts')]
                
                if 'ai_summary' not in columns:
                    db.session.execute(text("ALTER TABLE blog_posts ADD COLUMN ai_summary TEXT"))
                    print("✓ Додано колонку ai_summary")
                
                if 'ai_generated' not in columns:
                    db.session.execute(text("ALTER TABLE blog_posts ADD COLUMN ai_generated BOOLEAN DEFAULT FALSE"))
                    print("✓ Додано колонку ai_generated")
                
                db.session.commit()
        except Exception as e:
            # Якщо таблиця ще не існує або інша помилка - ігноруємо
            print(f"Міграція (можливо таблиця ще не створена): {e}")
            try:
                db.session.rollback()
            except:
                pass
    
    return app


