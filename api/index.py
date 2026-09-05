import httpx
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# 1. Настройка CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://kraken-umber.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# 2. Роуты
@app.get("/")
def home():
    return {"message": "200 ok"}

@app.get("/crypto/{coin_id}")
async def get_price(coin_id: str):
    # Принимает ID монеты: bitcoin, ethereum, solana и т.д.
    url = "https://api.coingecko.com/api/v3/simple/price"

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            response = await client.get(
                url,
                params={
                    "ids": coin_id.lower(),
                    "vs_currencies": "usd"  # Исправлено: указан имя параметра
                }
            )
            response.raise_for_status()
            data = response.json()

            # Если передан неверный coin_id, CoinGecko возвращает {}
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