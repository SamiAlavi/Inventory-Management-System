import uvicorn
from fastapi import FastAPI, HTTPException
import requests
from dotenv import load_dotenv
import os
import sqlite3
import socket
from pydantic import BaseModel
from typing import List, Optional

load_dotenv()

db_name = os.getenv('DATABASE_NAME', 'default.db')
api_url = os.getenv('API_URL', 'https://fakestoreapi.com')

app = FastAPI()

class Product(BaseModel):
    product_name: str
    stock_level: int
    price: float
    description: Optional[str] = None
    category: Optional[str] = None
    image: Optional[str] = None

class ExternalProduct(BaseModel):
    id: int
    title: str
    price: float

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