from fastapi import FastAPI

app = FastAPI(title="Real Estate AI")

@app.get("/")
def root():
    return {"message": "API is running"}