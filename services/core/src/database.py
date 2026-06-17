import os
import sys
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Request

DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
)

async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,              
    pool_pre_ping=True,
    pool_size=10,           
    max_overflow=20          
)

AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  
    autocommit=False,
    autoflush=False
)

async def get_db(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    story_name = "ЖИВОЙ ПОЛЬЗОВАТЕЛЬ (БРАУЗЕР)"
    step_name = "РУЧНОЙ КЛИК"
    
    if request is not None:
        story_name = request.headers.get("X-QA-Story", story_name)
        step_name = request.headers.get("X-QA-Step", step_name)

    async with AsyncSessionLocal() as session:
        session_id = id(session)
        print(f"\n==========================================================================", flush=True)
        print(f"🎬 [BDD ТЕСТ]: {story_name.upper()}", flush=True)
        print(f"👉 [ШАГ ТЕСТА]: {step_name}", flush=True)
        print(f"🔹 [БАЗА ДАННЫХ] Открыта асинхронная сессия #{session_id}", flush=True)
        print(f"--------------------------------------------------------------------------", flush=True)
        try:
            yield session
            await session.commit() 
            print(f"✅ [СУБД] Транзакция сессии #{session_id} успешно зафиксирована.", flush=True)
        except Exception as e:
            print(f"🚨 [КРИТИЧЕСКИЙ СБОЙ] Ошибка в сессии #{session_id}!", file=sys.stderr, flush=True)
            await session.rollback() 
            raise
        finally:
            print(f"==========================================================================\n", flush=True)
            await session.close()
