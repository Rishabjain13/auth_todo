# from app.routes.activity_ws import broadcast_activity

# async def emit_activity(
#     email: str,
#     role: str,
#     action: str,
#     entity: str,
#     title: str | None = None
# ):
#     await broadcast_activity({
#         "email": email,
#         "role": role,
#         "action": action,
#         "entity": entity,
#         "title": title
#     })
from app.routes.activity_ws import broadcast_activity

async def emit_activity(
    *,
    actor_email: str,
    actor_role: str,
    action: str,
    entity: str,
    title: str,
    visible_to_emails: list[str]
):
    await broadcast_activity({
        "actor_email": actor_email,
        "role": actor_role.lower(),
        "action": action,
        "entity": entity,
        "title": title,
        "visible_to": visible_to_emails
    })
