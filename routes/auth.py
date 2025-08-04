from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models import db, User

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    
    if request.is_json:
        username = request.json.get('username')
        password = request.json.get('password')
        password_confirm = request.json.get('password_confirm')
    else:
        username = request.form.get('username')
        password = request.form.get('password')
        password_confirm = request.form.get('password_confirm')
    
    if not username:
        if request.is_json:
            return jsonify({'error': 'Username required'}), 400
        flash('Имя пользователя обязательно', 'error')
        return render_template('auth/register.html')
    
    if not password:
        if request.is_json:
            return jsonify({'error': 'Password required'}), 400
        flash('Пароль обязателен', 'error')
        return render_template('auth/register.html')
    
    if len(password) < 6:
        if request.is_json:
            return jsonify({'error': 'Password must be at least 6 characters'}), 400
        flash('Пароль должен содержать минимум 6 символов', 'error')
        return render_template('auth/register.html')
    
    if password != password_confirm:
        if request.is_json:
            return jsonify({'error': 'Passwords do not match'}), 400
        flash('Пароли не совпадают', 'error')
        return render_template('auth/register.html')
    
    if len(username) < 3 or len(username) > 50:
        if request.is_json:
            return jsonify({'error': 'Username must be between 3 and 50 characters'}), 400
        flash('Имя пользователя должно содержать от 3 до 50 символов', 'error')
        return render_template('auth/register.html')

    existing_user = User.query.filter_by(username=username).first()
    if existing_user:
        if request.is_json:
            return jsonify({'error': 'Username already exists'}), 400
        flash('Пользователь с таким именем уже существует', 'error')
        return render_template('auth/register.html')

    new_user = User(username=username)
    new_user.set_password(password)
    
    try:
        db.session.add(new_user)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'username': username, 'message': 'Registration successful'})
        
        flash(f'Регистрация успешна! Добро пожаловать, {username}!', 'success')
        return redirect(url_for('auth.login_page'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Registration failed'}), 500
        flash('Ошибка при регистрации. Попробуйте еще раз.', 'error')
        return render_template('auth/register.html')

@auth_bp.route('/register-page', methods=['GET', 'POST'])
def register_page():
    if request.method == 'POST':
        return register()  # Переадресация на основной обработчик
    return render_template('auth/register.html')

@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    
    if request.is_json:
        username = request.json.get('username')
        password = request.json.get('password')
    else:
        username = request.form.get('username')
        password = request.form.get('password')

    if not username or not password:
        if request.is_json:
            return jsonify({'error': 'Username and password required'}), 400
        flash('Имя пользователя и пароль обязательны', 'error')
        return render_template('auth/login.html')

    user = User.query.filter_by(username=username).first()
    
    if not user or not user.check_password(password):
        if request.is_json:
            return jsonify({'error': 'Invalid credentials'}), 401
        flash('Неверное имя пользователя или пароль', 'error')
        return render_template('auth/login.html')

    session['username'] = username
    session['user_id'] = user.id
    
    if request.is_json:
        return jsonify({'message': 'Login successful'})
    
    flash('Вход выполнен успешно!', 'success')
    return redirect(url_for('main.index'))

@auth_bp.route('/login-page', methods=['GET', 'POST'])
def login_page():
    if request.method == 'POST':
        return login()
    return render_template('auth/login.html')

@auth_bp.route('/logout')
def logout():
    session.pop('username', None)
    flash('Вы успешно вышли из системы', 'info')
    return redirect(url_for('main.index'))