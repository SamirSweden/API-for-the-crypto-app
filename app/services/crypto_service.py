import httpx


async def get_crypto_price(symbol: str):
    url = "https://api.binance.com/api/v3/ticker/price"

    async with httpx.AsyncClient() as client:
        response = await client.get(
            url,
            params={"symbol": symbol}
        )

        response.raise_for_status()
        return response.json()

