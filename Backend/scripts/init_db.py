import asyncio
from app.infrastructure.database import connect_db

if __name__ == "__main__":
    asyncio.run(connect_db())
