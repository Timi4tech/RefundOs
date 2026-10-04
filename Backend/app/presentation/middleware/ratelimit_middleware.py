import time
from collections import defaultdict
from asyncio import Lock
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.responses import JSONResponse
class RateLimitMiddleware(BaseHTTPMiddleware):
    WINDOW_SECONDS=60
    MAX_REQUESTS=120
    def __init__(self, app):
        super().__init__(app); self._counts=defaultdict(lambda:[0,0.0]); self._lock=Lock()
    async def dispatch(self, request: Request, call_next):
        if request.url.path == "/health":
            return await call_next(request)
        key = request.client.host if request.client else "unknown"
        now=time.monotonic()
        async with self._lock:
            count,start=self._counts[key]
            if now-start >= self.WINDOW_SECONDS: count,start=0,now
            count+=1; self._counts[key]=[count,start]
        if count>self.MAX_REQUESTS:
            return JSONResponse(status_code=429,content={"detail":"Too many requests. Please try again later."},headers={"Retry-After":str(self.WINDOW_SECONDS)})
        response=await call_next(request)
        response.headers["X-RateLimit-Limit"]=str(self.MAX_REQUESTS)
        response.headers["X-RateLimit-Remaining"]=str(max(0,self.MAX_REQUESTS-count))
        return response
