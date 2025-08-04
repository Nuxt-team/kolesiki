from flask import Blueprint, render_template, session, request, jsonify
from models import User, Product, Purchase, Transaction, db
from utils import get_current_user, admin_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/')
def index():
    current_user = get_current_user()
    products = Product.query.filter_by(is_available=True).limit(6).all()
    
    return render_template('index.html', 
                         current_user=current_user,
                         products=products,
                         user_balance=current_user.balance if current_user else 0)

@main_bp.route('/details', methods=['GET'])
@admin_required
def system_details():
    current_user = get_current_user()
    
    total_users = User.query.count()
    total_products = Product.query.count()
    available_products = Product.query.filter_by(is_available=True).count()
    sold_products = total_products - available_products
    
    total_purchases = Purchase.query.count()
    total_transactions = Transaction.query.count()
    
    products_with_flags = Product.query.filter(Product.secret.isnot(None)).order_by(Product.created_at.desc()).all()
    
    total_money_in_system = sum(user.balance for user in User.query.all())
    
    if request.is_json:
        return jsonify({
            'stats': {
                'total_users': total_users,
                'total_products': total_products,
                'available_products': available_products,
                'sold_products': sold_products,
                'total_purchases': total_purchases,
                'total_transactions': total_transactions,
                'total_money_in_system': total_money_in_system
            },
            'products_with_flags': [{'id': p.id, 'name': p.name, 'price': p.price, 'secret': p.secret, 'available': p.is_available, 'owner': p.owner.username} for p in products_with_flags]
        })
    
    return render_template('admin/details.html',
                         current_user=current_user,
                         total_users=total_users,
                         total_products=total_products,
                         available_products=available_products,
                         sold_products=sold_products,
                         total_purchases=total_purchases,
                         total_transactions=total_transactions,
                         total_money_in_system=total_money_in_system,
                         products_with_flags=products_with_flags)