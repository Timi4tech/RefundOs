import hashlib
import math
from datetime import datetime, timezone, timedelta
from fastapi import APIRouter, Depends, HTTPException, Query, Header
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.application.dto.refund import CreateRefundRequest, RefundResponse, PaginatedRefunds
from app.infrastructure.database import AsyncSessionLocal, Refund, Transaction, IdempotencyKey
from app.infrastructure.security.auth import AuthenticatedUser
from app.infrastructure.security.permissions import require_customer
from app.core.config import settings

router = APIRouter(prefix="/api/v1/refunds", tags=["Refunds"])

def to_refund(item: Refund) -> RefundResponse:
    return RefundResponse(id=item.id, user_id=item.user_id, transaction_id=item.transaction_id, order_id=item.order_id, amount=item.amount, currency=item.transaction.currency, reason=item.reason, status=item.status, decision=item.decision, created_at=item.created_at, updated_at=item.updated_at)

@router.get("", response_model=PaginatedRefunds)
async def list_my_refunds(page:int=Query(1,ge=1), page_size:int=Query(10,ge=1,le=100), current_user:AuthenticatedUser=Depends(require_customer)):
    async with AsyncSessionLocal() as session:
        base = select(Refund).where(Refund.user_id == current_user.id)
        total = await session.scalar(select(func.count()).select_from(base.subquery())) or 0
        result = await session.scalars(base.options(selectinload(Refund.transaction)).order_by(Refund.created_at.desc()).offset((page-1)*page_size).limit(page_size))
        items = result.all()
    return PaginatedRefunds(items=[to_refund(x) for x in items], total=total, page=page, page_size=page_size, total_pages=max(1, math.ceil(total/page_size)))

@router.post("", response_model=RefundResponse, status_code=201)
async def create_refund(payload:CreateRefundRequest, current_user:AuthenticatedUser=Depends(require_customer), idempotency_key:str|None=Header(default=None, alias="Idempotency-Key")):
    if not idempotency_key or len(idempotency_key)>255:
        raise HTTPException(status_code=400, detail="Idempotency-Key header is required and must be at most 255 characters.")
    request_hash=hashlib.sha256(payload.model_dump_json().encode()).hexdigest()
    async with AsyncSessionLocal() as session:
        existing_key=await session.scalar(select(IdempotencyKey).where(IdempotencyKey.key==idempotency_key))
        if existing_key:
            if existing_key.user_id != current_user.id or existing_key.request_hash != request_hash:
                raise HTTPException(status_code=409, detail="Idempotency-Key has already been used for a different request.")
            if existing_key.response_id:
                existing_refund=await session.scalar(select(Refund).options(selectinload(Refund.transaction)).where(Refund.id==existing_key.response_id))
                if existing_refund: return to_refund(existing_refund)
            raise HTTPException(status_code=409, detail="This request is already being processed.")
        session.add(IdempotencyKey(key=idempotency_key,user_id=current_user.id,request_hash=request_hash,expires_at=datetime.now(timezone.utc)+timedelta(hours=24)))
        try:
            await session.commit()
        except Exception:
            await session.rollback()
            raise HTTPException(status_code=409, detail="This request is already being processed.")

    from uuid import uuid4
    from app.infrastructure.messaging.refund_rpc import request_refund
    request_id=str(uuid4())
    try:
        result=await request_refund({"request_id":request_id,"user_id":current_user.id,"transaction_id":payload.transaction_id,"amount":str(payload.amount) if payload.amount is not None else None,"reason":payload.reason}, settings.REFUND_WORKER_TIMEOUT_SECONDS)
    except Exception:
        raise HTTPException(status_code=503, detail="Refund processing service is temporarily unavailable.")
    if result.get("decision")=="REJECT":
        raise HTTPException(status_code=409, detail=result.get("message_context","Refund request was rejected."))
    if not result.get("refund_id"):
        raise HTTPException(status_code=503, detail="Refund processing did not create a ticket.")
    async with AsyncSessionLocal() as session:
        item=await session.scalar(select(Refund).options(selectinload(Refund.transaction)).where(Refund.id==result["refund_id"]))
        if item is None: raise HTTPException(status_code=503, detail="Refund ticket could not be loaded after processing.")
        key=await session.scalar(select(IdempotencyKey).where(IdempotencyKey.key==idempotency_key))
        if key:
            key.response_id=item.id
            await session.commit()
        return to_refund(item)
