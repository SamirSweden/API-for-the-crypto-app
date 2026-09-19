import random
import uuid
import requests
import httpx
from fastapi import  status
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field,EmailStr
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv

load_dotenv()
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
        raise HTTPException(status_code=401,detail="Pin code does not match, try again")

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
            detail=f"coingecko API request failed: {e.response.text}",
        )

    except httpx.RequestError as e:
        raise HTTPException(
            status_code=500,
            detail=f"coingecko API request failed: {str(e)}",
        )


import os
import time

RESEND_API_KEY = os.getenv("RESEND_API_KEY")
FROM_EMAIL = "onboarding@resend.dev"
CODE_TTL_SECONDS = 300
SESSION_TTL_SECONDS = 60 * 60 * 24 * 30


codes: dict[str, dict] = {}
sessions: dict[str, dict] = {}

class RequestCodeBody(BaseModel):
    email: EmailStr

class VerifyCodeBody(BaseModel):
    email: str
    code: str



def send_code(email: str, code: str):
    resp = requests.post(
        "https://api.resend.com/emails",
        headers={"Authorization": f"Bearer {RESEND_API_KEY}"},
        json={
            "from": FROM_EMAIL,
            "to": [email],
            "subject": f"your code: {code}",
            "html": f"<p>Kraken.su</p><br>your code {code}</br>"
        },
        timeout=10,
    )

    if resp.status_code >= 400:
        print(resp.status_code , resp.text)
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY,detail=f"we couldn't send you code, try again later")


@app.post("/auth/request-code")
def request_code(body: RequestCodeBody):
    code = f"{random.randint(0,9999):04d}"
    codes[body.email] = {
        "code": code,
        "expires": time.time() + CODE_TTL_SECONDS,
        "attempts": 0
    }

    send_code(body.email, code)
    return {"message": "code sent successfully"}

@app.post("/auth/verify-code")
def verify_code(body: VerifyCodeBody):
    record = codes.get(body.email)

    if not record:
        raise HTTPException(status_code=400, detail="request for code")

    if time.time() > record["expires"]:
        del codes[body.email]
        raise HTTPException(status_code=400, detail="email expired")

    record["attempts"] += 1
    if record["attempts"] > 5:
        del codes[body.email]
        raise HTTPException(status_code=429, detail="too many attempts")

    if record["code"] != body.code:
        raise HTTPException(status_code=400, detail="wrong code")
    del codes[body.email]

    token = str(uuid.uuid4())
    sessions[token] = {"email": body.email, "expires": time.time() + SESSION_TTL_SECONDS}

    return {"token": token}
@app.get("/auth/me")
def me(token: str):
    session = sessions.get(token)
    if not session or time.time() > session["expires"]:
        raise HTTPException(status_code=401, detail="unauthorized")
    return {"email": session["email"]}




