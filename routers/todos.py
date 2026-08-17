from fastapi import APIRouter, Depends, HTTPException, Path, Request
from fastapi.templating import Jinja2Templates
from typing import Annotated
from sqlalchemy.orm import Session
from starlette import status
from starlette.responses import RedirectResponse
from pydantic import BaseModel, Field
from models import Todos
from database import SessionLocal
from .auth import get_current_user

router = APIRouter(
  prefix='/todos',
  tags=['todos']
)

def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

user_dependency = Annotated[dict, Depends(get_current_user)]
db_dependency = Annotated[Session, Depends(get_db)]

class TodoRequest(BaseModel):
  title: str = Field(min_length=3)
  description: str = Field(min_length=3, max_length=100)
  priority: int = Field(gt=0, lt=6)
  complete: bool

templates = Jinja2Templates(directory="templates")

def redirect_to_login():
	redirect_response = RedirectResponse(url="/auth/login-page", status_code=status.HTTP_302_FOUND)
	redirect_response.delete_cookie(key="access_token")
	return redirect_response

### Pages ###

@router.get("/todo-page")
async def render_todo_page(request: Request, db: db_dependency):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		
		todos = db.query(Todos).filter(Todos.owner_id == user.get("id")).all()
		
		return templates.TemplateResponse(request=request, name="todos.html", context={"todos": todos, "user": user})
	except:
		return redirect_to_login()

@router.get("/add-todo-page")
async def render_todo_page(request: Request):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		return templates.TemplateResponse(request=request, name="add-todo.html", context={"user": user})
	except:
		return redirect_to_login()

@router.get("/edit-todo-page/{todo_id}")
async def render_edit_todo_page(request: Request, todo_id: int, db: db_dependency):
	try:
		user = await get_current_user(request.cookies.get('access_token'))
		if user is None:
			return redirect_to_login()
		todo = db.query(Todos).filter(Todos.id == todo_id).first()
		return templates.TemplateResponse(request=request, name="edit-todo.html", context={"user": user, "todo": todo})
	except:
		return redirect_to_login()

### Endpoints ### 

@router.post("/create", status_code=status.HTTP_201_CREATED)
async def create_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = Todos(**todo_request.model_dump(), owner_id=user.get('id'))
  db.add(todo_model)
  db.commit()

@router.get("/", status_code=status.HTTP_200_OK)
async def read_all_todos(user: user_dependency, db: db_dependency):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  return db.query(Todos).filter(Todos.owner_id == user.get('id')).all()

@router.get("/{todo_id}", status_code=status.HTTP_200_OK)
async def read_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
  return todo_model

@router.put("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def update_todo(user: user_dependency, db: db_dependency, todo_request: TodoRequest, todo_id: int = Path(gt=0)):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
  todo_model.title = todo_request.title
  todo_model.description = todo_request.description
  todo_model.priority = todo_request.priority
  todo_model.complete = todo_request.complete
  db.add(todo_model)
  db.commit()

@router.delete("/{todo_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_todo(user: user_dependency, db: db_dependency, todo_id: int = Path(gt=0)):
  if user is None:
    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail='Authentication Failed.')
  todo_model = db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).first()
  if todo_model is None:
    raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail='Todo not found.')
  db.query(Todos).filter(Todos.owner_id == user.get('id')).filter(Todos.id == todo_id).delete()
  db.commit()