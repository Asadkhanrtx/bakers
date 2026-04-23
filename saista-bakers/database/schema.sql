-- Saista Bakers Database Schema

CREATE DATABASE IF NOT EXISTS saista_bakers;
USE saista_bakers;

-- Users Table
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(120) UNIQUE NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    full_name VARCHAR(120),
    phone VARCHAR(20),
    address TEXT,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Products Table
CREATE TABLE IF NOT EXISTS products (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(120) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL,
    category VARCHAR(50) NOT NULL,
    available BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

-- Orders Table
CREATE TABLE IF NOT EXISTS orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    total_price DECIMAL(10, 2) NOT NULL,
    status VARCHAR(50) DEFAULT 'pending',
    delivery_date DATE,
    delivery_address TEXT,
    email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Order Items Table
CREATE TABLE IF NOT EXISTS order_items (
    id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    product_id INT,
    quantity INT NOT NULL DEFAULT 1,
    price_at_purchase DECIMAL(10, 2) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- Custom Orders Table
CREATE TABLE IF NOT EXISTS custom_orders (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    pound INT NOT NULL,
    flavour VARCHAR(50) NOT NULL,
    description TEXT,
    estimated_price DECIMAL(10, 2) NOT NULL,
    final_price DECIMAL(10, 2),
    status VARCHAR(50) DEFAULT 'pending',
    delivery_date DATE,
    email_sent BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

-- Insert sample products
INSERT INTO products (name, description, price, category) VALUES
-- Cakes
('Vanilla Cake', 'Classic vanilla sponge cake with fluffy buttercream frosting', 400.00, 'Cakes'),
('Chocolate Cake', 'Rich chocolate cake, perfect for chocolate lovers', 500.00, 'Cakes'),
('Black Forest Cake', 'Layers of chocolate sponge, cherries, and whipped cream', 550.00, 'Cakes'),
('White Forest Cake', 'Vanilla sponge with white chocolate flakes and cherries', 550.00, 'Cakes'),
('Red Velvet Cake', 'Delicious red velvet with premium cream cheese frosting', 600.00, 'Cakes'),
('Blueberry Cake', 'Light sponge cake infused with fresh blueberry compote', 600.00, 'Cakes'),
('Butterscotch Cake', 'Caramel-flavored sponge with crunchy butterscotch bits', 500.00, 'Cakes'),
('Pineapple Cake', 'Tropical delight with fresh pineapple chunks and cream', 450.00, 'Cakes'),
('KitKat Cake', 'Chocolate cake surrounded by crunchy KitKat bars', 700.00, 'Cakes'),
('Ferrero Rocher Cake', 'Premium hazelnut chocolate cake topped with Ferrero Rocher', 800.00, 'Cakes'),
('Oreo Cake', 'Cookies and cream cake packed with crushed Oreos', 650.00, 'Cakes'),
('Truffle Cake', 'Dense chocolate truffle cake with a glossy ganache finish', 700.00, 'Cakes'),

-- Cookies
('Butter Cookies', 'Melt-in-your-mouth classic butter cookies', 150.00, 'Cookies'),
('Chocolate Chip Cookies', 'Homemade soft and chewy chocolate chip cookies', 180.00, 'Cookies'),
('Oatmeal Cookies', 'Healthy oatmeal raisin cookies, perfectly spiced', 180.00, 'Cookies'),
('Almond Cookies', 'Crunchy cookies loaded with roasted almonds', 200.00, 'Cookies'),
('Cashew Cookies', 'Rich and buttery cookies packed with premium cashews', 200.00, 'Cookies'),
('Double Chocolate Cookies', 'Fudgy double chocolate cookies with cocoa and choc chips', 220.00, 'Cookies');

-- Create indexes for better query performance
CREATE INDEX idx_user_id ON orders(user_id);
CREATE INDEX idx_product_category ON products(category);
CREATE INDEX idx_custom_order_user ON custom_orders(user_id);
