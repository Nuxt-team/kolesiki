from flask import Flask, request, jsonify
import random

app = Flask(__name__)

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

    return jsonify({'message': 'Login successful'})

@app.route('/product/<int:product_id>', methods=['GET'])
def get_product(product_id):
    # TODO: Get product from database by ID

    return jsonify({'id': product_id, 'name': 'Sample Product', 'description': 'Sample Description', 'price': 100})

@app.route('/transfer', methods=['POST'])
def transfer_money():
    from_user = request.json.get('from_user')
    to_user = request.json.get('to_user')
    amount = request.json.get('amount')

    if not from_user or not to_user or amount is None:
        return jsonify({'error': 'from_user, to_user and amount required'}), 400

    # TODO: Transfer money between users in database

    return jsonify({'message': f'Transferred {amount} from {from_user} to {to_user}'})

@app.route('/add_product', methods=['POST'])
def add_product():
    name = request.json.get('name')
    description = request.json.get('description')
    price = request.json.get('price')

    if not name or not description or price is None:
        return jsonify({'error': 'name, description and price required'}), 400

    # TODO: Add product to database

    return jsonify({'message': 'Product added successfully'})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
