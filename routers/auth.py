from models import Users
from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class UserRequest(BaseModel):
    email: str
    username: str
    first_name: str
    last_name: str
    password: str
    role: str


@router.post("/auth")
async def create_user(user_request: UserRequest):
    user_model = Users(
        email=user_request.email,
        username=user_request.username,
        first_name=user_request.first_name,
        last_name=user_request.last_name,
        hashed_password=user_request.password,
        role=user_request.role,
        is_active=True
    )
    return user_model
