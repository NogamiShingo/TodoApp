from fastapi import APIRouter, Depends, HTTPException, Path
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from database import SessionLocal
from models import Todos
from .auth import get_current_user

router = APIRouter(
  prefix='/admin',
  tags=['admin']
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
  if user is None or user.get('role') != 'admin':
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  return db.query(Todos).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None or user.get('role') != 'admin':
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
  return todo_model

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None or user.get('role') != 'admin':
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = db.query(Todos).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
  db.query(Todos).filter(Todos.id == todo_id).delete()
  db.commit()