# services/core/src/components/analyzer_cache_manager.py
import httpx
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import PurchaseException

# Оперативный буфер кэша расчетов дефицита (остается в RAM для моментальной отдачи фронтенду)
_PRE_ORDERS_CACHE = []

# Исправлено: Домен сетевого имени сервиса из docker-compose — analyzer
ANALYZER_TRIGGER_URL = "http://analyzer:8002/api/v1/analyzer/trigger-calculation"

class AnalyzerCacheManager:
    @staticmethod
    async def get_cached_pre_orders(db: AsyncSession) -> dict:
        """
        📋 Выдача предзаказов фронтенду.
        Если кэш пуст, ядро пытается экстренно пнуть аналитику по сети.
        Если аналитика лежит — срабатывает бронебойный плейсхолдер-фоллбэк!
        """
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
            return {
                "status": "success",
                "fallback_active": True,  
                "data": []
            }

        # 🔍 ЧЕСТНЫЙ ВЫКАЧ ИСКЛЮЧЕНИЙ ИЗ ПОСТГРЕСА: Отсекаем забаненные в СУБД товары
        stmt = select(PurchaseException.product_id)
        res = await db.execute(stmt)
        excluded_ids = set(res.scalars().all())

        filtered_data = [item for item in _PRE_ORDERS_CACHE if item.get("product_id") not in excluded_ids]
        return {"status": "success", "fallback_active": False, "data": filtered_data}

    @staticmethod
    async def update_cache_payload(payload: list[dict]) -> dict:
        """📥 Ручка для микросервиса аналитики: загрузка свежего слепка расчетов дефицита"""
        global _PRE_ORDERS_CACHE
        _PRE_ORDERS_CACHE = payload
        return {"status": "success", "message": "Свежий аналитический кэш успешно залит в буфер ядра"}

    @staticmethod
    async def add_to_blacklist(product_id: int, db: AsyncSession) -> dict:
        """🚫 Галочка 'Больше не находить': физическая асинхронная запись в СУБД PostgreSQL"""
        # Проверяем, нет ли уже такого товара в исключениях, чтобы не поймать Unique Constraint Error
        stmt = select(PurchaseException).where(PurchaseException.product_id == product_id)
        existing = await db.execute(stmt)
        if existing.scalar_one_or_none():
            return {"status": "success", "message": f"Товар #{product_id} уже занесен в черный список СУБД"}

        new_exception = PurchaseException(product_id=product_id)
        db.add(new_exception)
        await db.commit()
        return {"status": "success", "message": f"Товар #{product_id} успешно сохранен в таблицы исключений СУБД"}

    @staticmethod
    async def get_raw_exceptions(db: AsyncSession) -> list[int]:
        """🔍 Отдача сырого черного списка напрямую из СУБД для аналитического микросервиса"""
        stmt = select(PurchaseException.product_id)
        res = await db.execute(stmt)
        return list(res.scalars().all())
