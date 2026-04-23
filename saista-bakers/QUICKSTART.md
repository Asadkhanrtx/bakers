# Quick Start Guide - Saista Bakers

## Fastest Way to Run the Application (5 minutes)

### Prerequisites
- Docker Desktop installed

### Steps

1. **Navigate to project folder:**
   ```bash
   cd saista-bakers
   ```

2. **Start all services:**
   ```bash
   docker-compose up --build
   ```

3. **Wait for startup (watch for green checks):**
   - MySQL: ✓ Ready
   - MailHog: ✓ Ready
   - User Service: ✓ Running
   - Order Service: ✓ Running
   - Frontend: ✓ Running

4. **Open your browser:**
   - Frontend: http://localhost:3000

5. **Create an account and start ordering!**

---

## Access Points

| Service | URL | Purpose |
|---------|-----|---------|
| Frontend | http://localhost:3000 | Web Application |
| User Service API | http://localhost:5001 | Authentication & Products |
| Order Service API | http://localhost:5002 | Orders & Custom Cakes |
| MailHog (Emails) | http://localhost:8025 | View test emails |
| MySQL | localhost:3306 | Database (user: baker, pass: baker123) |

---

## Test Flow

1. **Sign Up** - Create a new account
2. **Browse Products** - View available cakes and cookies
3. **Add to Cart** - Select products and quantities
4. **Place Order** - Checkout with delivery address and date
5. **Check Email** - View order confirmation in MailHog
6. **Custom Cake** - Design a custom cake with pricing
7. **View Orders** - See all placed orders and custom cakes

---

## Sample Test Account

You can sign up with any credentials. Example:
- Username: `testuser`
- Email: `test@example.com`
- Password: `password123`

---

## Stopping the Application

```bash
docker-compose down
```

---

## Troubleshooting

### Services won't start?
```bash
docker-compose down -v  # Remove volumes
docker-compose up --build  # Start fresh
```

### Frontend shows blank page?
- Wait 30 seconds for frontend to build
- Refresh the browser (Ctrl+R or Cmd+R)
- Check browser console for errors (F12)

### Can't see MailHog emails?
- Check MailHog is running: http://localhost:8025
- Emails appear instantly when order is placed
- Check browser dev tools for errors

### API errors?
- Ensure all services started without errors
- Check service logs: `docker-compose logs [service-name]`
- Restart: `docker-compose restart`

---

## For Local Development (Without Docker)

See README.md for detailed local setup instructions.

---

## Default Products in Database

1. **Chocolate Cake** - Rs. 500
2. **Vanilla Cake** - Rs. 400
3. **Red Velvet** - Rs. 600
4. **Chocolate Cookies** - Rs. 150
5. **Sugar Cookies** - Rs. 150
6. **Oatmeal Cookies** - Rs. 180

---

## Features to Try

✅ User Authentication (JWT)
✅ Product Browsing & Filtering
✅ Shopping Cart
✅ Order Placement
✅ Email Confirmations
✅ Custom Cake Orders
✅ Dynamic Pricing Calculation
✅ Order History

---

## Database Access

```bash
# Access MySQL from Docker
docker exec -it saista-mysql mysql -u baker -pbaker123 saista_bakers

# View tables
SHOW TABLES;
SELECT * FROM products;
SELECT * FROM orders;
```

---

Happy Baking! 🎂
