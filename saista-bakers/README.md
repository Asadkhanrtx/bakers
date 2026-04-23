# Saista Bakers - Microservices Application

A complete microservices-based bakery management system built with React, Flask, and MySQL. This application allows users to browse products, place regular orders, and customize cakes with dynamic pricing.

## Project Overview

### Architecture

The application consists of 3 main microservices:

1. **Frontend Service** - React.js application for user interface
2. **User Service** - Flask REST API for authentication and product management
3. **Order Service** - Flask REST API for cart, orders, and custom cakes

### Tech Stack

- **Frontend:** React.js, React Router, Axios
- **Backend:** Python Flask, Flask-JWT-Extended, Flask-CORS
- **Database:** MySQL 8.0
- **Authentication:** JWT (JSON Web Tokens)
- **Email:** SMTP with MailHog (for local development)
- **Containerization:** Docker & Docker Compose

## Project Structure

```
saista-bakers/
├── frontend/                 # React frontend application
│   ├── public/              # Static files
│   ├── src/
│   │   ├── pages/           # Page components (Login, Products, Cart, etc.)
│   │   ├── api/             # API client configurations
│   │   ├── styles/          # CSS files
│   │   ├── App.js           # Main app component
│   │   └── index.js         # Entry point
│   ├── package.json
│   └── Dockerfile
├── user-service/            # User & Product REST API
│   ├── app/
│   │   └── app.py           # Flask application
│   ├── requirements.txt
│   └── Dockerfile
├── order-service/           # Order & Custom Cake REST API
│   ├── app/
│   │   └── app.py           # Flask application
│   ├── requirements.txt
│   └── Dockerfile
├── database/
│   └── schema.sql           # MySQL database schema
├── docker/
│   ├── Dockerfile.frontend
│   ├── Dockerfile.user-service
│   └── Dockerfile.order-service
├── docker-compose.yml       # Docker Compose configuration
└── README.md
```

## Features

### User Authentication
- User signup with email validation
- User login with JWT tokens
- Secure password hashing

### Product System
- Browse all products (cakes, cookies)
- Filter products by category
- Product details with pricing

### Shopping Cart
- Add products to cart
- View cart items
- Remove items from cart
- Place orders with delivery details

### Custom Cake Feature
- Design custom cakes with specifications:
  - Weight (pounds): 1-8 lb
  - Flavour: Fruit, Chocolate, Fondant
  - Custom description
- Dynamic price calculation:
  - Base: Rs. 300 for 1 lb
  - Extra pound: +Rs. 200
  - Fruit per pound: +Rs. 100
  - Chocolate per pound: +Rs. 200
  - Fondant per pound: +Rs. 250
- Email confirmation with estimated price

### Order Management
- View all placed orders
- View custom cake orders
- Order status tracking
- Email notifications on order placement

### Email Notifications
- Order confirmation emails
- Custom cake order confirmation emails
- Email delivery via MailHog (local development)

## Prerequisites

### For Docker (Recommended)

- Docker Desktop installed and running
- Docker Compose installed (usually comes with Docker Desktop)

### For Local Development

- Node.js (v14 or higher)
- Python 3.9 or higher
- MySQL 8.0 or higher
- npm or yarn

## Installation & Setup

### Option 1: Using Docker Compose (Recommended - Easiest)

1. **Clone/Navigate to the project:**
   ```bash
   cd saista-bakers
   ```

2. **Build and start all services:**
   ```bash
   docker-compose up --build
   ```
   
   This command will:
   - Build Docker images for all services
   - Start MySQL database
   - Initialize the database schema
   - Start MailHog (email testing)
   - Start User Service (port 5001)
   - Start Order Service (port 5002)
   - Start Frontend (port 3000)

3. **Wait for services to start:**
   ```
   Watch for messages like:
   - "MySQL is ready for connections"
   - "User-service is running on port 5001"
   - "Order-service is running on port 5002"
   - "Frontend is running on port 3000"
   ```

