from uuid import uuid4
import jwt
from fastapi import WebSocket, WebSocketDisconnect
from pydantic import BaseModel, Field, ValidationError
from sqlalchemy import select
from app.core.config import settings
from app.infrastructure.database import AsyncSessionLocal, User
from app.presentation.websocket.connection_manager import connection_manager
from app.application.refund_chat_orchestrator import refund_chat_orchestrator

class ChatSocketMessage(BaseModel):
    message: str = Field(min_length=1, max_length=4000)
    message_id: str | None = None
    history: list[dict[str, str]] = Field(default_factory=list, max_length=8)

async def _authenticate(websocket: WebSocket):
    token = websocket.query_params.get("token")
    if not token: return None
    try:
        payload=jwt.decode(token,settings.JWT_SECRET_KEY,algorithms=[settings.JWT_ALGORITHM])
        async with AsyncSessionLocal() as session:
            user=await session.scalar(select(User).where(User.id==str(payload["sub"])))
            if user is None or user.email != str(payload["email"]) or user.role.value != str(payload["role"]): return None
            return user
    except (jwt.InvalidTokenError,KeyError,ValueError): return None

async def chat_websocket(websocket: WebSocket):
    user=await _authenticate(websocket)
    if user is None:
        await websocket.close(code=1008,reason="Authentication required."); return
    connection_id=str(uuid4()); await connection_manager.connect(connection_id,websocket)
    try:
        while True:
            try:
                payload=ChatSocketMessage.model_validate(await websocket.receive_json()); message=payload.message.strip()
                if not message: raise ValueError()
            except (ValidationError,ValueError):
                await connection_manager.send(connection_id,{"type":"error","message":"Invalid message payload."}); continue
            message_id=payload.message_id or str(uuid4())
            await connection_manager.send(connection_id,{"type":"processing","message_id":message_id,"connection_id":connection_id,"message":"I’m checking that for you…"})
            try:
                response=await refund_chat_orchestrator.handle(user.id,message,payload.history)
                await connection_manager.send(connection_id,{"type":"assistant_message","message_id":message_id,"connection_id":connection_id,"message":response})
            except Exception:
                await connection_manager.send(connection_id,{"type":"error","message":"The support service could not process your request. Please try again."})
    except WebSocketDisconnect:
        await connection_manager.disconnect(connection_id)
    except Exception:
        await connection_manager.disconnect(connection_id)
