
from fastapi import FastAPI


app = FastAPI()



@app.get("/")
def root():
    return {"message": "Hello Ryan"}



@app.get("/api/love")
def love():
    return {"is_love": "luv u"}
