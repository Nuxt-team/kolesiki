from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models import db, User, Transaction
from utils import login_required, get_current_user

users_bp = Blueprint('users', __name__)

@users_bp.route('/transfer', methods=['GET', 'POST'])
@login_required
def transfer_money():
    current_user = get_current_user()
    
    if request.method == 'GET':
        return render_template('users/transfer.html', 
                             current_user=current_user,
                             user_balance=current_user.balance)

    if request.is_json:
        to_user = request.json.get('to_user')
        amount = request.json.get('amount')
    else:
        to_user = request.form.get('to_user')
        amount = request.form.get('amount')
        if amount:
            try:
                amount = float(amount)
            except ValueError:
                flash('Сумма должна быть числом', 'error')
                return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)

    if not to_user or amount is None or amount == 0:
        if request.is_json:
            return jsonify({'error': 'to_user and non-zero amount required'}), 400
        flash('Получатель и ненулевая сумма обязательны', 'error')
        return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)

    recipient = User.query.filter_by(username=to_user).first()
    if not recipient:
        if request.is_json:
            return jsonify({'error': 'Recipient not found'}), 404
        flash('Пользователь не найден', 'error')
        return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)
    
    if recipient.id == current_user.id:
        if request.is_json:
            return jsonify({'error': 'Cannot transfer to yourself'}), 400
        flash('Нельзя переводить деньги самому себе', 'error')
        return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)
    
    if amount > 0 and not current_user.can_afford(amount):
        if request.is_json:
            return jsonify({'error': 'Insufficient funds'}), 400
        flash('Недостаточно средств для перевода', 'error')
        return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)

    try:
        current_user.balance -= amount
        
        recipient.balance += amount
        
        transaction = Transaction(
            from_user_id=current_user.id,
            to_user_id=recipient.id,
            amount=amount,
            description=f'Перевод от {current_user.username} к {recipient.username}'
        )
        db.session.add(transaction)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': f'Transferred {amount} from {current_user.username} to {to_user}'})
        
        flash(f'Переведено {amount:.2f} руб. пользователю {to_user}', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Transfer failed'}), 500
        flash('Ошибка при переводе денег. Попробуйте еще раз.', 'error')
        return render_template('users/transfer.html', current_user=current_user, user_balance=current_user.balance)

@users_bp.route('/transfer-page', methods=['GET', 'POST'])
@login_required
def transfer_page():
    if request.method == 'POST':
        return transfer_money()
    
    current_user = get_current_user()
    return render_template('users/transfer.html', 
                         current_user=current_user,
                         user_balance=current_user.balance)

@users_bp.route('/profile')
@login_required
def profile():
    current_user = get_current_user()
    
    total_products = len(current_user.products)
    available_products = len([p for p in current_user.products if p.is_available])
    sold_products = total_products - available_products
    
    from models import Purchase
    purchases = Purchase.query.filter_by(buyer_id=current_user.id).all()
    total_purchases = len(purchases)
    total_spent = sum(p.amount for p in purchases)
    
    sales = Purchase.query.filter_by(seller_id=current_user.id).all()
    total_sales = len(sales)
    total_earned = sum(s.amount for s in sales)
    
    from models import Transaction
    sent_transactions = Transaction.query.filter_by(from_user_id=current_user.id).all()
    received_transactions = Transaction.query.filter_by(to_user_id=current_user.id).all()
    
    total_sent = sum(t.amount for t in sent_transactions)
    total_received = sum(t.amount for t in received_transactions)
    
    stats = {
        'total_products': total_products,
        'available_products': available_products,
        'sold_products': sold_products,
        'total_purchases': total_purchases,
        'total_spent': total_spent,
        'total_sales': total_sales,
        'total_earned': total_earned,
        'total_sent': total_sent,
        'total_received': total_received
    }
    
    if request.is_json:
        return jsonify({
            'user': {
                'id': current_user.id,
                'username': current_user.username,
                'balance': current_user.balance,
                'created_at': current_user.created_at.isoformat()
            },
            'stats': stats
        })
    
    return render_template('users/profile.html',
                         current_user=current_user,
                         stats=stats,
                         user_balance=current_user.balance)