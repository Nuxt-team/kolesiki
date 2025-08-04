from flask import Flask
from flask_migrate import Migrate
from models import db
from config import Config
import random

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    
    db.init_app(app)
    migrate = Migrate(app, db)
    
    
    from routes import register_blueprints
    register_blueprints(app)
    
    
    with app.app_context():
        import time
        max_retries = 30
        for i in range(max_retries):
            try:
                db.create_all()
                init_admin()
                init_checker()
                print(f"Database initialized successfully on attempt {i + 1}")
                break
            except Exception as e:
                print(f"Database connection attempt {i + 1} failed: {e}")
                if i < max_retries - 1:
                    time.sleep(2)
                else:
                    print("Failed to connect to database after all retries")
                    raise
    
    return app

def generate_password(username):
    random.seed(0x1337)
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

def generate_checker_password(username):
    random.seed(0x2024)
    return ''.join([str(random.randint(0, 9)) for _ in range(12)])

def init_admin():
    from models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password(generate_password('admin'))
        admin.balance = 1000000.0
        db.session.add(admin)
        db.session.commit()

def init_checker():
    from models import User
    checker = User.query.filter_by(username='checker').first()
    if not checker:
        checker = User(username='checker')
        checker.set_password(generate_checker_password('checker'))
        checker.balance = 500000.0
        db.session.add(checker)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)