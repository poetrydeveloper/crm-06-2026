# services/core/src/database.py
import os
import sys
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from fastapi import Request

# 1. Получаем URL базы данных из переменных окружения
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
)

# 2. Создаем асинхронный движок для работы с PostgreSQL 16
async_engine = create_async_engine(
    DATABASE_URL,
    echo=True,              
    pool_pre_ping=True,
    pool_size=10,           
    max_overflow=20          
)

# 3. Фабрика для генерации изолированных асинхронных сессий транзакций
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  
    autocommit=False,
    autoflush=False
)

# 4. Функция-генератор с расширенной системой отчетов о транзакциях кассы и каталога
async def get_db(request: Request = None) -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для предоставления сессии БД с умным разделением по шагам BDD-тестов"""
    
    # 🔍 Вытаскиваем заголовки трассировки, которые прислал нам оркестратор тестов
    story_name = "ЖИВОЙ ПОЛЬЗОВАТЕЛЬ (БРАУЗЕР)"
    step_name = "РУЧНОЙ КЛИК"
    
    if request:
        story_name = request.headers.get("X-QA-Story", story_name)
        step_name = request.headers.get("X-QA-Step", step_name)

    async with AsyncSessionLocal() as session:
        session_id = id(session)
        
        # 🔥 ВИЗУАЛЬНЫЙ АНКОР: Печатаем жирный маркер шага прямо перед SQL-запросами!
        print(f"\n==========================================================================", flush=True)
        print(f"🎬 [BDD ТЕСТ]: {story_name.upper()}", flush=True)
        print(f"👉 [ШАГ ТЕСТА]: {step_name}", flush=True)
        print(f"🔹 [БАЗА ДАННЫХ] Открыта асинхронная сессия #{session_id}", flush=True)
        print(f"--------------------------------------------------------------------------", flush=True)
        
        try:
            yield session
            
            print(f"⏳ [СУБД] Эндпоинт отработал успешно. Применяем коммит для сессии #{session_id}...", flush=True)
            await session.commit() 
            print(f"✅ [СУБД] Транзакция сессии #{session_id} успешно зафиксирована.", flush=True)
            
        except Exception as e:
            print(f"🚨 [КРИТИЧЕСКИЙ СБОЙ] Ошибка в сессии #{session_id}!", file=sys.stderr, flush=True)
            print(f"🚨 [ДЕТАЛИ]: {str(e)}", file=sys.stderr, flush=True)
            print(f"⏪ [СУБД] Запускаем принудительный откат (ROLLBACK) для сессии #{session_id}...", file=sys.stderr, flush=True)
            await session.rollback() 
            raise
        finally:
            print(f"==========================================================================\n", flush=True)
            await session.close()
            
# 🔥 5. АВТОНОМНЫЙ ИЗОЛИРОВАННЫЙ ТРИГГЕР ИНИЦИАЛИЗАЦИИ ТАБЛИЦ (БЕЗ ДЕСТРУКТИВНЫХ СБОЕВ)
def init_db_tables_at_import():
    """Принудительно создает таблицы purchase_rules и purchase_exceptions при чтении файла Python"""
    from src.models import Base
    import src.models.purchase_rule
    import src.models.purchase_exception
    
    async def _execute_ddl():
        async with async_engine.begin() as conn:
            # 🛡️ БЕЗОПАСНЫЙ СУБД-СТАНДАРТ: Накатываем только недостающие структуры. 
            # Никаких DROP TABLE CASCADE, ломающих индексы FIFO кассы и наборов!
            await conn.run_sync(Base.metadata.create_all)
            
    try:
        loop = asyncio.get_running_loop()
        if loop.is_running():
            loop.create_task(_execute_ddl())
    except RuntimeError:
        asyncio.run(_execute_ddl())

# Запускаем генерацию DDL-структур СУБД прямо в момент импорта модуля
init_db_tables_at_import()
