from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased
from sqlalchemy import or_

from app.database import SessionLocal
from app.models.user import User
from app.models.todo import Todo
from app.models.todo_share import TodoShare
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
    search: str | None = Query(None),
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    Owner = aliased(User)
    SharedUser = aliased(User)

    rows = (
        db.query(Todo, Owner, TodoShare, SharedUser)
        .join(Owner, Todo.user_id == Owner.id)
        .outerjoin(TodoShare, Todo.id == TodoShare.todo_id)
        .outerjoin(SharedUser, TodoShare.user_id == SharedUser.id)
        .all()
    )

    tasks = {}

    for todo, owner, share, shared_user in rows:
        if todo.id not in tasks:
            tasks[todo.id] = {
                "id": todo.id,
                "title": todo.title,
                "priority": todo.priority,
                "completed": todo.completed,
                "owner_email": owner.email,
                "shared_with": []
            }

        if share and shared_user:
            tasks[todo.id]["shared_with"].append({
                "user_email": shared_user.email,
                "permission": share.permission
            })

    result = []

    for task in tasks.values():
        if search:
            emails = [task["owner_email"]] + [
                s["user_email"] for s in task["shared_with"]
            ]
            if search.lower() not in [e.lower() for e in emails]:
                continue

        result.append(task)

    return result


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    task = db.query(Todo).filter(Todo.id == task_id).first()
    if not task:
        raise HTTPException(404, "Task not found")

    db.delete(task)
    db.commit()
    return {"status": "deleted"}
