from fastapi import FastAPI, Request,HTTPException,Depends,status
from fastapi.middleware.cors import  CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
from pydantic import BaseModel
import secrets



app = FastAPI()

SECRET_TOKEN = secrets.token_hex(32)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
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

fake_users_db = {
    "admin": {
        "username": "admin",
        "password": "secret",
        "full_name": "Admin User"
    }
}


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
async def login(data: LoginRequest,request: Request):
    user = fake_users_db.get(data.username)

    if not user or user["password"] != data.password:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    request.session["user"] = {
        "username":user["username"],
        "full_name": user["full_name"],
    }

    return {"message": "Logged in successfully","user": request.session["user"]}


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
        "message": f"Hello {user["full_name"]}! This is a protected route.",
        "user": user
    }





