from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from jose import JWTError

from app.routes import AppResponse
from app.core.db import get_global_db_session
from app.core.settings import settings
from app.utils.auth import (
    verify_password,
    get_password_hash,
    create_access_token,
    decode_token,
    create_refresh_token,
    decode_refresh_token
)
from app.model_handlers.user_handler import UserHandler, UserCreate, UserResponse


auth_router = APIRouter(prefix="/auth", tags=["auth"])

# OAuth2PasswordBearer will tell FastAPI where to get the token
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="auth/token",
    scheme_name="JWT",
)

# ---------------------------
# Dependency to get current user
# ---------------------------
async def get_current_user(
    token: Annotated[str, Depends(oauth2_scheme)],
    db: Session = Depends(get_global_db_session)
) -> UserResponse:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        if payload is None:
            raise credentials_exception
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception

    user_handler = UserHandler(db)
    user = user_handler.get_by_email(email)
    if user is None:
        raise credentials_exception

    return user

# ---------------------------
# Register
# ---------------------------
@auth_router.post("/register", response_model=AppResponse, status_code=201)
async def register(user: UserCreate, db: Session = Depends(get_global_db_session)):
    user_handler = UserHandler(db)
    existing_user = user_handler.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    hashed_password = get_password_hash(user.password)

    new_user = user_handler.create(
        UserCreate(
            email=user.email,
            password=hashed_password,
            firstname=user.firstname,
            lastname=user.lastname
        )
    )

    return AppResponse(
        status="success",
        message="User registered successfully",
        data={
            "email": new_user.email,
            "firstname": new_user.firstname,
            "lastname": new_user.lastname
        }
    )

# ---------------------------
# Login (returns access + refresh token)
# ---------------------------
@auth_router.post("/login", response_model=AppResponse)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_global_db_session)
):
    user_handler = UserHandler(db)
    user = user_handler.get_by_email(form_data.username, with_password=True)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    refresh_token_expires = timedelta(days=7)

    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"sub": user.email}, expires_delta=refresh_token_expires
    )

    return AppResponse(
        status="success",
        message="User logged in successfully",
        data={
            "access_token": access_token,
            "refresh_token": refresh_token,
            "token_type": "bearer"
        }
    )

# ---------------------------
# Token (for Swagger API)
# ---------------------------

@auth_router.post("/token")
async def login_swagger(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_global_db_session)
):
    user_handler = UserHandler(db)
    user = user_handler.get_by_email(form_data.username, with_password=True)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=401,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

# ---------------------------
# Refresh Access Token
# ---------------------------
@auth_router.post("/refresh", response_model=AppResponse)
async def refresh_access_token(
    refresh_token: str,
    db: Session = Depends(get_global_db_session)
):
    payload = decode_refresh_token(refresh_token)
    if payload is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    email = payload.get("sub")
    if email is None:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_handler = UserHandler(db)
    user = user_handler.get_by_email(email)
    if user is None:
        raise HTTPException(status_code=401, detail="User not found")

    access_token_expires = timedelta(minutes=settings.auth.access_token_expire_minutes)
    new_access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )

    return AppResponse(
        status="success",
        message="Token refreshed successfully",
        data={
            "access_token": new_access_token,
            "token_type": "bearer"
        }
    )

# ---------------------------
# Get Current User (/me)
# ---------------------------
@auth_router.get("/me", response_model=AppResponse)
async def read_users_me(
    current_user: Annotated[UserResponse, Depends(get_current_user)]
):
    return AppResponse(
        status="success",
        message="User fetched successfully",
        data=current_user
    )

# ---------------------------
# Logout
# ---------------------------
@auth_router.post("/logout")
async def logout():
    # In a real application:
    # 1. Store refresh token in DB
    # 2. Mark as invalid on logout
    return AppResponse(
        status="success",
        message="Successfully logged out",
        data={}
    )
