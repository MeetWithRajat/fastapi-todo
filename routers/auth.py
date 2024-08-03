from jose import jwt
from models import Users
from starlette import status
from typing import Annotated
from pydantic import BaseModel
from database import SessionLocal
from sqlalchemy.orm import Session
from passlib.context import CryptContext
from datetime import timedelta, datetime, timezone
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

router = APIRouter()

SECRET_KEY = '861c6aa5c1766964f0469659b5f5f263c7c4ca44df9fa174efb5b0110d426e12'
ALGORITHM = 'HS256'

bcrypt_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


def authenticate_user(username: str, password: str, db):
    user = db.query(Users).filter(Users.username == username).first()
    if not user or not bcrypt_context.verify(password, user.hashed_password):
        return None
    return user


def create_access_token(username: str, user_id: int, expire_delta: timedelta):
    encode = {
        'sub': username,
        'id': user_id,
        'exp': datetime.now(timezone.utc) + expire_delta
    }
    return jwt.encode(encode, SECRET_KEY, algorithm=ALGORITHM)


@router.post("/auth", status_code=status.HTTP_201_CREATED)
async def create_user(db: db_dependency, user_request: UserRequest):
    user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=bcrypt_context.hash(user_request.password),
        role=user_request.role,
        is_active=True
    )
    db.add(user_model)
    db.commit()


@router.post("/token")
async def login_for_access_token(form_data: Annotated[OAuth2PasswordRequestForm, Depends()], db: db_dependency):
    user = authenticate_user(form_data.username, form_data.password, db)
    if user:
        token = create_access_token(user.username, user.id, timedelta(minutes=20))
        return {"access_token": token, "token_type": "bearer"}
    else:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")
