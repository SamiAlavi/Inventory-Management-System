import uvicorn
from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
import os
import sqlite3
import socket
from pydantic import BaseModel
from typing import List, Optional
import random
from datetime import datetime, timedelta
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score
import joblib

load_dotenv()

db_name = os.getenv('DATABASE_NAME', 'default.db')
api_url = os.getenv('API_URL', 'https://fakestoreapi.com')
sales_prediction_model_path = "sales_prediction_model.pkl"

app = FastAPI()

class Product(BaseModel):
    product_name: str
    stock_level: int
    price: float

    def __getitem__(self, item):
        return getattr(self, item)

class ExternalProduct(BaseModel):
    id: int
    title: str
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None

    def __getitem__(self, item):
        return getattr(self, item)

def connect_db():
    conn = sqlite3.connect(db_name)
    return conn
    
@app.get("/fetch_products")
async def fetch_products():
    products_url = f'{api_url}/products'
    response = requests.get(products_url)
    if response.status_code == 200:
        conn = connect_db()
        cursor = conn.cursor()
        products: List[ExternalProduct] = response.json()
        for product in products:
            stock_level = 100
            cursor.execute('''
                INSERT OR IGNORE INTO Inventory (product_id, product_name, stock_level, price) 
                VALUES (?, ?, ?, ?)''',
                (product['id'], product['title'], stock_level, product['price'])
            )
        conn.commit()
        conn.close()
        return {"message": "Products fetched and added to inventory successfully."}
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch products from API")

@app.get("/products", response_model=List[ExternalProduct])
async def get_products():
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute("SELECT product_id, product_name, stock_level, price FROM Inventory")
    products = cursor.fetchall()
    conn.close()

    product_list = [
        {"id": product[0], "title": product[1], "stock_level": product[2], "price": product[3]}
        for product in products
    ]
    
    return product_list

@app.post("/product")
async def add_product(product: Product):
    conn = connect_db()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO Inventory (product_name, stock_level, price)
        VALUES (?, ?, ?)''',
        (product.product_name, product.stock_level, product.price)
    )
    conn.commit()
    conn.close()
    return {"message": "Product added successfully."}

@app.post("/generate_sales")
async def generate_sales(num_sales: int = 100):
    conn = connect_db()
    cursor = conn.cursor()
    
    for _ in range(num_sales):
        product_id = random.randint(1, 20)
        quantity_sold = random.randint(1, 5)
        sale_date = datetime.now() - timedelta(days=random.randint(1, 30))
        
        cursor.execute('''
            INSERT INTO Sales (product_id, sale_date, quantity_sold)
            VALUES (?, ?, ?)''',
            (product_id, sale_date, quantity_sold)
        )
    conn.commit()
    conn.close()
    return {"message": f"{num_sales} sales transactions generated."}

@app.get("/train_model")
async def train_model():
    conn = connect_db()
    sales_data = pd.read_sql_query("SELECT * FROM Sales", conn)
    
    sales_data['sale_date'] = pd.to_datetime(sales_data['sale_date'])
    sales_data['day'] = sales_data['sale_date'].dt.day
    sales_data['month'] = sales_data['sale_date'].dt.month

    X = sales_data[['product_id', 'day', 'month']]
    y = sales_data['quantity_sold']

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    model = LinearRegression()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)
    mse = mean_squared_error(y_test, y_pred)
    r2 = r2_score(y_test, y_pred)

    joblib.dump(model, sales_prediction_model_path)

    return {
        "message": "Model trained and saved.",
        "mean_squared_error": mse,
        "r2_score": r2
    }

@app.get("/predict_sales")
async def predict_sales(product_id: int):
    try:
        model = joblib.load(sales_prediction_model_path)
    except:
        raise HTTPException(status_code=500, detail="Model not found. Please train the model first.")
    
    day = datetime.now().day
    month = datetime.now().month

    input_data = pd.DataFrame({
        'product_id': [product_id],
        'day': [day],
        'month': [month]
    })

    predicted_sales = model.predict(input_data)

    return {"predicted_sales": predicted_sales[0]}

@app.get("/")
async def home():
    return {"message": "Welcome to the Inventory Management System"}

def print_ip_addresses(port: int):
    hostname = socket.gethostname()
    ip_addresses = socket.gethostbyname_ex(hostname)[2]
    print("Server running on:")
    for ip in ip_addresses:
        print(f" - {ip}:{port}")

if __name__ == "__main__":
    port = 8000
    print_ip_addresses(port)
    uvicorn.run("app:app", host="0.0.0.0", port=port, reload=True)