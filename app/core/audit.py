from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from datetime import datetime, timezone

def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
):
    try:
        log = AuditLog(
            user_id=user_id,
            action=action,
            entity=entity,
            timestamp=datetime.now(timezone.utc)
        )
        db.add(log)
        db.commit()
    except Exception:
        db.rollback()
        # audit must NEVER crash main request
        pass
def log_todo_update(db: Session, user_id: int):
    create_audit_log(db, user_id, "TASK_UPDATED", "Todo")