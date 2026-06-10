import os
import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from src.database import async_engine
from src.routers.catalog import router as catalog_router
from src.routers.warehouse import router as warehouse_router
from src.routers.cash import router as cash_router

app = FastAPI(title="CRM Microservice Core API", version="1.0.0")

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

# ВЫРАВНЕНО ПОД ПРАВИЛА УРЕЗАНИЯ NGINX:
app.include_router(catalog_router, prefix="/api/v1")
app.include_router(warehouse_router, prefix="/api/v1")
app.include_router(cash_router, prefix="/v1") # ИСПРАВЛЕНО: Префикс /v1, так как Nginx уже отрезал /api/
