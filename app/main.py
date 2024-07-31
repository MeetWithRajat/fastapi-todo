import models
from models import Todos
from starlette import status
from typing import Annotated
from sqlalchemy.orm import Session
from database import engine, SessionLocal
from fastapi import Path, FastAPI, Depends, HTTPException


app = FastAPI()

models.Base.metadata.create_all(bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


db_dependency = Annotated[Session, Depends(get_db)]


@app.get("/", status_code=status.HTTP_200_OK)
async def read_all(db: db_dependency):
    return db.query(Todos).all()


@app.get("/todo/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(db: db_dependency, todo_id: int = Path(ge=1)):
    todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
    if todo_model:
        return todo_model
    else:
        raise HTTPException(status_code=404, detail="Todo not found")
