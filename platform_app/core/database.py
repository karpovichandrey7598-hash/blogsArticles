"""
Модуль для роботи з базою даних
"""
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

# Глобальні об'єкти для БД
db = SQLAlchemy()
migrate = Migrate()


def init_database(app: Flask) -> None:
    """Ініціалізує підключення до бази даних"""
    db.init_app(app)
    migrate.init_app(app, db)


