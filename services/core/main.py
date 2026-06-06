from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import os
import httpx  # Добавили асинхронный HTTP-клиент для межсервисного взаимодействия

app = FastAPI(title="CRM Core API", version="1.0.0")

# Настройка CORS, чтобы React мог отправлять запросы
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # В продакшене укажите конкретные домены
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Берем URL базы данных из переменных окружения Docker
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database")
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

@app.get("/api/v1/healthcheck")
async def health_check():
    # Отправляем лог в микросервис логгера по внутреннему имени сервиса в Docker-сети
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "level": "info", 
                    "message": "Healthcheck endpoint was hit"
                },
                timeout=2.0  # Ограничиваем время ожидания, чтобы бэкенд не зависал
            )
        except Exception:
            pass # Если логгер упал или недоступен, основной бэкенд продолжит работать

    try:
        # Проверяем подключение к базе данных с помощью функции text()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}
