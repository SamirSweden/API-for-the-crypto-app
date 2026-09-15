import os
from dotenv import load_dotenv
from fastapi import FastAPI,HTTPException, status
from passlib.context import CryptContext
from pydantic import BaseModel, Field
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from typing import Dict


load_dotenv()

app = FastAPI()


SECRET_TOKEN = os.getenv("SECRET_TOKEN")

if not SECRET_TOKEN:
    raise RuntimeError("SECRET_TOKEN not set")



origins = [
    "http://localhost:3000",
    "https://kraken-su.vercel.app"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST","DELETE"],
    allow_headers=["*"],
)

app.add_middleware(
    SessionMiddleware,
    secret_key=SECRET_TOKEN,
    max_age=60 * 60 * 24 * 14,
    same_site="lax",
    https_only=True,
)



pwd_context = CryptContext(
    schemes=["argon2"],
    deprecated="auto",
)

users: Dict[str, dict] = {}

class RegisterRequest(BaseModel):
    username: str = Field(
        min_length=3,
        max_length=30,
    )

    password: str = Field(
        min_length=6,
        max_length=128,
    )


@app.get("/api")
async def root():
    return {"message": "api is running"}

@app.get("/")
async def root():
    return {"message": "200 ok"}

@app.post("/api/register")
async def register(data: RegisterRequest):
    username = data.username.strip()

    if not username:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username already exists"
        )

    password_hash = pwd_context.hash(data.password)

    users[username] = {
        "username":username,
        "password_hash":password_hash
    }

    return {
        "message": "Registration successful",
        "username": username
    }








