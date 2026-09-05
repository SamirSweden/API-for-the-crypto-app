from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from app.routers.crypto import router as crypto_router
app = FastAPI()


origin = [
    "https://kraken-umber.vercel.app",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origin,
    allow_credentials=True,
    allow_methods=["GET, POST"],
    allow_headers=["*"],
)

app.include_router(crypto_router)

@app.get("/")
def root():
    return {"message": "Hello Ryan"}

@app.get("/api/sx")
def sx_handler():
    return {"messageFromRyan": "Ich leibe dich"}

@app.get("/api/love")
def love():
    return {"is_love": "Te adoro mas Haylin"}



@app.exception_handler(404)
def not_found(request, exc):
    return JSONResponse(
        status_code=404,
        content={
            "error": "404 not found",
            "message" : "The requested endpoint does not exist",
            "path":request.url.path
        }
    )