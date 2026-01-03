"""
Скрипт для додавання полів ШІ до таблиці blog_posts
Виконайте цей скрипт один раз на Render через Shell або локально

На Render: Web Service → Shell → python migrate_add_ai_fields.py
"""
from platform_app import create_application
from platform_app.core.database import db
from sqlalchemy import text

app = create_application()

with app.app_context():
    try:
        # Перевіряємо, чи існує колонка ai_summary
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='blog_posts' AND column_name='ai_summary'
        """))
        
        if not result.fetchone():
            db.session.execute(text("ALTER TABLE blog_posts ADD COLUMN ai_summary TEXT"))
            print("✓ Додано колонку ai_summary")
        else:
            print("✓ Колонка ai_summary вже існує")
    except Exception as e:
        print(f"Помилка при додаванні ai_summary: {e}")
    
    try:
        # Перевіряємо, чи існує колонка ai_generated
        result = db.session.execute(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name='blog_posts' AND column_name='ai_generated'
        """))
        
        if not result.fetchone():
            db.session.execute(text("ALTER TABLE blog_posts ADD COLUMN ai_generated BOOLEAN DEFAULT FALSE"))
            print("✓ Додано колонку ai_generated")
        else:
            print("✓ Колонка ai_generated вже існує")
    except Exception as e:
        print(f"Помилка при додаванні ai_generated: {e}")
    
    try:
        db.session.commit()
        print("✓ Міграція завершена успішно!")
    except Exception as e:
        print(f"Помилка при commit: {e}")
        db.session.rollback()
