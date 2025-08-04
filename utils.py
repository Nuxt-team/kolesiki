from functools import wraps
from flask import session, redirect, url_for, flash, g
from models import User

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            flash('Необходимо войти в систему', 'error')
            return redirect(url_for('auth.login_page'))
        return f(*args, **kwargs)
    return decorated_function

def get_current_user():
    if 'user_id' in session:
        return User.query.get(session['user_id'])
    return None

def admin_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        current_user = get_current_user()
        if not current_user or current_user.username not in ['admin', 'checker']:
            flash('Доступ запрещен', 'error')
            return redirect(url_for('main.index'))
        return f(*args, **kwargs)
    return decorated_function