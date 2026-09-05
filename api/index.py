import httpx
from fastapi import FastAPI, HTTPException
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

# 2. Модели / Схемы Pydantic
class CryptoResponse(BaseModel):
    symbol: str
    price: str

# 3. Вспомогательные функции (Бизнес-логика)
async def fetch_binance_price(symbol: str) -> dict:
    url = "https://api.binance.com/api/v3/ticker/price"
    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(url, params={"symbol": symbol})
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(
                status_code=e.response.status_code,
                detail=f"Binance Error: {e.response.text}"
            )
        except httpx.RequestError as e:
            raise HTTPException(
                status_code=502,
                detail=f"Connection error: {str(e)}"
            )

# 4. Роуты / Маршруты
@app.get("/")
def home():
    return {"message": "200 ok"}

@app.get("/crypto/{symbol}", response_model=CryptoResponse)
async def get_crypto(symbol: str):
    data = await fetch_binance_price(symbol.upper())
    return data