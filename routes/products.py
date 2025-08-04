from flask import Blueprint, request, jsonify, session, render_template, redirect, url_for, flash
from models import db, Product, User, Purchase
from utils import login_required, get_current_user

products_bp = Blueprint('products', __name__)

@products_bp.route('/<int:product_id>', methods=['GET'])
def get_product(product_id):
    product = Product.query.get_or_404(product_id)
    current_user = get_current_user()
    
    if request.is_json:
        return jsonify({
            'id': product.id,
            'name': product.name,
            'description': product.description,
            'price': product.price,
            'owner': product.owner.username,
            'is_available': product.is_available
        })
    
    return render_template('products/detail.html', 
                         product=product, 
                         current_user=current_user,
                         user_balance=current_user.balance if current_user else 0)


@products_bp.route('/add', methods=['GET', 'POST'])
@login_required
def add_product():
    current_user = get_current_user()
    
    if request.method == 'GET':
        return render_template('products/add.html', 
                             current_user=current_user,
                             user_balance=current_user.balance if current_user else 0)

    if request.is_json:
        name = request.json.get('name')
        description = request.json.get('description')
        price = request.json.get('price')
        secret = request.json.get('secret')
    else:
        name = request.form.get('name')
        description = request.form.get('description')
        price = request.form.get('price')
        secret = request.form.get('secret')
        if price:
            try:
                price = float(price)
            except ValueError:
                flash('Цена должна быть числом', 'error')
                return render_template('products/add.html', current_user=current_user, user_balance=current_user.balance)

    if not name or not description or price is None or price < 0:
        if request.is_json:
            return jsonify({'error': 'name, description and price required'}), 400
        flash('Все поля обязательны для заполнения, цена должна быть положительной', 'error')
        return render_template('products/add.html', current_user=current_user, user_balance=current_user.balance)

    try:
        new_product = Product(
            name=name,
            description=description,
            price=price,
            secret=secret,
            owner_id=current_user.id
        )
        db.session.add(new_product)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Product added successfully'})
        
        flash('Товар успешно добавлен!', 'success')
        return redirect(url_for('products.my_products'))
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Failed to add product'}), 500
        flash('Ошибка при добавлении товара. Попробуйте еще раз.', 'error')
        return render_template('products/add.html', current_user=current_user, user_balance=current_user.balance)

@products_bp.route('/add-page', methods=['GET', 'POST'])
def add_product_page():
    if 'username' not in session:
        flash('Необходимо войти в систему', 'error')
        return redirect(url_for('auth.login_page'))
    
    if request.method == 'POST':
        return add_product()
    
    current_user = get_current_user()
    return render_template('products/add.html', 
                         current_user=current_user,
                         user_balance=current_user.balance if current_user else 0)

@products_bp.route('/my-products', methods=['GET'])
@login_required
def my_products():
    current_user = get_current_user()
    user_products = Product.query.filter_by(owner_id=current_user.id).all()
    
    if request.is_json:
        products_data = [{
            'id': p.id,
            'name': p.name,
            'description': p.description,
            'price': p.price,
            'secret': p.secret,
            'is_available': p.is_available,
            'created_at': p.created_at.isoformat()
        } for p in user_products]
        return jsonify({'products': products_data})
    
    return render_template('products/my_products.html', 
                         products=user_products,
                         current_user=current_user,
                         user_balance=current_user.balance)

@products_bp.route('/purchased', methods=['GET'])
@login_required  
def purchased_products():
    current_user = get_current_user()
    
    purchases = Purchase.query.filter_by(buyer_id=current_user.id).order_by(Purchase.created_at.desc()).all()
    
    total_spent = sum(p.amount for p in purchases)
    total_purchases = len(purchases)
    
    if request.is_json:
        purchases_data = [{
            'id': p.id,
            'product_id': p.product_id,
            'product_name': p.product.name,
            'product_description': p.product.description,
            'product_secret': p.product.secret,
            'amount': p.amount,
            'seller': p.seller.username,
            'purchase_date': p.created_at.isoformat()
        } for p in purchases]
        return jsonify({
            'purchases': purchases_data,
            'total_spent': total_spent,
            'total_purchases': total_purchases
        })
    
    return render_template('products/purchased.html',
                         purchases=purchases,
                         current_user=current_user,
                         user_balance=current_user.balance,
                         total_spent=total_spent,
                         total_purchases=total_purchases)

