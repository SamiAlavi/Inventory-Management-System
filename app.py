import uvicorn
from fastapi import FastAPI
import socket

app = FastAPI()

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