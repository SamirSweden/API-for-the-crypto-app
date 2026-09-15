from fastapi import FastAPI, HTTPException
from pydantic import BaseModel,Field
from fastapi.middleware.cors import CORSMiddleware

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




class PinRequest(BaseModel):
    user_id: str
    pin: str = Field(..., min_length=4, max_length=4, description="Pin 4 digits")

@app.get("/")
async def root():
    return {
        "message": "Welcome to Kraken-Su API",
    }

@app.post("/set-pin")
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


@app.post("/verify-pin")
async def verify_pin(data: PinRequest):
    stored_pin = fake_db.get(data.user_id)

    if not stored_pin or stored_pin == "":
        raise HTTPException(
            status_code=404,
            detail="pin-code not found or user_id is invalid",
        )

    if stored_pin != data.pin:
        raise HTTPException(
            status_code=401,
            detail="Pin code does not match, try again",
        )

    return {
        "status": "success",
        "message": "Access granted",
    }


