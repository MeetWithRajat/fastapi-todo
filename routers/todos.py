from models import Todos
from starlette import status
from typing import Annotated
from database import SessionLocal
from sqlalchemy.orm import Session
from .auth import get_current_user
from pydantic import BaseModel, Field
from fastapi import Path, APIRouter, Depends, HTTPException


router = APIRouter()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]
user_dependencies = Annotated[dict, Depends(get_current_user)]


class TodoRequest(BaseModel):
    title: str = Field(min_length=3)
    description: str = Field(min_length=3, max_length=100)
    priority: int = Field(ge=1, le=5)
    complete: bool = False


@router.get("/", status_code=status.HTTP_200_OK)
async def read_all(user: user_dependencies, db: db_dependency):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")
    return db.query(Todos).filter(Todos.owner_id == int(user.get('id'))).all()


@router.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependencies, db: db_dependency, todo_id: int = Path(ge=1)):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == int(user.get('id'))).first()
    if todo_model:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.post("/todo", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependencies, db: db_dependency, todo_request: TodoRequest):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")
    todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
    db.add(todo_model)
    db.commit()


@router.put("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependencies, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(ge=1)):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == int(user.get('id'))).first()
    if todo_model:
        todo_model.title = todo_request.title
        todo_model.description = todo_request.description
        todo_model.priority = todo_request.priority
        todo_model.complete = todo_request.complete
        # db.add(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Todo not found")


@router.delete("/todo/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependencies, db: db_dependency, todo_id: int = Path(ge=1)):
    if not user:
        raise HTTPException(status_code=404, detail="Authentication Failed")
    todo_model = db.query(Todos).filter(Todos.id == todo_id).filter(Todos.owner_id == int(user.get('id'))).first()
    if todo_model:
        db.delete(todo_model)
        db.commit()
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
