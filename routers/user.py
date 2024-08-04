from models import Users
from starlette import status
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from .auth import get_current_user, bcrypt_context
from fastapi import APIRouter, Depends, HTTPException


router = APIRouter(
    prefix='/user',
    tags=['user']
)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]


class UserVerification(BaseModel):
    current_password: str
    new_password: str = Field(min_length=6)


@router.get("/", status_code=status.HTTP_200_OK)
async def get_user(user: user_dependencies, db: db_dependency):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    return db.query(Users).filter(Users.id == int(user.get('id'))).first()


@router.put("/password", status_code=status.HTTP_204_NO_CONTENT)
async def change_password(user: user_dependencies, db: db_dependency, verification: UserVerification):
    if not user:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed')
    user_model = db.query(Users).filter(Users.id == int(user.get('id'))).first()
    if user_model and bcrypt_context.verify(verification.current_password, user_model.hashed_password):
        user_model.hashed_password = bcrypt_context.hash(verification.new_password)
        db.commit()
    else:
        raise HTTPException(status_code=401, detail="Error on password change")
