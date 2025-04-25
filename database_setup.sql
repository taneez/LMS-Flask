CREATE DATABASE IF NOT EXISTS laundry_db_simple;
USE laundry_db_simple;

-- User Table
CREATE TABLE IF NOT EXISTS Users (
    user_id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(150) UNIQUE NOT NULL,
    password_hash VARCHAR(128) NOT NULL,
    first_name VARCHAR(250) NOT NULL,
    last_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20) NOT NULL,
    address VARCHAR(255) NOT NULL,
    role ENUM('customer', 'staff', 'admin') NOT NULL DEFAULT 'customer',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
    -- Removed account_balance for simplicity
);

-- Laundry Item Table (Defines services/items offered)
CREATE TABLE IF NOT EXISTS LaundryItems (
    laundry_item_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL UNIQUE, -- Make name unique
    description TEXT,
    base_price DECIMAL(10, 2) NOT NULL CHECK (base_price >= 0),
    category VARCHAR(50)
);

-- Orders Table
CREATE TABLE IF NOT EXISTS Orders (
    order_id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    due_date TIMESTAMP NULL,
    total_amount DECIMAL(10, 2) DEFAULT 0.00, -- Calculate based on items
    order_status ENUM('Pending', 'Received', 'Processing', 'Ready', 'Completed', 'Cancelled') NOT NULL DEFAULT 'Pending',
    special_instructions TEXT,
    FOREIGN KEY (user_id) REFERENCES Users(user_id) ON DELETE CASCADE
);

-- Order Items Table
CREATE TABLE IF NOT EXISTS OrderItems (
    order_item_id INT AUTO_INCREMENT PRIMARY KEY,
    order_id INT NOT NULL,
    laundry_item_id INT NOT NULL,
    quantity INT NOT NULL CHECK (quantity >= 1),
    price_per_unit DECIMAL(10, 2) NOT NULL, -- Price at time of order
    total_price DECIMAL(10, 2) NOT NULL,   -- quantity * price_per_unit
    FOREIGN KEY (order_id) REFERENCES Orders(order_id) ON DELETE CASCADE,
    FOREIGN KEY (laundry_item_id) REFERENCES LaundryItems(laundry_item_id) ON DELETE RESTRICT
);

-- Seed data (optional)
INSERT INTO Users (username, password_hash, first_name, last_name, email, phone, address, role)
VALUES ('admin', 'admin', 'Admin', 'Istrator', 'admin@laundry.com', '1234567890', '1 Admin Way', 'admin')
ON DUPLICATE KEY UPDATE username=username; -- Avoid error if run twice

INSERT INTO LaundryItems (name, description, base_price, category) VALUES
('Shirt Wash & Fold', 'Standard wash and fold', 2.00, 'Wash & Fold'),
('Trousers Wash & Fold', 'Standard wash and fold', 3.00, 'Wash & Fold'),
('Shirt Dry Clean', 'Dry cleaning service', 4.50, 'Dry Cleaning'),
('Suit Dry Clean', 'Two-piece suit dry cleaning', 15.00, 'Dry Cleaning'),
('Ironing per Item', 'Pressing only', 1.00, 'Pressing')
ON DUPLICATE KEY UPDATE name=name;