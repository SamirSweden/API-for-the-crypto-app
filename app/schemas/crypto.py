from pydantic import BaseModel


class CryptoCurrencyModel(BaseModel):
    symbol: str
    price: str






