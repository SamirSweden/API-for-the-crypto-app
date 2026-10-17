
from fastapi import FastAPI, HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from pydantic import Field, BaseModel


app = FastAPI()

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


    






