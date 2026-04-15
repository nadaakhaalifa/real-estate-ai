from fastapi import FastAPI
from backend.routes.upload import router as upload_router
from backend.routes.search import router as search_router

# create app instance [backend application]
app = FastAPI(title="Real Estate AI")

# register upload route [activate /upload endpoint]
app.include_router(upload_router)

# register search endpoint with natural query parsing and filtering capabilities
app.include_router(search_router)

#simple health check
@app.get("/")
def root():
    return {"message": "API is running"}