from fastapi import APIRouter, WebSocket, WebSocketDisconnect

router = APIRouter()
connections: list[WebSocket] = []

@router.websocket("/ws/activity")
async def activity_feed(ws: WebSocket):
    await ws.accept()
    connections.append(ws)
    try:
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        connections.remove(ws)

async def broadcast_activity(data: dict):
    for ws in connections:
        await ws.send_json(data)
