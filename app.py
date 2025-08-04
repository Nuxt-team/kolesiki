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
        db.create_all()
        init_admin()
    
    return app

def generate_password(username):
    random.seed(0x1337)
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

def init_admin():
    from models import User
    admin = User.query.filter_by(username='admin').first()
    if not admin:
        admin = User(username='admin')
        admin.set_password(generate_password('admin'))
        admin.balance = 1000000.0
        db.session.add(admin)
        db.session.commit()

app = create_app()

if __name__ == '__main__':
    import os
    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    app.run(host='0.0.0.0', port=5000, debug=debug_mode)