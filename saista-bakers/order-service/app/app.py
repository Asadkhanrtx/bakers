from flask import Flask, request, jsonify
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
import mysql.connector
import os
from datetime import datetime
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart

app = Flask(__name__)

# Configuration
app.config['JWT_SECRET_KEY'] = 'your-secret-key-change-this-in-production'

# Database configuration
DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'root'),
    'database': os.getenv('DB_NAME', 'saista_bakers'),
    'port': int(os.getenv('DB_PORT', 3306))
}

# Email configuration
EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
    'smtp_port': int(os.getenv('SMTP_PORT', 1025)),
    'sender_email': os.getenv('SENDER_EMAIL', 'noreply@saista-bakers.com'),
    'sender_password': os.getenv('SENDER_PASSWORD', '')
}

jwt = JWTManager(app)
CORS(app)

def get_db_connection():
    """Get database connection"""
    return mysql.connector.connect(**DB_CONFIG)

# Custom Cake Pricing Logic

def calculate_custom_price(pound, flavour):
    """
    Calculate custom cake price
    Base: 1 pound = 300, each extra pound = +200
    Flavour per pound:
    - fruit = +100
    - chocolate = +200
    - fondant = +250
    """
    base_price = 300  # 1 pound base
    extra_pound_price = 200  # per extra pound
    
    flavour_surcharge = {
        'fruit': 100,
        'chocolate': 200,
        'fondant': 250
    }
    
    # Calculate base price
    if pound <= 1:
        price = base_price
    else:
        price = base_price + (pound - 1) * extra_pound_price
    
    # Add flavour surcharge per pound
    flavour_charge = flavour_surcharge.get(flavour, 0) * pound
    
    total_price = price + flavour_charge
    return total_price

def send_email(recipient_email, subject, body):
    """Send email notification"""
    try:
        msg = MIMEMultipart()
        msg['From'] = EMAIL_CONFIG['sender_email']
        msg['To'] = recipient_email
        msg['Subject'] = subject
        
        msg.attach(MIMEText(body, 'html'))
        
        # Using basic SMTP without authentication (suitable for local SMTP server)
        server = smtplib.SMTP(EMAIL_CONFIG['smtp_server'], EMAIL_CONFIG['smtp_port'])
        server.send_message(msg)
        server.quit()
        return True
    except Exception as e:
        print(f"Error sending email: {str(e)}")
        return False

def send_order_confirmation_email(email, user_name, order_id, items, total_price):
    """Send order confirmation email"""
    subject = f"Order Confirmation - #{order_id}"
    
    items_html = ""
    for item in items:
        items_html += f"<tr><td>{item['name']}</td><td>x{item['quantity']}</td><td>Rs. {item['price_at_purchase']}</td></tr>"
    
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Order Confirmation</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for your order! Your order has been confirmed.</p>
            
            <h3>Order Details</h3>
            <p><strong>Order ID:</strong> {order_id}</p>
            
            <h3>Items</h3>
            <table border="1" cellpadding="10">
                <tr>
                    <th>Item</th>
                    <th>Quantity</th>
                    <th>Price</th>
                </tr>
                {items_html}
            </table>
            
            <h3>Total: Rs. {total_price}</h3>
            
            <p>We will prepare your order and contact you soon for delivery details.</p>
            <p>Thank you for choosing Saista Bakers!</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)

def send_custom_cake_confirmation_email(email, user_name, order_id, pound, flavour, description, estimated_price):
    """Send custom cake order confirmation email"""
    subject = f"Custom Cake Order Confirmation - #{order_id}"
    
    body = f"""
    <html>
        <body style="font-family: Arial, sans-serif;">
            <h2>Custom Cake Order Confirmation</h2>
            <p>Hi {user_name},</p>
            <p>Thank you for ordering a custom cake! Your order has been confirmed.</p>
            
            <h3>Order Details</h3>
            <p><strong>Order ID:</strong> {order_id}</p>
            
            <h3>Custom Cake Specifications</h3>
            <ul>
                <li><strong>Pound:</strong> {pound} lb</li>
                <li><strong>Flavour:</strong> {flavour}</li>
                <li><strong>Description:</strong> {description}</li>
            </ul>
            
            <h3>Estimated Price: Rs. {estimated_price}</h3>
            <p><em>Final price may vary based on design.</em></p>
            
            <p>We will contact you shortly to discuss design details and confirm the final price.</p>
            <p>Thank you for choosing Saista Bakers!</p>
        </body>
    </html>
    """
    
    return send_email(email, subject, body)

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
        return jsonify({'status': 'healthy', 'service': 'order-service'}), 200
    except Exception as e:
        return jsonify({'status': 'unhealthy', 'error': str(e)}), 500

