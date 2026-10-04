import math
from datetime import datetime,timedelta,timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, select
from sqlalchemy.orm import selectinload
from app.application.dto.refund import PaginatedRefunds, RefundResponse, RefundSummary, ReviewRefundRequest
from app.infrastructure.database import AsyncSessionLocal, Refund, Transaction, AuditLog
from app.domain.enums.refund import RefundStatus
from app.infrastructure.security.auth import AuthenticatedUser
from app.infrastructure.security.permissions import require_admin
from app.presentation.routes.refunds import to_refund

router=APIRouter(prefix="/api/v1/admin",tags=["Administration"])

@router.get("/refunds",response_model=PaginatedRefunds)
async def list_refunds(page:int=Query(1,ge=1),page_size:int=Query(10,ge=1,le=100),status:str|None=Query(default=None,pattern=r"^(PENDING|PROCESSING|APPROVED|REJECTED|REQUIRES_REVIEW|COMPLETED|FAILED)$"),refund_id:str|None=None,created_date:str|None=None,current_user:AuthenticatedUser=Depends(require_admin)):
    conditions=[]
    if status: conditions.append(Refund.status==RefundStatus(status))
    if refund_id: conditions.append(Refund.id==refund_id)
    if created_date:
        try: start=datetime.fromisoformat(created_date).replace(tzinfo=timezone.utc); conditions += [Refund.created_at>=start, Refund.created_at<start+timedelta(days=1)]
        except ValueError: raise HTTPException(status_code=422,detail="created_date must be YYYY-MM-DD.")
    async with AsyncSessionLocal() as session:
        stmt=select(Refund).where(*conditions)
        total=await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        result=await session.scalars(stmt.options(selectinload(Refund.transaction)).order_by(Refund.created_at.desc()).offset((page-1)*page_size).limit(page_size))
        items=result.all()
    return PaginatedRefunds(items=[to_refund(x) for x in items],total=total,page=page,page_size=page_size,total_pages=max(1,math.ceil(total/page_size)))

@router.get("/refunds/summary",response_model=RefundSummary)
async def summary(current_user:AuthenticatedUser=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        created=await session.scalar(select(func.count(Refund.id))) or 0
        approved=await session.scalar(select(func.count(Refund.id)).where(Refund.status==RefundStatus.APPROVED)) or 0
        rejected=await session.scalar(select(func.count(Refund.id)).where(Refund.status==RefundStatus.REJECTED)) or 0
        escalated=await session.scalar(select(func.count(Refund.id)).where(Refund.status==RefundStatus.REQUIRES_REVIEW)) or 0
    return RefundSummary(created=created,approved=approved,rejected=rejected,escalated=escalated)

@router.post("/refunds/{refund_id}/review",response_model=RefundResponse)
async def review_refund(refund_id:str,payload:ReviewRefundRequest,current_user:AuthenticatedUser=Depends(require_admin)):
    async with AsyncSessionLocal() as session:
        item=await session.scalar(select(Refund).options(selectinload(Refund.transaction)).where(Refund.id==refund_id))
        if item is None: raise HTTPException(status_code=404,detail="Refund not found.")
        if item.status.value in {"COMPLETED","REJECTED"}: raise HTTPException(status_code=409,detail=f"Refund is already {item.status.value.lower()}.")
        status_value="APPROVED" if payload.decision=="APPROVE" else "REJECTED"
        item.status=RefundStatus(status_value)
        item.decision=payload.decision
        if status_value=="APPROVED": item.transaction.refunded=True
        session.add(AuditLog(refund_id=refund_id,actor_type="ADMIN",actor_id=current_user.id,action="REFUND_APPROVED" if status_value=="APPROVED" else "REFUND_REJECTED",note=payload.note or f"Refund {status_value.lower()} by administrator.",metadata_json={"decision":payload.decision}))
        await session.commit(); await session.refresh(item)
        return to_refund(item)
