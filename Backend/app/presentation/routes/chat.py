from fastapi import APIRouter, Depends
from app.application.dto.chat import ChatRequest, ChatResponse
from app.application.refund_chat_orchestrator import refund_chat_orchestrator
from app.infrastructure.security.auth import AuthenticatedUser
from app.infrastructure.database import AsyncSessionLocal, AuditLog
from app.infrastructure.security.permissions import require_customer

router = APIRouter(prefix="/api/v1", tags=["Support"])

@router.post("/chat", response_model=ChatResponse)
async def chat(payload: ChatRequest, current_user: AuthenticatedUser = Depends(require_customer)):
    message = payload.message.strip()
    history = [item.model_dump() for item in payload.history]
    response = await refund_chat_orchestrator.handle(current_user.id, message, history)
    async with AsyncSessionLocal() as session:
        session.add(AuditLog(actor_type=current_user.role.value, actor_id=current_user.id, action="CHAT_MESSAGE", note="Customer support chat message processed by Gemini refund orchestration.", metadata_json={"message_length": len(message)}))
        await session.commit()
    return ChatResponse(message=response)
