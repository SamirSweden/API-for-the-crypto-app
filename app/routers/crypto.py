from fastapi import APIRouter
from app.schemas.crypto import CryptoCurrencyModel
from app.services.crypto_service import get_crypto_price


router = APIRouter(
    prefix="/crypto",
    tags=["Crypto"],
)



@router.get(
    "/{symbol}",
    response_model=CryptoCurrencyModel
)
async def crypto_price(symbol: str):

    data = await get_crypto_price(symbol.upper())

    return {
        "symbol": data["symbol"],
        "price": data["price"]
    }

