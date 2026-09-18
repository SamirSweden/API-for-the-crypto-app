import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from fastapi.middleware.cors import CORSMiddleware



app = FastAPI()

origins = [
    "http://localhost:3000",
    "https://kraken-su.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


fake_db = {}
alerts = {}



class PinRequest(BaseModel):
    user_id: str
    pin: str = Field(..., min_length=4, max_length=4, description="Pin 4 digits")


class AlertCreate():
    symbol: str
    target_price: float
    condition: str


@app.get("/")
async def root():
    return {
        "message": "Welcome to Kraken-Su API",
    }

@app.post("/api/set-pin")
async def set_pin(data: PinRequest):
    if not data.pin.isdigit():
        raise HTTPException(
            status_code=401,
            detail="Pin must be an integer",
        )
    fake_db[data.user_id] = data.pin
    return {
        "status": "success",
        "message": "Pin set successfully",
    }


@app.post("/api/verify-pin")
async def verify_pin(data: PinRequest):
    stored_pin = fake_db.get(data.user_id)

    if not stored_pin or stored_pin == "":
        raise HTTPException(
            status_code=404,
            detail="pin-code not found or user_id is invalid",
        )

    if stored_pin != data.pin:
        raise HTTPException(
            status_code=401,
            detail="Pin code does not match, try again",
        )

    return {
        "status": "success",
        "message": "Access granted",
    }



@app.post("/api/crypto")
async def get_crypto():
    url = "https://api.coingecko.com/api/v3/simple/price"

    params = {
        "ids": ",".join([
            "bitcoin",
            "ethereum",
            "tether",
            "binancecoin",
            "solana",
            "usd-coin",
            "xrp",
            "dogecoin",
            "cardano",
            "avalanche-2",
            "tron",
            "chainlink",
            "polkadot",
            "polygon",
            "litecoin",
            "shiba-inu",
            "uniswap",
            "stellar",
            "near",
            "internet-computer",
        ]),
        "vs_currencies": "usd",
    }

    try: 
        async with httpx.AsyncClient(timeout=10.0) as client:
            resp = await client.get(url, params=params)
        resp.raise_for_status()

        return resp.json()

    except httpx.HTTPStatusError as e:
        raise HTTPException(
            status_code=500,
            detail=f"coingecko API request failed: {str(e)}",
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"coingecko API request failed: {str(e)}",
        )

    