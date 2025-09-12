from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.routes.auth import auth_router
# from app.routes.chat import chat_router
from app.routes.documents import document_router
from app.routes.folders import folder_router
from app.routes.users import user_router
from app.routes.auth import get_current_user


# Initialize FastAPI app
app = FastAPI(
    root_path="/api/v1",
    title="AskDocs API",
    description="Visit http://0.0.0.0:8000/docs for API documentation",
    version="0.0.1"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:8000", "http://127.0.0.1:8000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# PUBLIC_PATHS = {
#     "/docs",
#     "/redoc",
#     "/openapi.json",
#     "/api/v1/docs",
#     "/api/v1/redoc",
#     "/api/v1/openapi.json",
#     "/auth/login",
#     "/auth/register",
#     "/auth/refresh",
#     "/auth/me",
# }

# # Add auth middleware (protects everything except PUBLIC_PATHS)
# def auth_middleware(app):
#     class AuthMiddleware(BaseHTTPMiddleware):
#         async def dispatch(self, request: Request, call_next):
#             # ✅ allowlist: skip auth for public paths
#             if request.url.path in PUBLIC_PATHS:
#                 return await call_next(request)

#             # 🔒 here do your JWT / session check
#             token = request.headers.get("Authorization")
#             if not token:
#                 return JSONResponse(
#                     status_code=401,
#                     content={"detail": "Unauthorized"},
#                 )

#             # (your token validation logic goes here)

#             return await call_next(request)

#     app.add_middleware(AuthMiddleware)

# Register routers
app.include_router(auth_router)
app.include_router(document_router, dependencies=[Depends(get_current_user)])
app.include_router(folder_router, dependencies=[Depends(get_current_user)])
# app.include_router(chat_router)
app.include_router(user_router, dependencies=[Depends(get_current_user)])
