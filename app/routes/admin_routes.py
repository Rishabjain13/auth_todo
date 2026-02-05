from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session, aliased, joinedload
from sqlalchemy import or_

from app.database.session import get_db
from app.models.user import User
from app.models.todo import Todo
from app.models.todo_share import TodoShare
from app.deps import require_admin, get_current_admin_user
from app.models.audit_log import AuditLog
from app.core.audit import create_audit_log


router = APIRouter(prefix="/admin", tags=["Admin"])


@router.get("/users")
def get_all_users(
    page: int = 1,
    limit: int = 10,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to fetch all users.

    Supports pagination.
    Admin access only.
    """
    offset = (page - 1) * limit
    return (
        db.query(User)
        .offset(offset)
        .limit(limit)
        .all()
    )


@router.get("/tasks")
def get_all_tasks(
    search: str | None = Query(None),
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin endpoint to fetch all tasks.

    Includes:
    - Owner email
    - Shared users and permissions

    Supports search by owner/shared user email.
    Deleted tasks are excluded.
    """
    Owner = aliased(User)
    SharedUser = aliased(User)

    rows = (
        db.query(Todo, Owner, TodoShare, SharedUser)
        .join(Owner, Todo.user_id == Owner.id)
        .outerjoin(TodoShare, Todo.id == TodoShare.todo_id)
        .outerjoin(SharedUser, TodoShare.user_id == SharedUser.id)
        .filter(Todo.is_deleted == False)
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

@router.get("/audit-logs")
def get_audit_logs(
    user: str | None = Query(None, description="Search by user email"),
    action: str | None = Query(None),
    db: Session = Depends(get_db),
    _: dict = Depends(get_current_admin_user),
):
    query = (
        db.query(AuditLog)
        .options(joinedload(AuditLog.user))
    )

    if user:
        query = query.join(User).filter(
            User.email.ilike(f"%{user}%")
        )

    if action:
        query = query.filter(AuditLog.action == action)

    logs = query.order_by(AuditLog.timestamp.desc()).all()

    return [
        {
            "email": log.user.email if log.user else "system",
            "role": (
                log.user.role.upper()
                if log.user and log.user.role
                else "SYSTEM"
            ),
            "action": log.action,
            "entity": log.entity,
            "timestamp": log.timestamp,
        }
        for log in logs
    ]


@router.delete("/tasks/{task_id}")
def delete_task(
    task_id: int,
    _: dict = Depends(require_admin),
    db: Session = Depends(get_db)
):
    """
    Admin soft delete for tasks.

    Marks task as deleted and records audit log.
    """
    task = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.is_deleted == False
    ).first()

    if not task:
        raise HTTPException(404, "Task not found")

    # admin = db.query(User).filter(User.id == int(_["sub"])).first()

    task.is_deleted = True

    create_audit_log(
        db=db,
        user_id=int(_["sub"]),
        action="TASK_DELETED",
        entity="Todo"
    )
    db.commit()
    return {"status": "deleted"}
