from app.models.user import User
from app.routes.activity_ws import send_to_users


async def emit_activity(
    db,
    actor_id: int,
    action: str,
    entity: str,
    title: str,
    allowed_user_ids: list[int]
):
    """
    Send activity ONLY to users allowed to see it
    """

    actor = db.query(User).filter(User.id == actor_id).first()

    payload = {
        "actor_email": actor.email if actor else "system",
        "action": action,
        "entity": entity,
        "title": title,
        "allowed_user_ids": allowed_user_ids
    }

    await send_to_users(payload)
   
