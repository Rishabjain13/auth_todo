from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from datetime import date

from app.database.session import get_db
from app.models.todo import Todo
from app.models.todo_share import TodoShare   
from app.models.user import User              
from app.deps import get_current_user
from app.schemas.todo import TodoCreate, TodoUpdate, TodoResponse
from app.core.audit import create_audit_log, log_todo_update
from app.core.activity import emit_activity

router = APIRouter(prefix="/tasks", tags=["Tasks"])

@router.get("")
# @router.get("/")
def get_tasks(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Fetch all tasks visible to the current user.

    Includes:
    - Tasks owned by the user
    - Tasks shared with the user (viewer/editor)

    Deleted tasks are excluded.
    """
    user_id = int(payload["sub"])

    response = []

    owned = (
        db.query(Todo).filter(
            Todo.user_id == user_id,
            Todo.is_deleted == False
        )
        .all()
    )
    for t in owned:
        response.append({
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "completed": t.completed,
            "permission": "owner",
            "due_date": t.due_date.isoformat() if t.due_date else None
        })

    shared = (
        db.query(Todo, TodoShare.permission)
        .join(TodoShare, Todo.id == TodoShare.todo_id)
        .filter( TodoShare.user_id == user_id,
            Todo.is_deleted == False)
        .all()
    )

    for t, perm in shared:
        response.append({
            "id": t.id,
            "title": t.title,
            "priority": t.priority,
            "completed": t.completed,
            "permission": perm,
            "due_date": t.due_date.isoformat() if t.due_date else None
        })

    return response

@router.get("/overdue")
def get_overdue_tasks(
    db: Session = Depends(get_db),
    user=Depends(get_current_user)
):
    return (
        db.query(Todo)
        .filter(
            Todo.user_id == user.id,
            Todo.completed == False,
            Todo.due_date < date.today(),
            Todo.is_deleted == False
        )
        .all()
    )

@router.post("", response_model=TodoResponse)
async def create_task(
    data: TodoCreate,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Create a new task for the logged-in user.
    The creator becomes the task owner.
    """
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()
    if data.due_date is None:
        data.due_date = date.today()

    todo = Todo(
        title=data.title,
        priority=data.priority,
        due_date=data.due_date,
        completed=False,
        user_id=user_id,
        is_deleted=False
    )
    db.add(todo)
    db.commit()
    db.refresh(todo)

    create_audit_log(db, user_id, "TASK_CREATED", "Todo")

    await emit_activity(
        db=db,
        actor_id=user_id,
        action="created",
        entity="Task",
        title=todo.title,
        allowed_user_ids=[user_id]
    )
    return todo


@router.put("/{task_id}", response_model=TodoResponse)
async def update_task(
    task_id: int,
    data: TodoUpdate,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Update an existing task.

    Allowed:
    - Owner can edit
    - Editor can edit
    Viewer cannot edit.
    """
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    todo = (
        db.query(Todo)
        .filter(
            Todo.id == task_id,
            Todo.is_deleted == False
        )
        .first()
    )

    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    if todo.user_id != user_id:
        share = db.query(TodoShare).filter(
            TodoShare.todo_id == task_id,
            TodoShare.user_id == user_id,
            TodoShare.permission == "editor"
        ).first()

        if not share:
            raise HTTPException(status_code=403, detail="Edit not allowed")
            
    if data.title is not None:
        todo.title = data.title
    if data.priority is not None:
        todo.priority = data.priority
    if data.completed is not None:
        todo.completed = data.completed
    if data.due_date is not None:
        todo.due_date = data.due_date

    db.commit()
    db.refresh(todo)

    # ✅ FIX: correct audit call (no extra args)
    log_todo_update(db, user_id)    

    shared_users_id = (
        db.query(TodoShare.user_id)
        .filter(TodoShare.todo_id == task_id)
        .all()
    )

    allowed_user_ids = [todo.user_id] + [u[0] for u in shared_users_id]

    await emit_activity(
        db=db,
        actor_id=user_id,
        action="updated",
        entity="Task",
        title=todo.title,
        allowed_user_ids=allowed_user_ids
    )
    return todo


@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Soft delete a task.

    Only the task owner can delete.
    Task is marked as deleted, not removed from DB.
    """
    user_id = int(payload["sub"])
    user = db.query(User).filter(User.id == user_id).first()

    todo = db.query(Todo).filter(
        Todo.id == task_id,
        Todo.user_id == user_id,
        Todo.is_deleted == False
    ).first()

    if not todo:
        raise HTTPException(status_code=403, detail="Only owner can delete")

    todo.is_deleted = True
    db.commit()
    create_audit_log(db, user_id, "TASK_DELETED", "Todo")

    await emit_activity(
        db=db,
        actor_id=user_id,
        action="deleted",
        entity="Task",
        title=todo.title,
        allowed_user_ids=[user_id]
    )

    return {"status": "deleted"}


@router.post("/{task_id}/share")
async def share_task(
    task_id: int,
    user_email: str,
    permission: str,  
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Share a task with another user.

    Only the owner can share.
    Permissions allowed: viewer, editor.
    """
    user_id = int(payload["sub"])
    actor = db.query(User).filter(User.id == user_id).first()

    if permission not in ("viewer", "editor"):
        raise HTTPException(status_code=400, detail="Invalid permission")

    todo = (
        db.query(Todo)
        .filter(
            Todo.id == task_id,
            Todo.is_deleted == False
        )
        .first()
    )
    if not todo:
        raise HTTPException(status_code=404, detail="Task not found")

    if todo.user_id != user_id:
        raise HTTPException(status_code=403, detail="Only owner can share")

    user = db.query(User).filter(User.email == user_email).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    exists = db.query(TodoShare).filter(
        TodoShare.todo_id == task_id,
        TodoShare.user_id == user.id
    ).first()

    if exists:
        raise HTTPException(status_code=400, detail="Already shared")

    share = TodoShare(
        todo_id=task_id,
        user_id=user.id,
        permission=permission
    )

    db.add(share)
    db.commit()

    create_audit_log(db, user_id, "TASK_SHARED", "Todo")
    allowed_user_ids = [todo.user_id, user.id]

    await emit_activity(
        db=db,
        actor_id=actor.id,
        action=f"shared with {user.email}",
        entity="Task",
        title=todo.title,
        allowed_user_ids=allowed_user_ids
    )

    return {
        "status": "shared",
        "email": user.email,
        "permission": permission
    }