4. **Access the application:**
   - Frontend: http://localhost:3000
   - User Service API: http://localhost:5001
   - Order Service API: http://localhost:5002
   - MailHog (Email testing): http://localhost:8025

5. **Stop all services:**
   ```bash
   docker-compose down
   ```

### Option 2: Local Development Setup

#### Step 1: Setup MySQL Database

1. Create the database and import schema:
   ```bash
   mysql -u root -p < database/schema.sql
   ```
   Or create manually:
   ```bash
   mysql -u root -p
   ```
   ```sql
   source database/schema.sql;
   ```

2. Verify database creation:
   ```bash
   USE saista_bakers;
   SHOW TABLES;
   ```

#### Step 2: Setup User Service

1. Navigate to user-service:
   ```bash
   cd user-service
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment:
   - **Windows:**
     ```bash
     venv\Scripts\activate
     ```
   - **macOS/Linux:**
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the service:
   ```bash
   python app/app.py
   ```
   
   Service will be available at: http://localhost:5001

#### Step 3: Setup Order Service

1. In a new terminal, navigate to order-service:
   ```bash
   cd order-service
   ```

2. Create virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate virtual environment (same as Step 2.3)

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the service:
   ```bash
   python app/app.py
   ```
   
   Service will be available at: http://localhost:5002

#### Step 4: Setup Frontend

1. In a new terminal, navigate to frontend:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Create .env file:
   ```bash
   echo "REACT_APP_USER_SERVICE_URL=http://localhost:5001" > .env
   echo "REACT_APP_ORDER_SERVICE_URL=http://localhost:5002" >> .env
   ```

4. Start the development server:
   ```bash
   npm start
   ```
   
   Frontend will be available at: http://localhost:3000

## API Endpoints

### User Service (Port 5001)

#### Authentication
- `POST /signup` - Create new user account
- `POST /login` - Login user, returns JWT token

#### Products
- `GET /products` - Get all products
- `GET /products?category=Cakes` - Get products by category
- `GET /products/categories` - Get all product categories
- `GET /products/<id>` - Get single product details

#### User
- `GET /profile` - Get current user profile (requires JWT)
- `GET /users/<id>` - Get user information

### Order Service (Port 5002)

#### Cart
- `POST /cart` - Add product to cart (requires JWT)
- `GET /cart/<order_id>` - Get cart items (requires JWT)
- `DELETE /cart/<order_id>/item/<item_id>` - Remove item from cart (requires JWT)

#### Orders
- `POST /order` - Place order from cart (requires JWT)
- `GET /orders` - Get all user orders (requires JWT)

#### Custom Cakes
- `POST /custom-cake` - Create custom cake order (requires JWT)
- `GET /custom-cake/<order_id>` - Get custom cake order details (requires JWT)
- `GET /custom-cakes` - Get all user custom cake orders (requires JWT)

## Database Schema

### Users Table
- User authentication information
- Profile details (name, phone, address)

### Products Table
- Available products (cakes, cookies)
- Pricing and category information
- Product descriptions

### Orders Table
- Regular product orders
- Order status and pricing
- Delivery details

### Order Items Table
- Individual items in each order
- Pricing at time of purchase

### Custom Orders Table
- Custom cake orders
- Design specifications
- Estimated and final pricing

## Authentication

The application uses JWT (JSON Web Tokens) for authentication:

1. User signs up or logs in
2. Server returns JWT token
3. Token is stored in browser's localStorage
4. Token is sent with each API request in the Authorization header
5. Server validates token and processes the request

**Example API Request:**
```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
     http://localhost:5002/orders
```

## Custom Cake Pricing Logic

### Formula:
```
Base Price = 300 (for 1 pound)

For weights > 1 pound:
Base = 300 + (weight - 1) × 200

Flavour Surcharge (per pound):
- Fruit: +100
- Chocolate: +200
- Fondant: +250

