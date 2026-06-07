# services/core/src/database.py
import os
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession

# 1. Получаем URL базы данных из переменных окружения (подставляется из docker-compose)
DATABASE_URL = os.getenv(
    "DATABASE_URL", 
    "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
)

# 2. Создаем асинхронный движок для работы с PostgreSQL 16
# pool_pre_ping=True автоматически проверяет живое ли соединение перед отправкой запроса
async_engine = create_async_engine(
    DATABASE_URL,
    echo=False,              # Поставь True, если нужно будет видеть сырые SQL-запросы в консоли Docker
    pool_pre_ping=True,
    pool_size=10,            # Базовое количество одновременных соединений в пуле
    max_overflow=20          # Максимальное количество дополнительных соединений при пиковых нагрузках кассы
)

# 3. Фабрика для генерации изолированных асинхронных сессий транзакций
AsyncSessionLocal = async_sessionmaker(
    bind=async_engine,
    class_=AsyncSession,
    expire_on_commit=False,  # Защищает объекты SQLAlchemy от инвалидации после коммита
    autocommit=False,
    autoflush=False
)

# 4. Функция-генератор (Зависимость FastAPI) для внедрения сессии БД в эндпоинты
# Конструкция async with гарантирует, что сессия и транзакция закроются автоматически, даже при ошибке в коде
async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Зависимость для предоставления асинхронной сессии базы данных на каждый HTTP-запрос"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit() # Автоматический коммит, если эндпоинт отработал без исключений
        except Exception:
            await session.rollback() # Полный откат транзакции в случае любой непредвиденной ошибки
            raise
