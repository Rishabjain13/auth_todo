from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.user import User
from app.models.todo import Todo
from app.deps import require_admin

router = APIRouter(prefix="/admin", tags=["Admin"])

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("/users")
def get_all_users(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(User).all()


@router.get("/tasks")
def get_all_tasks(
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    return db.query(Todo).all()
