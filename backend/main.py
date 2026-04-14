from fastapi import FastAPI
from backend.routes.upload import router as upload_router

# create app instance [backend application]
app = FastAPI(title="Real Estate AI")

# register upload route [activate /upload endpoint]
app.include_router(upload_router)

#simple health check
@app.get("/")
def root():
    return {"message": "API is running"}