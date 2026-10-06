import uuid

import httpx
from fastapi import FastAPI , HTTPException,status, UploadFile,File
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

app = FastAPI()


users: dict[str, dict[str, str]] = {}

class AuthRequest(BaseModel):
    email: EmailStr
    password: str = Field(
        min_length=8,
        max_length=128,
    )


class UserResponse(BaseModel):
    email: EmailStr


@app.post(
    "/auth/register",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
)
def register(data: AuthRequest):
    email = str(data.email).lower().strip()


    if email in users:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Email already registered",
        )

    users[email] = {
        "password": pwd_context.hash(data.password),
    }

    return {
        "email": email
    }


@app.post("/auth/login", response_model=UserResponse)
def login(data: AuthRequest):

    email = str(data.email).lower().strip()
    user = users.get(email)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    password_valid = pwd_context.verify(
        data.password,
        user["password"]
    )


    if not password_valid:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
        )

    return {
        "email": email
    }


@app.get("/")
async def root():
    return {"message": "http 200 ok"}


@app.get("/api/haylin")
def haylin():
    return {
        "status": "Princess",
        "isSweet":True,
        "isCute":True,
        "isRyanLoves":True,
        "bites": 100,
        "message": "Самой красивой принцессе❤️",
    }






@app.get("/prices")
async def get_all_prices():
    url = f"https://api.coingecko.com/api/v3/coins/markets"

    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": 250,
        "page": 1,
        "sparkline": "false"
    }

    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        response.raise_for_status()
        return response.json()





import os
from dotenv import load_dotenv
from supabase import Client, create_client

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

supabase = Client = create_client(
    SUPABASE_URL,
    SUPABASE_KEY
)

@app.post("/api/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="only images allowed")

    content = await file.read()

    filename = f"{uuid.uuid4()}-{file.filename}"

    result = supabase.storage \
        .from_("couple-photos") \
        .upload(
        filename,
        content,
        {
            "content-type": file.content_type
        }
    )


    return {
        "message" : "Photo uploaded",
        "filename": filename,
    }


