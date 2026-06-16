# services/core/src/database.py
import os
import sys
import asyncio
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

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
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для предоставления сессии БД с логированием коммитов и откатов"""
    async with AsyncSessionLocal() as session:
        session_id = id(session)
        print(f"🔹 [БАЗА ДАННЫХ] Открыта новая асинхронная сессия #{session_id}", flush=True)
        try:
            yield session
            
            print(f"⏳ [БАЗА ДАННЫХ] Эндпоинт отработал успешно. Применяем коммит для сессии #{session_id}...", flush=True)
            await session.commit() 
            print(f"✅ [БАЗА ДАННЫХ] Транзакция сессии #{session_id} успешно зафиксирована in СУБД.", flush=True)
            
        except Exception as e:
            print(f"🚨 [КРИТИЧЕСКИЙ СБОЙ БАЗЫ ДАННЫХ] Ошибка в сессии #{session_id}!", file=sys.stderr, flush=True)
            print(f"🚨 [ДЕТАЛИ ИСКЛЮЧЕНИЯ]: {str(e)}", file=sys.stderr, flush=True)
            print(f"⏪ [БАЗА ДАННЫХ] Запускаем принудительный откат (ROLLBACK) для сессии #{session_id}...", file=sys.stderr, flush=True)
            await session.rollback() 
            print(f"🛑 [БАЗА ДАННЫХ] Откат сессии #{session_id} завершен. Данные в безопасности.", file=sys.stderr, flush=True)
            raise

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
