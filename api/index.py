from fastapi import FastAPI , HTTPException,status
from fastapi.middleware.cors import CORSMiddleware
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field


app = FastAPI()


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

origins = [
    "http://localhost:3000",
    "https://kraken-su.vercel.app"
]


#2GF5IL55BSHUAAQ4TQQN65QXLERIGNAW
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET",  "POST"],
    allow_headers=["*"],
)

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
    return {"message": "Hello World"}






