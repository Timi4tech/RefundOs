import asyncio
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import select
from app.core.config import settings
from app.infrastructure.database import connect_db, disconnect_db, AsyncSessionLocal, User
from app.presentation.middleware.request_id_middleware import RequestIdMiddleware
from app.presentation.middleware.ratelimit_middleware import RateLimitMiddleware
from app.presentation.middleware.error_middleware import unhandled_error_handler
from app.presentation.routes.auth import router as auth_router
from app.presentation.routes.refunds import router as refunds_router
from app.presentation.routes.admin import router as admin_router
from app.presentation.routes.developer import router as developer_router
from app.presentation.routes.chat import router as chat_router
from app.presentation.websocket.websocket_consumer import chat_websocket
from app.infrastructure.messaging.rabbitmq import rabbitmq_client
from app.infrastructure.messaging.refund_rpc import start_refund_response_listener

async def _connect_rabbitmq(attempts: int = 15, delay: float = 3.0) -> None:
    for attempt in range(1, attempts + 1):
        try:
            await rabbitmq_client.connect()
            return
        except Exception:
            if attempt == attempts:
                raise
            await asyncio.sleep(delay)

@asynccontextmanager
async def lifespan(app:FastAPI):
    await connect_db()
    await _connect_rabbitmq()
    await start_refund_response_listener()
    try: yield
    finally:
        await rabbitmq_client.close(); await disconnect_db()

app=FastAPI(title="Banking Refund API",version="1.0.0",lifespan=lifespan)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins,allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
app.add_middleware(RequestIdMiddleware); app.add_middleware(RateLimitMiddleware); app.add_exception_handler(Exception,unhandled_error_handler)
app.include_router(auth_router); app.include_router(refunds_router); app.include_router(admin_router); app.include_router(developer_router); app.include_router(chat_router)

@app.get("/health",tags=["Health"])
async def health(): return {"status":"healthy"}

@app.get("/ready",tags=["Health"])
async def ready():
    async with AsyncSessionLocal() as session: await session.scalar(select(User.id).limit(1))
    return {"status":"ready"}

@app.websocket("/api/v1/ws/chat")
async def websocket_chat(websocket:WebSocket): await chat_websocket(websocket)
