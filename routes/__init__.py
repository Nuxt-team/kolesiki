from flask import Blueprint

def register_blueprints(app):
    from .main import main_bp
    from .auth import auth_bp
    from .products import products_bp
    from .users import users_bp
    
    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(products_bp, url_prefix='/products')
    app.register_blueprint(users_bp, url_prefix='/users')