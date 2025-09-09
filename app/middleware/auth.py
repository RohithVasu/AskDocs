from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
from app.utils.auth import decode_token
from app.model_handlers.user_handler import UserHandler
from app.core.db import get_global_db_session

PUBLIC_PATHS = {"/login", "/register", "/refresh", "/me", "/docs", "/openapi.json"}

def auth_middleware(app):
    @app.middleware("http")
    async def check_auth(request: Request, call_next):
        if request.url.path in PUBLIC_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return JSONResponse({"detail": "Not authenticated"}, status_code=status.HTTP_401_UNAUTHORIZED)

        token = auth_header.split(" ")[1]
        try:
            payload = decode_token(token)
            if not payload or "sub" not in payload:
                raise HTTPException(status_code=401)

            email = payload["sub"]
            db = next(get_global_db_session())
            user = UserHandler(db).get_by_email(email)
            if not user:
                raise HTTPException(status_code=401)

            request.state.user = user  # save user to request state

        except Exception:
            return JSONResponse({"detail": "Invalid or expired token"}, status_code=status.HTTP_401_UNAUTHORIZED)

        return await call_next(request)
