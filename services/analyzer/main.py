import os
import httpx
from fastapi import FastAPI, status
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text
# 🔥 ИСПРАВЛЕНО: Используем специальный асинхронный планировщик вместо фоновых потоков
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from contextlib import asynccontextmanager

# 🔥 ПЛОСКИЙ ИМПОРТ: analytics_modules лежит прямо на корне рядом с main.py
from analytics_modules.deficit_engine import DeficitEngine

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database")
engine = create_async_engine(DATABASE_URL, echo=True)
CORE_URL = "http://backend:8000" 

async def execute_deficit_cron_job():
    """🤖 ФОНОВЫЙ КРОН-ЗАДАЧА: Автоматический обсчет дефицита розничной сети"""
    print("⏳ [CRON]: Запуск планового 5-минутного расчета матрицы снабжения...")
    computed_pre_orders = await DeficitEngine.run_calculation(engine)
    
    async with httpx.AsyncClient() as client:
        try:
            await client.post(f"{CORE_URL}/api/v1/warehouse/pre-orders/cache-update", json=computed_pre_orders)
            print(f"✅ [CRON]: Аналитический кэш успешно обновлен. Записей: {len(computed_pre_orders)}")
        except Exception as e:
            print(f"❌ [CRON]: Сбой отправки кэша в ядро: {str(e)}")

@asynccontextmanager
async def lifespan(app: FastAPI):
    """⏳ Настройка и запуск планировщика при старте контейнера"""
    # 🔥 ИСПРАВЛЕНО: Теперь планировщик работает внутри единого Event Loop с FastAPI
    scheduler = AsyncIOScheduler()
    # Передаем напрямую асинхронную функцию без оберток и потоков
    scheduler.add_job(execute_deficit_cron_job, 'interval', minutes=5, id='deficit_calc_job')
    scheduler.start()
    yield
    scheduler.shutdown()

# 🔥 ИСПРАВЛЕНО: Корректное имя аргумента lifespan
app = FastAPI(title="CRM Analytics Service", version="1.0.0", lifespan=lifespan)

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "crm_analyzer_service"}

@app.get("/api/v1/analytics/summary")
async def get_analytics_summary():
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
            await conn.commit()
        return {
            "status": "success",
            "metrics": {"total_sales": 150000, "active_customers": 42, "conversion_rate": "12.5%"}
        }
    except Exception as e:
        return {"status": "error", "detail": str(e)}

@app.post("/api/v1/analyzer/trigger-calculation", status_code=200)
async def trigger_supply_chain_calculation():
    """🛠️ Ручной эндпоинт (сохранен для совместимости с BDD тестами)"""
    await execute_deficit_cron_job()
    return {"status": "success", "message": "Аналитический пересчет матриц снабжения запущен вручную."}