Total Price = Base + (Flavour Surcharge × Weight)
```

### Examples:
- 1 lb Fruit cake: 300 + (100 × 1) = Rs. 400
- 2 lb Chocolate cake: (300 + 200) + (200 × 2) = Rs. 900
- 3 lb Fondant cake: (300 + 400) + (250 × 3) = Rs. 1,450

## Email Configuration

### Development (MailHog)

MailHog is included in docker-compose for testing emails locally:

1. SMTP Server: localhost:1025
2. Web UI: http://localhost:8025
3. All emails sent during testing can be viewed in MailHog web interface

### Production

To use a real email service, modify the email configuration in `order-service/app/app.py`:

```python
EMAIL_CONFIG = {
    'smtp_server': 'smtp.gmail.com',  # Your SMTP server
    'smtp_port': 587,
    'sender_email': 'your-email@gmail.com',
    'sender_password': 'your-app-password'
}
```

## Sample Test Users & Products

The database is automatically populated with:

**Sample Products:**
- Chocolate Cake (Rs. 500)
- Vanilla Cake (Rs. 400)
- Red Velvet (Rs. 600)
- Chocolate Cookies (Rs. 150)
- Sugar Cookies (Rs. 150)
- Oatmeal Cookies (Rs. 180)

**Create Users:**
Sign up through the frontend interface at http://localhost:3000

## Troubleshooting

### Port Already in Use
If a port is already in use, you can change it:

**Docker Compose:**
Edit `docker-compose.yml` and change the port mappings

**Local Development:**
Edit the Flask app.py files:
```python
app.run(port=5003)  # Change 5003 to your preferred port
```

### Database Connection Error
1. Ensure MySQL is running
2. Check credentials in `.env` file
3. For Docker: ensure mysql service is healthy

### Frontend Can't Connect to API
1. Check API URLs in frontend `.env` file
2. Ensure both services are running
3. Check browser console for CORS errors
4. For Docker: services should use `http://service-name:port`

### Email Not Sending
1. Check MailHog is running (docker-compose only)
2. Verify SMTP configuration in order-service
3. Check email logs in MailHog web UI

## Development Notes

### Adding New Products
Edit `database/schema.sql` and add to the INSERT statement:
```sql
INSERT INTO products (name, description, price, category) VALUES
('Your Product', 'Description', 500, 'Category');
```

### Modifying Pricing Logic
Edit the `calculate_custom_price()` function in `order-service/app/app.py`

### Adding New Routes
Add new endpoints to the Flask apps in `user-service/app/app.py` or `order-service/app/app.py`

## Production Deployment

For production deployment:

1. Use strong JWT secret key (change in app.py)
2. Set `FLASK_ENV=production`
3. Use a production-grade SMTP server
4. Use environment variables for sensitive data
5. Enable HTTPS/SSL
6. Use a reverse proxy (Nginx)
7. Configure proper CORS settings
8. Use a process manager (Gunicorn)

## Security Considerations

- Passwords are hashed using werkzeug.security
- JWT tokens expire after 30 days
- CORS is enabled for all origins (configure for production)
- SQL injection is prevented using parameterized queries
- CSRF protection should be added for production

## API Response Examples

### Login Success
```json
{
  "message": "Login successful",
  "user_id": 1,
  "username": "john_doe",
  "full_name": "John Doe",
  "email": "john@example.com",
  "access_token": "eyJ0eXAiOiJKV1QiLC..."
}
```

### Custom Cake Order
```json
{
  "message": "Custom cake order created successfully",
  "order_id": 1,
  "pound": 2,
  "flavour": "chocolate",
  "estimated_price": 900.0,
  "note": "Final price may vary based on design."
}
```

### Cart Items
```json
{
  "order_id": 1,
  "items": [
    {
      "id": 1,
      "product_id": 1,
      "name": "Chocolate Cake",
      "quantity": 1,
      "price": 500,
      "item_total": 500
    }
  ],
  "total": 500
}
```

## License

This project is open source and available for educational purposes.

## Support

For issues, questions, or suggestions, please check the repository or contact the development team.

---

**Happy Baking! 🎂**
