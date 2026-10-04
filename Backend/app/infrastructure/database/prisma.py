from contextlib import asynccontextmanager
from prisma import Prisma

prisma = Prisma()

async def connect_db() -> None:
    if not prisma.is_connected():
        await prisma.connect()

async def disconnect_db() -> None:
    if prisma.is_connected():
        await prisma.disconnect()

@asynccontextmanager
async def prisma_lifespan():
    await connect_db()
    try:
        yield
    finally:
        await disconnect_db()
