from dotenv import load_dotenv
load_dotenv()

from fastapi import FastAPI
from fastapi.security import HTTPBearer
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from app.database import Base, engine
from app.routes.auth_routes import router as auth_router
from app.routes.todo_routes import router as todo_router
from app.routes.admin_routes import router as admin_router





Base.metadata.create_all(bind=engine)

app = FastAPI(title="TodoApp")
security = HTTPBearer()

BASE_DIR = Path(__file__).resolve().parent

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")

@app.get("/", response_class=HTMLResponse)
def dashboard():
    return (BASE_DIR / "static" / "index.html").read_text(encoding="utf-8")

@app.get("/login", response_class=HTMLResponse)
def login_page():
    return (BASE_DIR / "static" / "login.html").read_text(encoding="utf-8")

@app.get("/register", response_class=HTMLResponse)
def register_page():
    return (BASE_DIR / "static" / "register.html").read_text(encoding="utf-8")

app.include_router(auth_router)
app.include_router(todo_router)
app.include_router(admin_router)
