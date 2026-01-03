"""
Точка входу для веб-застосунку "Платформа для блогів"
"""
from platform_app import create_application

application = create_application()

if __name__ == "__main__":
    application.run(debug=True, host="0.0.0.0", port=5000)


