from fastapi import FastAPI, HTTPException, Depends, status
from fastapi.security import OAuth2PasswordBearer
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from jose import JWTError, jwt
from datetime import datetime
import mysql.connector
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from dotenv import load_dotenv

# Load .env from parent directory (service root)
load_dotenv(dotenv_path=Path(__file__).parent.parent / ".env")

app = FastAPI(title="Saista Bakers Order Service")

# Configuration
SECRET_KEY = "your-secret-key-change-this-in-production"
ALGORITHM = "HS256"

DB_CONFIG = {
    'host': os.getenv('DB_HOST', 'localhost'),
    'user': os.getenv('DB_USER', 'root'),
    'password': os.getenv('DB_PASSWORD', 'Asad@1234'),
    'database': os.getenv('DB_NAME', 'saista_bakers'),
    'port': int(os.getenv('DB_PORT', 3306))
}

EMAIL_CONFIG = {
    'smtp_server': os.getenv('SMTP_SERVER', 'localhost'),
    'smtp_port': int(os.getenv('SMTP_PORT', 1025)),
    'sender_email': os.getenv('SENDER_EMAIL', 'noreply@saista-bakers.com'),
}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def get_db_connection():
    try:
        return mysql.connector.connect(**DB_CONFIG)
    except mysql.connector.Error as err:
        print(f"Error: {err}")
        raise HTTPException(status_code=500, detail="Database connection failed")

def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return int(user_id)

# Email functions
def send_email(recipient_email, subject, body):
    """Send HTML email. Fails silently if SMTP not configured."""
    try:
        smtp_server = EMAIL_CONFIG['smtp_server']
        smtp_port = EMAIL_CONFIG['smtp_port']
        sender = EMAIL_CONFIG['sender_email']
        smtp_user = os.getenv('SMTP_USER', '')
        smtp_pass = os.getenv('SMTP_PASSWORD', '')

        msg = MIMEMultipart('alternative')
        msg['From'] = sender
        msg['To'] = recipient_email
        msg['Subject'] = subject
        msg.attach(MIMEText(body, 'html'))

        if smtp_port == 465:
            server = smtplib.SMTP_SSL(smtp_server, smtp_port)
        else:
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.ehlo()
            if smtp_port == 587:
                server.starttls()
                server.ehlo()

        if smtp_user and smtp_pass:
            server.login(smtp_user, smtp_pass)

        server.send_message(msg)
        server.quit()
        print(f"✓ Email sent to {recipient_email}")
        return True
    except Exception as e:
        print(f"Email sending skipped (SMTP not configured): {str(e)}")
        return False

# Pricing logic for Custom Cakes
def calculate_custom_price(pound: int, flavour: str):
    base_price = 300
    extra_pound_price = 200
    
    # Specific fruit flavours add 100, chocolate adds 200, fondant adds 250
    flavour_surcharge = {
        'Strawberry': 100,
        'Mango': 100,
        'Pineapple': 100,
        'Blueberry': 100,
        'Chocolate': 200,
        'Fondant': 250
    }
    
    price = base_price if pound <= 1 else base_price + (pound - 1) * extra_pound_price
    flavour_charge = flavour_surcharge.get(flavour, 0) * pound
    return price + flavour_charge

# Models
class CartItemAdd(BaseModel):
    product_id: int
    quantity: int = 1

class OrderPlace(BaseModel):
    order_id: int
    delivery_address: str
    delivery_date: str

class CustomCakeCreate(BaseModel):
    pound: int
    flavour: str
    description: str
    delivery_date: str

# Routes
@app.get("/health")
def health():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT 1")
    cursor.fetchone()
    cursor.close()
    conn.close()
    return {"status": "healthy", "service": "order-service"}

