from fastapi import FastAPI, Request, status
from fastapi.responses import RedirectResponse
# from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from models import Base
from database import engine
from routers import auth, todos, admin, user

app = FastAPI()

Base.metadata.create_all(bind=engine)

# templates = Jinja2Templates(directory="Project5/templates")

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/")
def test(request: Request):
	# return templates.TemplateResponse(request=request, name="home.html")
  return RedirectResponse(url="/todos/todo-page", status_code=status.HTTP_302_FOUND)

@app.get("/healthy")
async def health_check():
  return {'status': 'Healthy'}

app.include_router(auth.router)
app.include_router(todos.router)
app.include_router(admin.router)
app.include_router(user.router)