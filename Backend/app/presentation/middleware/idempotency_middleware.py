from datetime import datetime, timedelta, timezone
import hashlib
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
from sqlalchemy import select
from app.infrastructure.database import AsyncSessionLocal, IdempotencyKey

class IdempotencyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        if request.method not in {"POST","PUT","PATCH"} or request.url.path in {"/api/v1/auth/login","/api/v1/auth/signup"}:
            return await call_next(request)
        key=request.headers.get("Idempotency-Key")
        if not key: return await call_next(request)
        if len(key)>255: return JSONResponse(status_code=400,content={"detail":"Idempotency-Key is too long."})
        body=await request.body(); digest=hashlib.sha256(body).hexdigest(); user_id=getattr(request.state,"user_id",None)
        if not user_id: return await call_next(request)
        try:
            async with AsyncSessionLocal() as session:
                existing=await session.scalar(select(IdempotencyKey).where(IdempotencyKey.key==key))
                if existing:
                    if existing.request_hash != digest or existing.user_id != user_id:
                        return JSONResponse(status_code=409,content={"detail":"Idempotency-Key has already been used for a different request."})
                    return JSONResponse(status_code=409,content={"detail":"This request has already been processed or is currently in progress."})
                session.add(IdempotencyKey(key=key,user_id=user_id,request_hash=digest,expires_at=datetime.now(timezone.utc)+timedelta(hours=24)))
                await session.commit()
        except Exception:
            pass
        return await call_next(request)
