import os
from fastapi import FastAPI, Request,HTTPException,Depends,status
from fastapi.middleware.cors import  CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

SECRET_TOKEN = os.getenv("SECRET_TOKEN")

if not SECRET_TOKEN:
    raise RuntimeError(
        "SECRET_TOKEN is not configured"
    )

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
    session_cookie="session",
    max_age=14 * 24 * 60 * 60,
    same_site="lax",
    https_only=True,
)


@app.get("/")
def root():
    return {"message": "http 200 ok"}


@app.get("/api/sx")
def sx_team():
    return {"message": "Love you"}


class LoginRequest(BaseModel):
    username: str
    password: str

def get_current_user(request: Request):
    user = request.session.get("user")

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    return user

@app.post("/login")
async def login(data: LoginRequest , request: Request):
    if not data.username or not data.password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Username and password are required"
        )

    request.session["user"] = {
        "username": data.username,
        "full_name": data.username,
    }

    return {
        "message": "Logged in successfully",
        "user": request.session["user"]
    }



@app.delete("/logout")
async def logout(request: Request):
    request.session.clear()
    return {"message": "Successfully logged out"}



@app.get("/me")
async def me(user: dict = Depends(get_current_user)):
    return user

@app.post("/protected")
async def protected_route(user: dict = Depends(get_current_user)):
    return {
        "message": f"Hello {user['full_name']}! This is a protected route.",
        "user": user
    }

