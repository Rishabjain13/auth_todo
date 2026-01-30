from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import SessionLocal
from app.models.todo import Todo
from app.deps import get_current_user
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse

router = APIRouter(prefix="/tasks", tags=["Tasks"])


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@router.get("", response_model=list[TodoResponse])
def get_tasks(
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    return db.query(Todo).filter(Todo.user_id == user_id).all()


@router.post("", response_model=TodoResponse)
def create_task(
    data: TodoCreate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = Todo(
        title=data.title,
        priority=data.priority,
        completed=False,
        user_id=user_id
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo


@router.put("/{task_id}", response_model=TodoResponse)
def update_task(
    task_id: int,
    data: TodoUpdate,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.user_id == user_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    todo.title = data.title
    todo.priority = data.priority
    todo.completed = data.completed
    db.commit()
    db.refresh(todo)
    return todo


@router.delete("/{task_id}")
def delete_task(
    task_id: int,
    user_id: int = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    todo = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.user_id == user_id
    ).first()

    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    db.delete(todo)
    db.commit()
    return {"status": "deleted"}
