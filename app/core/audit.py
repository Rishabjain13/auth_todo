from sqlalchemy.orm import Session
from app.models.audit_log import AuditLog
from app.routes.activity_ws import connections
from datetime import datetime, timezone

async def broadcast_activity(data):
    for ws in connections:
        await ws.send_json(data)

def create_audit_log(
    db: Session,
    user_id: int | None,
    action: str,
    entity: str,
    admin_email: str | None = None
):
    try:
        log = AuditLog(
            user_id=user_id,
            # admin_email=admin_email,
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