@products_bp.route('/purchased/<string:uuid_id>', methods=['GET'])
def purchase_detail(uuid_id):
    current_user = get_current_user()
    
    purchase = Purchase.query.filter_by(uuid_id=uuid_id).first_or_404()
    
    if request.is_json:
        response_data = {
            'id': purchase.id,
            'product_id': purchase.product_id,
            'product_name': purchase.product.name,
            'product_description': purchase.product.description,
            'amount': purchase.amount,
            'seller': purchase.seller.username,
            'purchase_date': purchase.created_at.isoformat(),
            'buyer': purchase.buyer.username,
            'is_own_purchase': current_user and current_user.id == purchase.buyer_id
        }
        
        if purchase.product.secret and current_user and current_user.id != purchase.buyer_id:
            response_data['product_secret'] = purchase.product.secret
        
        return jsonify(response_data)
    
    return render_template('products/purchase_detail.html',
                         purchase=purchase,
                         current_user=current_user,
                         user_balance=current_user.balance)

@products_bp.route('/buy/<int:product_id>', methods=['POST'])
@login_required
def buy_product(product_id):
    current_user = get_current_user()
    product = Product.query.get_or_404(product_id)
    
    if not product.is_available:
        if request.is_json:
            return jsonify({'error': 'Product is not available'}), 400
        flash('Товар недоступен для покупки', 'error')
        return redirect(url_for('main.index'))
    
    if product.owner_id == current_user.id:
        if request.is_json:
            return jsonify({'error': 'Cannot buy your own product'}), 400
        flash('Нельзя купить собственный товар', 'error')
        return redirect(url_for('main.index'))
    
    if not current_user.can_afford(product.price):
        if request.is_json:
            return jsonify({'error': 'Insufficient funds'}), 400
        flash('Недостаточно средств для покупки', 'error')
        return redirect(url_for('main.index'))
    
    try:
        current_user.balance -= product.price
        
        seller = User.query.get(product.owner_id)
        seller.balance += product.price
        
        purchase = Purchase(
            buyer_id=current_user.id,
            product_id=product.id,
            seller_id=seller.id,
            amount=product.price
        )
        db.session.add(purchase)
        
        product.is_available = False
        
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Product purchased successfully'})
        
        flash(f'Товар "{product.name}" успешно куплен за {product.price:.2f} руб.!', 'success')
        return redirect(url_for('main.index'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Purchase failed'}), 500
        flash('Ошибка при покупке товара. Попробуйте еще раз.', 'error')
        return redirect(url_for('main.index'))

@products_bp.route('/delete/<int:product_id>', methods=['POST'])
@login_required
def delete_product(product_id):
    current_user = get_current_user()
    product = Product.query.get_or_404(product_id)
    
    if product.owner_id != current_user.id:
        if request.is_json:
            return jsonify({'error': 'Access denied'}), 403
        flash('У вас нет прав для удаления этого товара', 'error')
        return redirect(url_for('products.my_products'))
    
    if not product.is_available:
        if request.is_json:
            return jsonify({'error': 'Cannot delete sold product'}), 400
        flash('Нельзя удалить проданный товар', 'error')
        return redirect(url_for('products.my_products'))
    
    try:
        db.session.delete(product)
        db.session.commit()
        
        if request.is_json:
            return jsonify({'message': 'Product deleted successfully'})
        
        flash(f'Товар "{product.name}" успешно удален', 'success')
        return redirect(url_for('products.my_products'))
        
    except Exception as e:
        db.session.rollback()
        if request.is_json:
            return jsonify({'error': 'Failed to delete product'}), 500
        flash('Ошибка при удалении товара', 'error')
        return redirect(url_for('products.my_products'))