@app.route('/cart', methods=['POST'])
@jwt_required()
def add_to_cart():
    """Add product to cart (store in session/order)"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Create or get pending order
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Check if user has pending order
        cursor.execute("SELECT id FROM orders WHERE user_id = %s AND status = 'cart'", (user_id,))
        order = cursor.fetchone()
        
        if not order:
            # Create new cart order
            cursor.execute(
                "INSERT INTO orders (user_id, total_price, status) VALUES (%s, 0, 'cart')",
                (user_id,)
            )
            conn.commit()
            order_id = cursor.lastrowid
        else:
            order_id = order[0]
        
        # Add item to order
        product_id = data.get('product_id')
        quantity = data.get('quantity', 1)
        
        # Get product price
        cursor.execute("SELECT price FROM products WHERE id = %s", (product_id,))
        product = cursor.fetchone()
        
        if not product:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Product not found'}), 404
        
        price_at_purchase = product[0]
        
        # Check if item already in cart
        cursor.execute(
            "SELECT id, quantity FROM order_items WHERE order_id = %s AND product_id = %s",
            (order_id, product_id)
        )
        existing_item = cursor.fetchone()
        
        if existing_item:
            # Update quantity
            new_quantity = existing_item[1] + quantity
            cursor.execute(
                "UPDATE order_items SET quantity = %s WHERE id = %s",
                (new_quantity, existing_item[0])
            )
        else:
            # Add new item
            cursor.execute(
                "INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)",
                (order_id, product_id, quantity, price_at_purchase)
            )
        
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({
            'message': 'Item added to cart',
            'order_id': order_id
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cart/<int:order_id>', methods=['GET'])
@jwt_required()
def get_cart(order_id):
    """Get cart items"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify order belongs to user
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cart not found'}), 404
        
        # Get cart items
        cursor.execute("""
            SELECT oi.id, oi.product_id, p.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        items = cursor.fetchall()
        cursor.close()
        conn.close()
        
        cart_items = []
        total = 0
        for item in items:
            item_total = item[4] * item[3]
            total += item_total
            cart_items.append({
                'id': item[0],
                'product_id': item[1],
                'name': item[2],
                'quantity': item[3],
                'price': float(item[4]),
                'item_total': float(item_total)
            })
        
        return jsonify({
            'order_id': order_id,
            'items': cart_items,
            'total': float(total)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/cart/<int:order_id>/item/<int:item_id>', methods=['DELETE'])
@jwt_required()
def remove_from_cart(order_id, item_id):
    """Remove item from cart"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify order belongs to user
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cart not found'}), 404
        
        # Delete item
        cursor.execute("DELETE FROM order_items WHERE id = %s AND order_id = %s", (item_id, order_id))
        conn.commit()
        
        cursor.close()
        conn.close()
        
        return jsonify({'message': 'Item removed from cart'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/order', methods=['POST'])
@jwt_required()
def place_order():
    """Place order from cart"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        order_id = data.get('order_id')
        delivery_address = data.get('delivery_address')
        delivery_date = data.get('delivery_date')
        
        if not delivery_address or not delivery_date:
            return jsonify({'error': 'Missing delivery address or date'}), 400
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Verify order is cart
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_id, user_id))
        if not cursor.fetchone():
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cart not found'}), 404
        
        # Get cart items and calculate total
        cursor.execute("""
            SELECT SUM(oi.quantity * oi.price_at_purchase)
            FROM order_items oi
            WHERE oi.order_id = %s
        """, (order_id,))
        
        total = cursor.fetchone()[0]
        if not total:
            cursor.close()
            conn.close()
            return jsonify({'error': 'Cart is empty'}), 400
        
        # Update order
        cursor.execute("""
            UPDATE orders 
            SET status = 'pending', total_price = %s, delivery_address = %s, delivery_date = %s
            WHERE id = %s
        """, (total, delivery_address, delivery_date, order_id))
        
        # Get order items
        cursor.execute("""
            SELECT p.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        
        items = cursor.fetchall()
        items_list = [{'name': item[0], 'quantity': item[1], 'price_at_purchase': item[2]} for item in items]
        
        # Get user email
        cursor.execute("SELECT email, full_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        conn.commit()
        cursor.close()
        conn.close()
        
        # Send confirmation email
        if user:
            send_order_confirmation_email(user[0], user[1], order_id, items_list, total)
        
        return jsonify({
            'message': 'Order placed successfully',
            'order_id': order_id,
            'total_price': float(total),
            'status': 'pending'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/custom-cake', methods=['POST'])
@jwt_required()
def create_custom_order():
    """Create custom cake order"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        pound = data.get('pound')
        flavour = data.get('flavour')
        description = data.get('description')
        delivery_date = data.get('delivery_date')
        
        if not pound or not flavour or not description:
            return jsonify({'error': 'Missing required fields'}), 400
        
        # Validate inputs
        if not isinstance(pound, int) or pound < 1:
            return jsonify({'error': 'Pound must be a positive integer'}), 400
        
        if flavour not in ['fruit', 'chocolate', 'fondant']:
            return jsonify({'error': 'Invalid flavour. Choose from: fruit, chocolate, fondant'}), 400
        
        # Calculate estimated price
        estimated_price = calculate_custom_price(pound, flavour)
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        # Insert custom order
        cursor.execute("""
            INSERT INTO custom_orders (user_id, pound, flavour, description, estimated_price, delivery_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, pound, flavour, description, estimated_price, delivery_date))
        
        conn.commit()
        order_id = cursor.lastrowid
        
        # Get user email
        cursor.execute("SELECT email, full_name FROM users WHERE id = %s", (user_id,))
        user = cursor.fetchone()
        
        cursor.close()
        conn.close()
        
        # Send confirmation email
        if user:
            send_custom_cake_confirmation_email(
                user[0], user[1], order_id, pound, flavour, description, estimated_price
            )
        
        return jsonify({
            'message': 'Custom cake order created successfully',
            'order_id': order_id,
            'pound': pound,
            'flavour': flavour,
            'estimated_price': float(estimated_price),
            'note': 'Final price may vary based on design.'
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/custom-cake/<int:order_id>', methods=['GET'])
@jwt_required()
def get_custom_order(order_id):
    """Get custom cake order details"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pound, flavour, description, estimated_price, final_price, status, delivery_date
            FROM custom_orders
            WHERE id = %s AND user_id = %s
        """, (order_id, user_id))
        
        order = cursor.fetchone()
        cursor.close()
        conn.close()
        
        if not order:
            return jsonify({'error': 'Custom order not found'}), 404
        
        return jsonify({
            'id': order[0],
            'pound': order[1],
            'flavour': order[2],
            'description': order[3],
            'estimated_price': float(order[4]),
            'final_price': float(order[5]) if order[5] else None,
            'status': order[6],
            'delivery_date': order[7]
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/orders', methods=['GET'])
@jwt_required()
def get_user_orders():
    """Get all orders for user"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, total_price, status, delivery_date, created_at
            FROM orders
            WHERE user_id = %s AND status != 'cart'
            ORDER BY created_at DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        order_list = []
        for order in orders:
            order_list.append({
                'id': order[0],
                'total_price': float(order[1]),
                'status': order[2],
                'delivery_date': order[3],
                'created_at': order[4].isoformat()
            })
        
        return jsonify({
            'orders': order_list,
            'total': len(order_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/custom-cakes', methods=['GET'])
@jwt_required()
def get_user_custom_cakes():
    """Get all custom cake orders for user"""
    try:
        user_id = get_jwt_identity()
        
        conn = get_db_connection()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT id, pound, flavour, description, estimated_price, final_price, status, created_at
            FROM custom_orders
            WHERE user_id = %s
            ORDER BY created_at DESC
        """, (user_id,))
        
        orders = cursor.fetchall()
        cursor.close()
        conn.close()
        
        order_list = []
        for order in orders:
            order_list.append({
                'id': order[0],
                'pound': order[1],
                'flavour': order[2],
                'description': order[3],
                'estimated_price': float(order[4]),
                'final_price': float(order[5]) if order[5] else None,
                'status': order[6],
                'created_at': order[7].isoformat()
            })
        
        return jsonify({
            'custom_cakes': order_list,
            'total': len(order_list)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5002)
