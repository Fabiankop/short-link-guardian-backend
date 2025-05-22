from fastapi import APIRouter, WebSocket, WebSocketDisconnect, Query, status
from jose import JWTError
from app.core.security import decode_access_token

router = APIRouter()

@router.websocket("/ws/echo")
async def websocket_echo(websocket: WebSocket, token: str = Query(...)):
    try:
        payload = decode_access_token(token)
        user_id = payload.get("sub")
        if not user_id:
            await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
            return
    except JWTError:
        await websocket.close(code=status.WS_1008_POLICY_VIOLATION)
        return
    await websocket.accept()
    try:
        while True:
            data = await websocket.receive_text()
            await websocket.send_text(f"Echo: {data}")
    except WebSocketDisconnect:
        pass
