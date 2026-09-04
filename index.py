from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()



@app.get("/")
def root():
    return {"message": "Hello Ryan"}

@app.get("/api/sx")
def sx_handler():
    return {"messageFromRyan": "Ich leibe dich"}

@app.get("/api/love")
def love():
    return {"is_love": "luv u"}



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