from fastapi import FastAPI


app = FastAPI()


@app.get("/users")
def get_users():
    return  {"users": "Ryan, st"}

@app.get("/status")
def get_users():
    return  {"status": "http 201 ok"}