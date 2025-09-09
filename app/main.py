from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from app.routes.auth import auth_router
# from app.routes.chat import chat_router
from app.routes.documents import document_router
from app.routes.folders import folder_router
from app.routes.users import user_router

# Initialize FastAPI app
app = FastAPI(
    root_path="/api/v1",
    title="AskDocs API",
    description="Visit http://0.0.0.0:8000/docs for API documentation",
    version="0.0.1"
)

PUBLIC_PATHS = {
    "/docs",
    "/redoc",
    "/openapi.json",
    "/api/v1/docs",
    "/api/v1/redoc",
    "/api/v1/openapi.json",
    "/auth/login",
}

# Add auth middleware (protects everything except PUBLIC_PATHS)
def auth_middleware(app):
    class AuthMiddleware(BaseHTTPMiddleware):
        async def dispatch(self, request: Request, call_next):
            # ✅ allowlist: skip auth for public paths
            if request.url.path in PUBLIC_PATHS:
                return await call_next(request)

            # 🔒 here do your JWT / session check
            token = request.headers.get("Authorization")
            if not token:
                return JSONResponse(
                    status_code=401,
                    content={"detail": "Unauthorized"},
                )

            # (your token validation logic goes here)

            return await call_next(request)

    app.add_middleware(AuthMiddleware)

# Register routers
app.include_router(auth_router)
app.include_router(document_router)
app.include_router(folder_router)
# app.include_router(chat_router)
app.include_router(user_router)
