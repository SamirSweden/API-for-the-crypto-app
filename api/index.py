from http import client
from urllib import request

import httpx
from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

app = FastAPI()

# 1. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kraken-umber.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class RegisterUser(BaseModel):
    username: str

# 2. Роуты
@app.get("/")
def home():
    return {"message": "200 ok"}



@app.get("/api/sx")
def home():
    return {"messageFromRyan": "I love you"}

@app.get("/crypto/{coin_id}")
async def get_price(coin_id: str):
    url = "https://api.coingecko.com/api/v3/simple/price"

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(
                url,
                params={
                    "ids": coin_id.lower(),
                    "vs_currencies": "usd"
                }
            )
            response.raise_for_status()
            data = response.json()

            if not data or coin_id.lower() not in data:
                raise HTTPException(status_code=404, detail=f"Coin '{coin_id}' not found")

            return data
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=e.response.text
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Connection error to CoinGecko: {str(e)}"
            )



@app.get("/api/ip")
async def get_user_ip(request: Request):
    return {
        "ip": request.client.host,
    }




@app.post("/api/register")
async def register_user(data: RegisterUser, request: Request):
    username = data.username
    ip = request.client.host

    return {
        "userName": username,
        "ip": ip
    }
