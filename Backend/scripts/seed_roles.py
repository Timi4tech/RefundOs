import asyncio, os
from sqlalchemy import select
from app.infrastructure.database import AsyncSessionLocal, User
from app.infrastructure.security.auth import hash_password
from app.domain.enums.user import Role

async def main():
    async with AsyncSessionLocal() as session:
        for role, email_key, password_key, name_key in [(Role.ADMIN,"SEED_ADMIN_EMAIL","SEED_ADMIN_PASSWORD","SEED_ADMIN_NAME"),(Role.DEVELOPER,"SEED_DEVELOPER_EMAIL","SEED_DEVELOPER_PASSWORD","SEED_DEVELOPER_NAME")]:
            email=os.getenv(email_key,"").strip().lower(); password=os.getenv(password_key,""); name=os.getenv(name_key,role.title())
            if not email or not password: continue
            existing=await session.scalar(select(User).where(User.email==email))
            if existing: continue
            session.add(User(email=email,name=name,password_hash=hash_password(password),role=role))
        await session.commit()

if __name__=="__main__": asyncio.run(main())
