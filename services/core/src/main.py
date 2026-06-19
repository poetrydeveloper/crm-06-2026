# services/core/src/main.py
import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text
from contextlib import asynccontextmanager

from src.database import async_engine
from src.routers.catalog import router as catalog_router
from src.routers.warehouse import router as warehouse_router
from src.routers.cash import router as cash_router

# 🛡️ ИСПРАВЛЕНО: Импортируем Base строго из первоисточника models/base.py,
# полностью исключая двоение реестра метадаты из-за промежуточного __init__.py
from src.models.base import Base

# 🔥 СТРОГИЙ ЯВНЫЙ ИМПОРТ ВСЕЙ НОМЕНКЛАТУРЫ ДЛЯ РЕГИСТРАЦИИ В METADATA
import src.models.brand
import src.models.category
import src.models.product
import src.models.product_unit
import src.models.supplier
import src.models.purchase_rule       # Подключаем физическую таблицу правил
import src.models.purchase_exception  # Подключаем физическую таблицу исключений

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    🛡️ БРОНЕБОЙНАЯ ОРМ-ИНИЦИАЛИЗАЦИЯ:
    Гарантирует 100% сборку всех таблиц в единый реестр и штампует их в PostgreSQL
    строго до старта обработки входящих сетевых запросов.
    """
    async with async_engine.begin() as conn:
        # Теперь реестр Base.metadata.tables гарантированно содержит 'purchase_rules' и 'purchase_exceptions'
        await conn.run_sync(Base.metadata.create_all)
    yield

app = FastAPI(title="CRM Microservice Core API", version="1.0.0", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/v1/healthcheck", tags=["Системные"])
async def health_check():
    async with httpx.AsyncClient() as client:
        try:
            await client.post("http://logger:8001/api/v1/log", json={"service": "core", "operation_code": "0000", "level": "INFO", "message": "Healthcheck endpoint hit."}, timeout=2.0)
        except Exception:
            pass
    try:
        async with async_engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {"status": "healthy", "service": "crm_backend_core", "database": "connected"}
    except Exception as e:
        return {"status": "unhealthy", "database": str(e)}

app.include_router(catalog_router, prefix="/api/v1")
app.include_router(warehouse_router, prefix="/api/v1")
app.include_router(cash_router, prefix="/api/v1")
