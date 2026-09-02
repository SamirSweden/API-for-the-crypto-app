from fastapi import FastAPI


app = FastAPI()


@app.get("/users")
def get_users():
    return  {"user": "Ryan"}

@app.get("/status")
def get_users():
    return  {"status": "http 200 ok"}