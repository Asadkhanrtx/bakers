from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity
from flask_cors import CORS
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import timedelta
import mysql.connector
import os
from functools import wraps
import json

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'
app.config['JWT_ACCESS_TOKEN_EXPIRES'] = timedelta(days=30)

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'saista_bakers'),
    'port': int(os.getenv('DB_PORT', 3306))
}

jwt = JWTManager(app)
CORS(app)

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)

def dict_from_cursor(cursor, data):
    """Convert database row to dictionary"""
    columns = [desc[0] for desc in cursor.description]
    return dict(zip(columns, data))

# Routes

@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT 1")
        cursor.close()
        conn.close()
        return jsonify({'status': 'healthy', 'service': 'user-service'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/signup', methods=['POST'])
def signup():
    """User signup endpoint"""
    try:
        data = request.get_json()
        
        # Validation
        if not data or not data.get('username') or not data.get('email') or not data.get('password'):
            return jsonify({'error': 'Missing required fields'}), 400
        
        username = data.get('username')
        email = data.get('email')
        password = data.get('password')
        full_name = data.get('full_name', '')
        
        # Hash password
        password_hash = generate_password_hash(password)
        
        # Insert into database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute(
                "INSERT INTO users (username, email, password_hash, full_name) VALUES (%s, %s, %s, %s)",
                (username, email, password_hash, full_name)
            )
            conn.commit()
            user_id = cursor.lastrowid
            
            # Create JWT token
            access_token = create_access_token(identity=user_id)
            
            return jsonify({
                'message': 'User created successfully',
                'user_id': user_id,
                'access_token': access_token
            }), 201
            
        except mysql.connector.errors.IntegrityError as e:
            return jsonify({'error': 'Username or email already exists'}), 409
        finally:
            cursor.close()
            conn.close()
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/login', methods=['POST'])
def login():
    """User login endpoint"""
    try:
        data = request.get_json()
        
        if not data or not data.get('username') or not data.get('password'):
            return jsonify({'error': 'Missing username or password'}), 400
        
        username = data.get('username')
        password = data.get('password')
        
        # Get user from database
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, password_hash, full_name, email FROM users WHERE username = %s", (username,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Verify password
        if not check_password_hash(user[1], password):
            return jsonify({'error': 'Invalid username or password'}), 401
        
        # Create JWT token
        access_token = create_access_token(identity=user[0])
        
        return jsonify({
            'message': 'Login successful',
            'user_id': user[0],
            'username': username,
            'full_name': user[2],
            'email': user[3],
            'access_token': access_token
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/profile', methods=['GET'])
@jwt_required()
def get_profile():
    """Get user profile"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, full_name, phone, address FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3],
            'phone': user[4],
            'address': user[5]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products', methods=['GET'])
def get_products():
    """Get all products with optional category filter"""
    try:
        category = request.args.get('category')
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        if category:
            cursor.execute(
                "SELECT id, name, description, price, category FROM products WHERE category = %s AND available = TRUE ORDER BY name",
                (category,)
            )
        else:
            cursor.execute("SELECT id, name, description, price, category FROM products WHERE available = TRUE ORDER BY category, name")
        
        products = cursor.fetchall()
        cursor.close()
        conn.close()
        
        product_list = []
        for product in products:
            product_list.append({
                'id': product[0],
                'name': product[1],
                'description': product[2],
                'price': float(product[3]),
                'category': product[4]
            })
        
        return jsonify({
            'products': product_list,
            'total': len(product_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/categories', methods=['GET'])
def get_categories():
    """Get all product categories"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT DISTINCT category FROM products WHERE available = TRUE ORDER BY category")
        categories = cursor.fetchall()
        cursor.close()
        conn.close()
        
        category_list = [cat[0] for cat in categories]
        
        return jsonify({
            'categories': category_list
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/products/<int:product_id>', methods=['GET'])
def get_product(product_id):
    """Get single product by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute(
            "SELECT id, name, description, price, category FROM products WHERE id = %s AND available = TRUE",
            (product_id,)
        )
        product = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not product:
            return jsonify({'error': 'Product not found'}), 404
        
        return jsonify({
            'id': product[0],
            'name': product[1],
            'description': product[2],
            'price': float(product[3]),
            'category': product[4]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    """Get user information by ID"""
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT id, username, email, full_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        return jsonify({
            'id': user[0],
            'username': user[1],
            'email': user[2],
            'full_name': user[3]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5001)
