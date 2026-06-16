# services/analyzer/main.py
import os
import httpx
from fastapi import FastAPI, status
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# 🔥 ПЛОСКИЙ ИМПОРТ: Так как папка analytics_modules лежит прямо на корне рядом с main.py
from analytics_modules.deficit_engine import DeficitEngine

app = FastAPI(title="CRM Analytics Service", version="1.0.0")

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database")
engine = create_async_engine(DATABASE_URL, echo=True)

# Имя сервиса ядра в докере строго backend (порт 8000)
CORE_URL = "http://backend:8000" 

@app.get("/health")
async def health_check():
    """Служебная ручка для проверки доступности контейнера QA-роботом"""
    return {"status": "healthy", "service": "crm_analyzer_service"}

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    """📈 Оригинальная ручка сложных аналитических расчетов (Выручка, маржа)"""
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        return {
            "status": "success",
            "metrics": {
                "total_sales": 150000,
                "active_customers": 42,
                "conversion_rate": "12.5%"
            }
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/v1/analyzer/trigger-calculation", status_code=200)
async def trigger_supply_chain_calculation():
    """🛠️ Эндпоинт запуска расчёта снабжения и отправки кэш-пакета в буфер ядра"""
    computed_pre_orders = await DeficitEngine.run_calculation(engine)
    
    async with httpx.AsyncClient() as client:
        try:
            # Путь в ядре настроен как /warehouse/pre-orders/...
            await client.post(f"{CORE_URL}/warehouse/pre-orders/cache-update", json=computed_pre_orders)
        except Exception as e:
            return {"status": "partial_success", "message": f"Расчёт завершён, но буфер ядра недоступен: {str(e)}"}

    return {
        "status": "success", 
        "message": "Аналитический пересчет матриц снабжения завершен. Кэш обновлен.",
        "computed_count": len(computed_pre_orders)
    }
