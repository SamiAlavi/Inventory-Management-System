import uvicorn
from fastapi import FastAPI, HTTPException
import requests
from pydantic import BaseModel
from dotenv import load_dotenv
import os
import socket

load_dotenv()

app = FastAPI()

class Product(BaseModel):
    product_name: str
    stock_level: int
    price: float

@app.get("/fetch_products")
async def fetch_products():
    api_url = os.getenv('API_URL', 'https://fakestoreapi.com')
    products_url = f'{api_url}/products'
    response = requests.get(products_url)
    if response.status_code == 200:
        products: list[Product] = response.json()
        for product in products:
            print(product)
        return {"message": "Products fetched and added to inventory successfully."}
    else:
        raise HTTPException(status_code=400, detail="Failed to fetch products from API")

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