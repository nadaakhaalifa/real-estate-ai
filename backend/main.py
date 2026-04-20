from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from backend.routes.upload import router as upload_router
from backend.routes.search import router as search_router
from backend.routes.summary import router as summary_router
from backend.routes import health
from fastapi.middleware.cors import CORSMiddleware



# create app instance [backend application]
app = FastAPI(title="Real Estate AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routes
app.include_router(upload_router)
app.include_router(search_router)
app.include_router(summary_router)
app.include_router(health.router)


# fix Swagger UI rendering for multiple file uploads
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

            # Swagger UI behaves better with format=binary here
            items.pop("contentMediaType", None)
            items["type"] = "string"
            items["format"] = "binary"

    # 1) try fixing inline schema on /upload
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

    # if schema is inline
    fix_files_schema(schema_obj)

    # 2) if schema uses $ref, resolve it and patch the component schema
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


# simple health check
@app.get("/")
def root():
    return {"message": "API is running"}