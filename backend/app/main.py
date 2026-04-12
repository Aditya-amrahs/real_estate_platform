from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from backend.app.api.auth import router as auth_router
from backend.app.api.properties import router as property_router
from backend.app.api.favorites import router as favorite_router
from backend.app.api.booking import router as booking_router
from backend.app.api import favorites, booking, dashboard, recommendations

app = FastAPI()

app.include_router(auth_router)
app.include_router(property_router)
app.include_router(favorite_router)
app.include_router(booking_router)
app.include_router(dashboard.router)
app.include_router(recommendations.router)

@app.get("/")
def root():
    return {"message": "API running"}


# ✅ CUSTOM OPENAPI FOR AUTHORIZE BUTTON
def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema

    openapi_schema = get_openapi(
        title="Real Estate API",
        version="1.0",
        description="JWT Auth API",
        routes=app.routes,
    )

    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }

    # Apply globally (optional but common)
    for path in openapi_schema["paths"].values():
        for method in path.values():
            method["security"] = [{"BearerAuth": []}]

    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi