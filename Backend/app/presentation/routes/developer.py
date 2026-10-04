import math
from datetime import datetime,timedelta,timezone
from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy import func, select
from app.application.dto.audit_log import PaginatedAuditLogs, AuditLogResponse
from app.infrastructure.database import AsyncSessionLocal, AuditLog
from app.infrastructure.security.auth import AuthenticatedUser
from app.infrastructure.security.permissions import require_developer
router=APIRouter(prefix="/api/v1/developer",tags=["Developer"])

@router.get("/audit-logs",response_model=PaginatedAuditLogs)
async def audit_logs(page:int=Query(1,ge=1),page_size:int=Query(15,ge=1,le=100),created_date:str|None=None,current_user:AuthenticatedUser=Depends(require_developer)):
    conditions=[]
    if created_date:
        try: start=datetime.fromisoformat(created_date).replace(tzinfo=timezone.utc); conditions += [AuditLog.created_at>=start,AuditLog.created_at<start+timedelta(days=1)]
        except ValueError: raise HTTPException(status_code=422,detail="created_date must be YYYY-MM-DD.")
    async with AsyncSessionLocal() as session:
        stmt=select(AuditLog).where(*conditions)
        total=await session.scalar(select(func.count()).select_from(stmt.subquery())) or 0
        result=await session.scalars(stmt.order_by(AuditLog.created_at.desc()).offset((page-1)*page_size).limit(page_size))
        items=result.all()
    return PaginatedAuditLogs(items=[AuditLogResponse(id=x.id,refund_id=x.refund_id,actor_type=x.actor_type,actor_id=x.actor_id,action=x.action,note=x.note,metadata=x.metadata_json,created_at=x.created_at) for x in items],total=total,page=page,page_size=page_size,total_pages=max(1,math.ceil(total/page_size)))
