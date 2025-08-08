from datetime import timedelta
from typing import Annotated
from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from app.core.db import get_global_db_session
from app.utils.auth import verify_password, get_password_hash, create_access_token, decode_token
from app.model_handlers.user_handler import UserHandler
from pydantic import BaseModel

router = APIRouter()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

class User(BaseModel):
    id: str
    email: str
    name: str
    created_at: str
    last_active_at: str

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: str | None = None

class RegisterUser(BaseModel):
    email: str
    password: str
    name: str

async def get_current_user(token: Annotated[str, Depends(oauth2_scheme)], db: Session = Depends(get_global_db_session)):
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
        token_data = TokenData(email=email)
    except JWTError:
        raise credentials_exception
    
    user_handler = UserHandler(db)
    user = user_handler.get_by_email(token_data.email)
    if user is None:
        raise credentials_exception
    return user

@router.post("/register", response_model=User, status_code=201)
async def register(user: RegisterUser, db: Session = Depends(get_global_db_session)):
    user_handler = UserHandler(db)
    existing_user = user_handler.get_by_email(user.email)
    if existing_user:
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )
    
    hashed_password = get_password_hash(user.password)
    new_user = user_handler.create({
        "email": user.email,
        "password": hashed_password,
        "name": user.name
    })
    return User(
        id=str(new_user.id),
        email=new_user.email,
        name=new_user.name,
        created_at=new_user.created_at.isoformat(),
        last_active_at=new_user.last_active_at.isoformat()
    )

@router.post("/token", response_model=Token)
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    db: Session = Depends(get_global_db_session)
):
    user_handler = UserHandler(db)
    user = user_handler.get_by_email(form_data.username)
    if not user or not verify_password(form_data.password, user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": user.email}, expires_delta=access_token_expires
    )
    return {"access_token": access_token, "token_type": "bearer"}

@router.get("/me", response_model=User)
async def read_users_me(current_user: Annotated[User, Depends(get_current_user)]):
    return current_user

@router.post("/logout")
async def logout():
    # In a real application, you might want to invalidate the token
    # or perform some cleanup here
    return {"message": "Successfully logged out"}
