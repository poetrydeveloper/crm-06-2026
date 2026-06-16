# services/core/src/components/analyzer_cache_manager.py
import httpx
from sqlalchemy import select
from src.database import AsyncSessionLocal  # 🔥 Импортируем вашу фабрику сессий напрямую
from src.models import PurchaseException

_PRE_ORDERS_CACHE = []
ANALYZER_TRIGGER_URL = "http://analyzer:8002/api/v1/analyzer/trigger-calculation"

class AnalyzerCacheManager:
    @staticmethod
    async def get_cached_pre_orders() -> dict:
        """📋 Выдача предзаказов фронтенду с автономным открытием сессии СУБД"""
        global _PRE_ORDERS_CACHE
        
        if not _PRE_ORDERS_CACHE:
            async with httpx.AsyncClient() as client:
                try:
                    res = await client.post(ANALYZER_TRIGGER_URL, timeout=1.5)
                    if res.status_code == 200:
                        return {"status": "success", "fallback_active": False, "data": _PRE_ORDERS_CACHE}
                except Exception:
                    pass

        if not _PRE_ORDERS_CACHE:
            return {"status": "success", "fallback_active": True, "data": []}

        # 🔥 Автономно открываем сессию для чтения исключений
        async with AsyncSessionLocal() as db:
            stmt = select(PurchaseException.product_id)
            res = await db.execute(stmt)
            excluded_ids = set(res.scalars().all())

        filtered_data = [item for item in _PRE_ORDERS_CACHE if item.get("product_id") not in excluded_ids]
        return {"status": "success", "fallback_active": False, "data": filtered_data}

    @staticmethod
    async def update_cache_payload(payload: list[dict]) -> dict:
        global _PRE_ORDERS_CACHE
        _PRE_ORDERS_CACHE = payload
        return {"status": "success", "message": "Свежий аналитический кэш успешно залит в буфер ядра"}

    @staticmethod
    async def add_to_blacklist(product_id: int) -> dict:
        """🚫 Галочка 'Больше не находить': автономная транзакция в СУБД PostgreSQL"""
        async with AsyncSessionLocal() as db:
            stmt = select(PurchaseException).where(PurchaseException.product_id == product_id)
            existing = await db.execute(stmt)
            if existing.scalar_one_or_none():
                return {"status": "success", "message": f"Товар #{product_id} уже занесен в черный список СУБД"}

            new_exception = PurchaseException(product_id=product_id)
            db.add(new_exception)
            await db.commit()  # Жестко и надежно коммитим внутри изолированного контекста
            return {"status": "success", "message": f"Товар #{product_id} успешно сохранен в таблицы исключений СУБД"}

    @staticmethod
    async def get_raw_exceptions() -> list[int]:
        """🔍 Отдача сырого черного списка напрямую из СУБД для crm_analyzer_service"""
        async with AsyncSessionLocal() as db:
            stmt = select(PurchaseException.product_id)
            res = await db.execute(stmt)
            return list(res.scalars().all())
