from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from app.database.session import get_db
from app.deps import decode_token
from app.models.todo import Todo
from app.models.todo_share import TodoShare

router = APIRouter()

connections: dict[WebSocket, int] = {}

@router.websocket("/ws/activity")
async def activity_feed(ws: WebSocket):
    token = ws.query_params.get("token")
    payload = decode_token(token)

    if not payload:
        await ws.close(code=1008)
        return

    user_id = int(payload["sub"])

    # 🔒 CHECK: user must own OR be shared on at least one task
    db: Session = next(get_db())

    has_access = (
        db.query(Todo)
        .filter(Todo.user_id == user_id, Todo.is_deleted == False)
        .first()
        or
        db.query(TodoShare)
        .filter(TodoShare.user_id == user_id)
        .first()
    )

    if not has_access:
        await ws.close(code=1008)
        return

    await ws.accept()
    connections[ws] = user_id

    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.pop(ws, None)


async def send_to_users(data: dict):
    """
    data MUST contain:
    - allowed_user_ids: list[int]
    """
    allowed = set(data.get("allowed_user_ids", []))

    for ws, uid in list(connections.items()):
        if uid in allowed:
            try:
                await ws.send_json(data)
            except Exception:
                connections.pop(ws, None)
    