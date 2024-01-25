-- Reset: sqlite3 database.db ".read store_schema.sql"

PRAGMA foreign_keys=on;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    username        VARCHAR(50) NOT NULL UNIQUE,
    password        VARCHAR(50) NOT NULL,
    fname           VARCHAR(50) NOT NULL,
    lname           VARCHAR(50) NOT NULL
);

DROP TABLE IF EXISTS orders;
CREATE TABLE orders (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    user_id         INT NOT NULL,
    date_placed     DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY     (user_id) REFERENCES users(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS categories;
CREATE TABLE categories (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(50) NOT NULL UNIQUE
);

DROP TABLE IF EXISTS products;
CREATE TABLE products (
    id              INTEGER NOT NULL PRIMARY KEY AUTOINCREMENT,
    name            VARCHAR(50) NOT NULL UNIQUE,
    price           DECIMAL(10,2),
    stock           INT DEFAULT 0,
    image_url       VARCHAR(100),
    description     VARCHAR(300)
);

DROP TABLE IF EXISTS category_products;
CREATE TABLE category_products (
    category_id     INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    PRIMARY KEY     (category_id, product_id),
    FOREIGN KEY     (category_id) REFERENCES categories(id) ON DELETE CASCADE,
    FOREIGN KEY     (product_id) REFERENCES products(id) ON DELETE CASCADE
);

DROP TABLE IF EXISTS order_products;
CREATE TABLE order_products (
    order_id        INTEGER NOT NULL,
    product_id      INTEGER NOT NULL,
    quantity        INTEGER NOT NULL,
    price_per       DECIMAL(10,2),
    PRIMARY KEY     (order_id, product_id),
    FOREIGN KEY     (order_id) REFERENCES orders(id) ON DELETE CASCADE,
    FOREIGN KEY     (product_id) REFERENCES products(id) ON DELETE SET NULL
);

-- users
INSERT INTO users (username, password, fname, lname) VALUES ('testuser', 'testpass', 'Test', 'User');

-- categories
INSERT INTO categories (name) VALUES ('Groceries');
INSERT INTO categories (name) VALUES ('Electronics');
INSERT INTO categories (name) VALUES ('Toys');

-- products
INSERT INTO products (name, price, stock, description) VALUES ('CanTenna', 9.95, 10, 'Two tin cans with antennas. Features better reception than a cell phone.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Customer Service Dream Phone', 29.95, 5, '/static/img/customer-service-dream-phone.jpg', 'By spinning the wheel on the telephone, you can speak to a real-life customer and hear their problem!');
INSERT INTO products (name, price, stock, description) VALUES ('USB Tire', 74.95, 100, 'Store files and important documents and even use it as an actual tire! 20-mile warranty.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Jalapeño Milk', 2.95, 1000, '/static/img/jalapeno-milk.jpg', 'The signature recipe formulated for people who like spicy foods plus milk.');
INSERT INTO products (name, price, stock, description) VALUES ('Yo-Yo Yo-Yo', 7.95, 1000, 'Listen, it''s two yo-yo''s put together. I don''t know what else to tell ya.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Waterproof Bread', 4.95, 99, '/static/img/waterproof-bread.jpg', 'This magical waterproof bread has a Canadian chemical making it waterproof. Currently awaiting FDA approval.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Toilet Soldiers', 4.95, 99, '/static/img/toilet-soldiers.jpg', 'A toilet with toy soldiers and a toy army base installed on it. Toilet not included.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Toxic O''s', 2.95, 99, '/static/img/toxic-os.jpg', 'World''s safest rat poison.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Forty-Seven Hour Energy Bar', 8.95, 99, '/static/img/energy-bar.jpg', 'Eat the whole bar to have energy for forty-seven hours. Want half the energy time? Eat half the bar.');
INSERT INTO products (name, price, stock, image_url, description) VALUES ('Double-Sided Spoon', 8.95, 3, '', '');
INSERT INTO products (name, price, stock, image_url) VALUES ('Rear-View Glasses', 19.95, 4, '/static/img/rear-view-glasses.jpg');

-- category_products
INSERT INTO category_products VALUES (1, 4);
INSERT INTO category_products VALUES (1, 6);
INSERT INTO category_products VALUES (1, 8);
INSERT INTO category_products VALUES (1, 9);
INSERT INTO category_products VALUES (2, 1);
INSERT INTO category_products VALUES (2, 2);
INSERT INTO category_products VALUES (2, 3);
INSERT INTO category_products VALUES (3, 1);
INSERT INTO category_products VALUES (3, 2);
INSERT INTO category_products VALUES (3, 5);
INSERT INTO category_products VALUES (3, 7);
INSERT INTO category_products VALUES (3, 10);
INSERT INTO category_products VALUES (3, 11);
