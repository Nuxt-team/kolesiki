from flask import Flask, request, jsonify, session
import random

app = Flask(__name__)
app.secret_key = 'shop_secret_key_123'

def generate_password(username):
    random.seed(0x1337)
    return ''.join([str(random.randint(0, 9)) for _ in range(16)])

@app.route('/register', methods=['POST'])
def register():
    username = request.json.get('username')
    if not username:
        return jsonify({'error': 'Username required'}), 400

    password = generate_password(username)

    # TODO: Save user to database

    return jsonify({'username': username, 'password': password})

@app.route('/login', methods=['POST'])
def login():
    username = request.json.get('username')
    password = request.json.get('password')

    if not username or not password:
        return jsonify({'error': 'Username and password required'}), 400

    # TODO: Check user credentials in database

    session['username'] = username
    return jsonify({'message': 'Login successful'})

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # TODO: Get product from database by ID

    return jsonify({'id': product_id, 'name': 'Sample Product', 'description': 'Sample Description', 'price': 100})

@app.route('/transfer', methods=['POST'])
def transfer_money():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    from_user = session['username']
    to_user = request.json.get('to_user')
    amount = request.json.get('amount')

    if not to_user or amount is None:
        return jsonify({'error': 'to_user and amount required'}), 400

    # TODO: Transfer money between users in database

    return jsonify({'message': f'Transferred {amount} from {from_user} to {to_user}'})

@app.route('/add_product', methods=['POST'])
def add_product():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    name = request.json.get('name')
    description = request.json.get('description')
    price = request.json.get('price')

    if not name or not description or price is None:
        return jsonify({'error': 'name, description and price required'}), 400

    # TODO: Add product to database

    return jsonify({'message': 'Product added successfully'})

@app.route('/my-products', methods=['GET'])
def my_products():
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    # TODO: Get user products from database

    return jsonify({'products': []})

@app.route('/buy/<int:product_id>', methods=['POST'])
def buy_product(product_id):
    if 'username' not in session:
        return jsonify({'error': 'Not logged in'}), 401

    # TODO: Get product price from database
    # TODO: Get user money from database
    # TODO: Check if user has enough money
    # TODO: Update user money and product ownership in database

    return jsonify({'message': 'Product purchased successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
