# services/core/src/components/analyzer_cache_manager.py
import httpx
from sqlalchemy.ext.asyncio import AsyncSession

# Оперативный буфер кэша внутри ядра СУБД для моментальной отдачи фронтенду
_PRE_ORDERS_CACHE = []
_EXCLUDED_PRODUCT_IDS = set()

ANALYZER_TRIGGER_URL = "http://crm_analyzer_service:8002/api/v1/analyzer/trigger-calculation"

class AnalyzerCacheManager:
    @staticmethod
    async def get_cached_pre_orders(db: AsyncSession) -> dict:
        """
        📋 Выдача предзаказов фронтенду.
        Если кэш пуст, ядро пытается экстренно пнуть аналитику по сети.
        Если аналитика лежит — срабатывает бронебойный плейсхолдер-фоллбэк!
        """
        global _PRE_ORDERS_CACHE
        
        # Если кэш пуст, пробуем принудительно триггернуть микросервис аналитики
        if not _PRE_ORDERS_CACHE:
            async with httpx.AsyncClient() as client:
                try:
                    res = await client.post(ANALYZER_TRIGGER_URL, timeout=1.5)
                    if res.status_code == 200:
                        # Аналитика успешно посчитала и обновила кэш через /cache-update
                        return {"status": "success", "fallback_active": False, "data": _PRE_ORDERS_CACHE}
                except Exception:
                    # Аналитика физически мертва или перегружена — включаем защитный плейсхолдер
                    pass

        # Если кэш по-прежнему пуст (фоллбэк-режим), отдаем пустой массив с флагом плейсхолдера
        if not _PRE_ORDERS_CACHE:
            return {
                "status": "success",
                "fallback_active": True,  # Сигнал фронтенду включить UI-плейсхолдер!
                "data": []
            }

        # Фильтруем выданный аналитикой кэш, отсекая product_id, на которые нажали галочку исключения
        filtered_data = [item for item in _PRE_ORDERS_CACHE if item.get("product_id") not in _EXCLUDED_PRODUCT_IDS]
        return {"status": "success", "fallback_active": False, "data": filtered_data}

    @staticmethod
    async def update_cache_payload(payload: list[dict]) -> dict:
        """📥 Ручка для микросервиса аналитики: загрузка свежего слепка расчетов дефицита"""
        global _PRE_ORDERS_CACHE
        _PRE_ORDERS_CACHE = payload
        return {"status": "success", "message": "Свежий аналитический кэш успешно залит в буфер ядра"}

    @staticmethod
    async def add_to_blacklist(product_id: int) -> dict:
        """🚫 Галочка 'Больше не находить': занесение товара в черный список исключений ядра"""
        global _EXCLUDED_PRODUCT_IDS
        _EXCLUDED_PRODUCT_IDS.add(product_id)
        return {"status": "success", "message": f"Товар #{product_id} успешно забанен на уровне ядра"}

    @staticmethod
    async def get_raw_exceptions() -> list[int]:
        """🔍 Отдача сырого черного списка для аналитического микросервиса"""
        return list(_EXCLUDED_PRODUCT_IDS)
