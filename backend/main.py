import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from backend.database import Base, engine
from backend.models import Upload, Unit
from backend.routes.upload import router as upload_router
from backend.routes.search import router as search_router
from backend.routes.summary import router as summary_router
from backend.routes import health


app = FastAPI(title="Real Estate AI")

Base.metadata.create_all(bind=engine)

frontend_url = os.getenv("FRONTEND_URL")

allowed_origins = [
    "http://localhost:5173",
    "http://localhost:5174",
    "http://127.0.0.1:5173",
    "http://127.0.0.1:5174",
]

if frontend_url:
    allowed_origins.append(frontend_url)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload_router)
app.include_router(search_router)
app.include_router(summary_router)
app.include_router(health.router)


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title=app.title,
        version="1.0.0",
        description=app.description,
        routes=app.routes,
    )

    def fix_files_schema(schema_dict):
        if not isinstance(schema_dict, dict):
            return

        properties = schema_dict.get("properties", {})
        files_prop = properties.get("files")

        if files_prop and files_prop.get("type") == "array":
            items = files_prop.get("items", {})
            items.pop("contentMediaType", None)
            items["type"] = "string"
            items["format"] = "binary"

    upload_post = (
        openapi_schema.get("paths", {})
        .get("/upload", {})
        .get("post", {})
    )

    multipart_content = (
        upload_post.get("requestBody", {})
        .get("content", {})
        .get("multipart/form-data", {})
    )

    schema_obj = multipart_content.get("schema", {})
    fix_files_schema(schema_obj)

    ref = schema_obj.get("$ref")
    if ref and ref.startswith("#/components/schemas/"):
        schema_name = ref.split("/")[-1]
        component_schema = (
            openapi_schema.get("components", {})
            .get("schemas", {})
            .get(schema_name)
        )
        fix_files_schema(component_schema)

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi


@app.get("/")
def root():
    return {"message": "API is running"}


@app.get("/healthh")
def health_check():
    return {"status": "ok"}