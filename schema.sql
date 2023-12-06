-- Customer Table
CREATE TABLE customer (
    customer_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    phone VARCHAR(15),
    address VARCHAR(255)
);

-- Product Table
CREATE TABLE product (
    product_id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    price DECIMAL(10, 2) NOT NULL
);

-- Purchase Table
CREATE TABLE purchase (
    purchase_id SERIAL PRIMARY KEY,
    customer_id INT REFERENCES Customer(customer_id),
    purchase_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    status VARCHAR(20) DEFAULT 'Received'
);

-- PurchaseItem Table to represent the relationship between Purchase and Product
CREATE TABLE purchase_product (
    item_id SERIAL PRIMARY KEY,
    purchase_id INT REFERENCES Purchase(purchase_id),
    product_id INT REFERENCES Product(product_id),
    quantity INT NOT NULL,
    subtotal DECIMAL(10, 2) NOT NULL
);