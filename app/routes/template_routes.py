from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.task_template import TaskTemplate
from app.schemas.todo import TemplateCreate
from app.models.todo import Todo
from app.deps import get_current_user
from datetime import date

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("")
def list_templates(
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(payload["sub"])
    return db.query(TaskTemplate).filter(
        TaskTemplate.user_id == user_id
    ).all()


@router.post("")
def create_template(
    data: TemplateCreate,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(payload["sub"])

    template = TaskTemplate(
        name=data.name,
        title=data.title,
        priority=data.priority,
        user_id=user_id
    )

    db.add(template)
    db.commit()
    db.refresh(template)
    return template


@router.post("/{template_id}/use")
def use_template(
    template_id: int,
    payload: dict = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    user_id = int(payload["sub"])

    template = db.query(TaskTemplate).filter(
        TaskTemplate.id == template_id,
        TaskTemplate.user_id == user_id
    ).first()

    if not template:
        return {"detail": "Template not found"}

    todo = Todo(
        title=template.title,
        priority=template.priority,
        completed=False,
        user_id=user_id,
        is_deleted=False
    )

    db.add(todo)
    db.commit()
    db.refresh(todo)
    return todo

