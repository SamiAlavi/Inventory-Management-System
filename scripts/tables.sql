CREATE TABLE IF NOT EXISTS Inventory (
    product_id INTEGER PRIMARY KEY,
    product_name TEXT,
    stock_level INTEGER,
    price REAL
);

CREATE TABLE IF NOT EXISTS Sales (
    sale_id INTEGER PRIMARY KEY,
    product_id INTEGER,
    sale_date DATE,
    quantity_sold INTEGER,
    FOREIGN KEY(product_id) REFERENCES Inventory(product_id)
);
