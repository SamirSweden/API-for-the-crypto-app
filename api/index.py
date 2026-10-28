import secrets
import httpx
import hashlib
from fastapi import FastAPI, HTTPException,status,Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel


app = FastAPI(title="My English AI Dictionary")



origins = [
    "https://kraken-su.vercel.app",
    "http://localhost:3000"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_headers=["*"],
    allow_methods=["POST","GET"]
)


class LoginRequest(BaseModel):
    username: str = Field(min_length=3,max_length=100)
    password: str = Field(min_length=8,max_length=100)

users = set()

@app.get("/")
async def home():
    return {
        "message": "http 200 ok"
    }

@app.post("/api/login")
async def login_user(data: LoginRequest):
    username = data.username.strip()

    if len(username) < 3:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username must contain at least 3 characters"
        )

    if username.lower() in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="User already exists"
        )

    users.add(username.lower())


    return {
        "message" : "Login successful",
        "username": username
    }

words = [
    ["Hello / Hi", "Привет"],
    ["Good morning", "Доброе утро"],
    ["I'm up for that / Count me in / I'm down", "Я согласен, я за"],
    ["I don't feel like it", "Не хочу, нет желания"],
    ["I must be off / I have to go / I gotta go", "Мне пора идти"],
    ["I see red", "Я злюсь"],
    ["Take care", "Береги себя"],
    ["Keep in mind", "Имей в виду, запомни"],
    ["I have a favor to ask", "У меня к тебе просьба"],
    ["Time will tell", "Время покажет"],
]
    
class TranslateRequest(BaseModel):
    question: str = Field(min_length=1,max_length=500)


def normalize(text: str) -> str:
    return " ".join(text.casefold().strip().split())

@app.post("/api/translate")
async def translate(data: TranslateRequest):
    question = normalize(data.question)
    results=[]

    for english, russian in words:
        english_parts = [
            normalize(part)
            for part in english.split("/")
        ]

        russian_normalazed = normalize(russian)
        if (
            question in russian_normalazed
            or russian_normalazed in question
        ):
            results.append({
                "english":english,
                "russian": russian
            })
        elif any(
            question in part or part in question
            for part in english_parts
        ):
            results.append({
                "english": english,
                "russian": russian
            })

    return {
        "question":data.question,
        "found": bool(results),
        "results": results[:5],
        "message": (
            "Found in your dictionary"
            if results
            else "Phrase not found"
        )

    }



@app.get("/api/words")
async def get_words():
    return {
        "count": len(words),
        "words":[
            {"english":english ,"russian":russian}
            for english ,russian in words
        ]
    }




# class UserRegister(BaseModel):
#     username: str
#     password: str
#
# class UserResponse(BaseModel):
#     username: str
#     password: str
#
#
# @app.post("/register")
# async def register(data: UserResponse):
#     return {
#         "message":"user registered",
#         "username": data.username,
#     }



class UserRegister(BaseModel):
    username: str
    password: str


class UserResponse(BaseModel):
    username: str
    message: str


@app.post("/register", response_model=UserResponse)
async def register(data: UserRegister):
    return {
        "message": "user registered",
        "username": data.username,
    }


class CoinResponse(BaseModel):
    id: str 
    name: str
    symbol: str
    rank: int
    price_usd: float
    change_24h: float

@app.get("/prices", response_model=list[CoinResponse])
async def get_prices(
    limit: int = Query(default=20, ge=1,le=100)
):
    url = "https://api.coinpaprika.com/v1/tickers"

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            response = await client.get(
                url,
                params={"quotes":"USD"}
            )
            response.raise_for_status()
            data = response.json()

    except httpx.HTTPError as err:
        raise HTTPException(
            status_code=502,
            detail="could not make request"
        ) from err

    coins = []

    for coin in data[:limit]:
        usd = coin.get("quotes",{}).get("USD", {})
        price = usd.get("price")
        change = usd.get("percent_change_24h")

        if price is None:
            continue

        coins.append({
            "id": coin["id"],
            "name": coin["name"],
            "symbol": coin["symbol"],
            "rank": coin["rank"],
            "price_usd": price,
            "change_24h": change or 0.0,
        })

    return coins





