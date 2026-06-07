# services/core/src/main.py
import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

# Импортируем асинхронный движок из нашего модуля БД и роутер каталога
from src.database import async_engine
from src.routers.catalog import router as catalog_router

app = FastAPI(
    title="CRM Microservice Core API",
    description="Ядро FARM-системы CRM: FIFO учет, Умный поиск, Наборы, Логирование и Касса",
    version="1.0.0"
)

# Настройка CORS, чтобы React мог общаться с бэкендом напрямую при отладке
# При работе через Nginx CORS не сработает, но для гибкости разработки оставляем
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- ОБНОВЛЕННЫЙ HEALTHCHECK С АСИНХРОННЫМ МЕЖСЕРВИСНЫМ ЛОГИРОВАНИЕМ ---
@app.get("/api/v1/healthcheck", tags=["Системные"])
async def health_check():
    """Проверка жизнеспособности ядра, связи с БД и асинхронной отправки лога по Коду команды"""
    
    # Отправляем лог в микросервис логгера по внутренней Docker-сети
    async with httpx.AsyncClient() as client:
        try:
            # Логгер теперь принимает структуру под наше ТЗ
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": "0000", # Системный код проверки
                    "level": "INFO", 
                    "message": "Healthcheck endpoint was hit. Core infrastructure is stable."
                },
                timeout=2.0  # Защита от зависания ядра, если логгер недоступен
            )
        except Exception:
            pass # Если логгер временно отключен, ядро продолжает летать

    # Проверяем живое асинхронное подключение к PostgreSQL 16
    try:
        # Используем глобальный async_engine из database.py
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "healthy", 
            "service": "crm_backend_core",
            "database": "connected"
        }
    except Exception as e:
        return {
            "status": "unhealthy", 
            "service": "crm_backend_core",
            "database": str(e)
        }

# --- РЕГИСТРАЦИЯ НАШИХ УМНЫХ РОУТЕРОВ ---
# Все эндпоинты каталога и поиска автоматически получат префикс /api/v1
app.include_router(catalog_router, prefix="/api/v1")