@app.post("/cart", status_code=201)
def add_to_cart(item: CartItemAdd, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM orders WHERE user_id = %s AND status = 'cart'", (user_id,))
        order = cursor.fetchone()
        
        if not order:
            cursor.execute("INSERT INTO orders (user_id, total_price, status) VALUES (%s, 0, 'cart')", (user_id,))
            conn.commit()
            order_id = cursor.lastrowid
        else:
            order_id = order[0]
            
        cursor.execute("SELECT price FROM products WHERE id = %s", (item.product_id,))
        product = cursor.fetchone()
        if not product:
            raise HTTPException(status_code=404, detail="Product not found")
            
        price_at_purchase = product[0]
        
        cursor.execute("SELECT id, quantity FROM order_items WHERE order_id = %s AND product_id = %s", (order_id, item.product_id))
        existing_item = cursor.fetchone()
        
        if existing_item:
            cursor.execute("UPDATE order_items SET quantity = %s WHERE id = %s", (existing_item[1] + item.quantity, existing_item[0]))
        else:
            cursor.execute("INSERT INTO order_items (order_id, product_id, quantity, price_at_purchase) VALUES (%s, %s, %s, %s)",
                           (order_id, item.product_id, item.quantity, price_at_purchase))
        
        conn.commit()
        return {"message": "Item added to cart", "order_id": order_id}
    finally:
        cursor.close()
        conn.close()

@app.get("/cart/{order_id}")
def get_cart(order_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cart not found")
            
        cursor.execute("""
            SELECT oi.id, oi.product_id, p.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi
            JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_id,))
        items = cursor.fetchall()
        
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
            
        return {"order_id": order_id, "items": cart_items, "total": float(total)}
    finally:
        cursor.close()
        conn.close()

@app.delete("/cart/{order_id}/item/{item_id}")
def remove_from_cart(order_id: int, item_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cart not found")
            
        cursor.execute("DELETE FROM order_items WHERE id = %s AND order_id = %s", (item_id, order_id))
        conn.commit()
        return {"message": "Item removed from cart"}
    finally:
        cursor.close()
        conn.close()

@app.post("/order", status_code=201)
def place_order(order_req: OrderPlace, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id FROM orders WHERE id = %s AND user_id = %s AND status = 'cart'", (order_req.order_id, user_id))
        if not cursor.fetchone():
            raise HTTPException(status_code=404, detail="Cart not found")
            
        cursor.execute("SELECT SUM(quantity * price_at_purchase) FROM order_items WHERE order_id = %s", (order_req.order_id,))
        total = cursor.fetchone()[0]
        if not total:
            raise HTTPException(status_code=400, detail="Cart is empty")
        
        # Get order items for email
        cursor.execute("""
            SELECT p.name, oi.quantity, oi.price_at_purchase
            FROM order_items oi JOIN products p ON oi.product_id = p.id
            WHERE oi.order_id = %s
        """, (order_req.order_id,))
        items = cursor.fetchall()
            
        cursor.execute("""
            UPDATE orders SET status = 'pending', total_price = %s, delivery_address = %s, delivery_date = %s
            WHERE id = %s
        """, (total, order_req.delivery_address, order_req.delivery_date, order_req.order_id))
        conn.commit()
        
        # Get user email for notification
        cursor.execute("SELECT email, username FROM users WHERE id = %s", (user_id,))
        user_row = cursor.fetchone()
        if user_row:
            user_email, username = user_row
            # Build email body
            items_html = "".join([
                f"<tr><td style='padding:8px;border-bottom:1px solid #f0f0f0'>{i[0]}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #f0f0f0;text-align:center'>{i[1]}</td>"
                f"<td style='padding:8px;border-bottom:1px solid #f0f0f0;text-align:right'>Rs. {float(i[1]*i[2]):.2f}</td></tr>"
                for i in items
            ])
            email_body = f"""
            <div style="font-family:Arial,sans-serif;max-width:600px;margin:0 auto;padding:20px">
              <div style="background:linear-gradient(135deg,#f7cac9,#a7d7c5);padding:30px;border-radius:15px;text-align:center;margin-bottom:25px">
                <h1 style="font-family:Georgia,serif;color:#3d2b1f;margin:0">🎂 Saista Bakers</h1>
                <p style="color:#6b5044;margin:5px 0 0">Order Confirmation</p>
              </div>
              <p>Dear <strong>{username}</strong>,</p>
              <p>Your order has been placed successfully! Here are the details:</p>
              <table style="width:100%;border-collapse:collapse;margin:20px 0">
                <thead><tr style="background:#f7cac9">
                  <th style="padding:10px;text-align:left">Item</th>
                  <th style="padding:10px;text-align:center">Qty</th>
                  <th style="padding:10px;text-align:right">Price</th>
                </tr></thead>
                <tbody>{items_html}</tbody>
              </table>
              <p style="text-align:right;font-size:1.2em"><strong>Total: Rs. {float(total):.2f}</strong></p>
              <p>📍 <strong>Delivery to:</strong> {order_req.delivery_address}</p>
              <p>📅 <strong>Delivery Date:</strong> {order_req.delivery_date}</p>
              <div style="background:#f0faf6;border-radius:12px;padding:20px;margin:20px 0;border-left:4px solid #a7d7c5">
                <h3 style="color:#3a9a82;margin-top:0">💳 Payment Instructions</h3>
                <p>Please complete payment within 24 hours using any of these methods:</p>
                <ul>
                  <li><strong>EasyPaisa:</strong> 0300-1234567 (Saista Bakers)</li>
                  <li><strong>JazzCash:</strong> 0300-1234567 (Saista Bakers)</li>
                  <li><strong>Bank Transfer:</strong> HBL - 0123-4567890 (Saista Bakers)</li>
                  <li><strong>Cash on Delivery</strong> available for orders above Rs. 500</li>
                </ul>
                <p style="font-size:0.85em;color:#888">Please send payment screenshot to WhatsApp: 0300-1234567</p>
              </div>
              <p style="color:#aaa;font-size:0.85em">Our team will contact you within 2 hours to confirm your order.</p>
              <hr style="border:none;border-top:1px solid #f0f0f0;margin:20px 0">
              <p style="color:#bbb;font-size:0.8em;text-align:center">Saista Bakers | Crafted with Love ❤️</p>
            </div>"""
            send_email(user_email, f"Order Confirmation #{order_req.order_id} - Saista Bakers", email_body)
        
        return {"message": "Order placed successfully", "order_id": order_req.order_id, "total_price": float(total), "status": "pending"}
    finally:
        cursor.close()
        conn.close()

@app.post("/custom-cake", status_code=201)
def create_custom_order(cake: CustomCakeCreate, user_id: int = Depends(get_current_user)):
    if cake.pound < 1:
        raise HTTPException(status_code=400, detail="Pound must be a positive integer")
    if cake.flavour not in ['Strawberry', 'Mango', 'Pineapple', 'Blueberry', 'Chocolate', 'Fondant']:
        raise HTTPException(status_code=400, detail="Invalid flavour")
        
    estimated_price = calculate_custom_price(cake.pound, cake.flavour)
    
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            INSERT INTO custom_orders (user_id, pound, flavour, description, estimated_price, delivery_date)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (user_id, cake.pound, cake.flavour, cake.description, estimated_price, cake.delivery_date))
        conn.commit()
        order_id = cursor.lastrowid
        return {
            "message": "Custom cake order created successfully",
            "order_id": order_id,
            "pound": cake.pound,
            "flavour": cake.flavour,
            "estimated_price": float(estimated_price),
            "note": "Final price may vary based on design."
        }
    finally:
        cursor.close()
        conn.close()

@app.get("/custom-cake/{order_id}")
def get_custom_order(order_id: int, user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("""
            SELECT id, pound, flavour, description, estimated_price, final_price, status, delivery_date
            FROM custom_orders WHERE id = %s AND user_id = %s
        """, (order_id, user_id))
        order = cursor.fetchone()
        if not order:
            raise HTTPException(status_code=404, detail="Custom order not found")
            
        return {
            "id": order[0], "pound": order[1], "flavour": order[2], "description": order[3],
            "estimated_price": float(order[4]), "final_price": float(order[5]) if order[5] else None,
            "status": order[6], "delivery_date": order[7]
        }
    finally:
        cursor.close()
        conn.close()

@app.get("/orders")
def get_user_orders(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, total_price, status, delivery_date, created_at FROM orders WHERE user_id = %s AND status != 'cart' ORDER BY created_at DESC", (user_id,))
        orders = cursor.fetchall()
        order_list = [
            {"id": o[0], "total_price": float(o[1]), "status": o[2], "delivery_date": o[3], "created_at": o[4].isoformat()}
            for o in orders
        ]
        return {"orders": order_list, "total": len(order_list)}
    finally:
        cursor.close()
        conn.close()

@app.get("/custom-cakes")
def get_user_custom_cakes(user_id: int = Depends(get_current_user)):
    conn = get_db_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT id, pound, flavour, description, estimated_price, final_price, status, created_at FROM custom_orders WHERE user_id = %s ORDER BY created_at DESC", (user_id,))
        orders = cursor.fetchall()
        order_list = [
            {"id": o[0], "pound": o[1], "flavour": o[2], "description": o[3], "estimated_price": float(o[4]), 
             "final_price": float(o[5]) if o[5] else None, "status": o[6], "created_at": o[7].isoformat()}
            for o in orders
        ]
        return {"custom_cakes": order_list, "total": len(order_list)}
    finally:
        cursor.close()
        conn.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=5002, reload=True)
