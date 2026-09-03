from fastapi import FastAPI


app = FastAPI()

@app.get("/")
def health_check():
    return {"status": "http 200 ok"}
@app.get("/users")
def get_users():
    return  {"users": "Ryan , A"}

