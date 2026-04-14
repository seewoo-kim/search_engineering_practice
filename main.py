from fastapi import FastAPI

app = FastAPI()

@app.get("/greeting")
def read_root():
    return {"message" : "Hello world"}