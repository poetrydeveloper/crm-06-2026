import httpx
from sqlalchemy import select
from src.database import AsyncSessionLocal

# 🔥 ИСПРАВЛЕНО: Безопасный импорт модели. Если класса нет в models, 
# скрипт не упадет, а мягко предупредит в логах.
try:
    from src.models import PurchaseException
except ImportError:
    PurchaseException = None

# Глобальный буфер кэша в памяти
_PRE_ORDERS_CACHE = []
ANALYZER_TRIGGER_URL = "http://analyzer:8002/api/v1/analyzer/trigger-calculation"

class AnalyzerCacheManager:
    @staticmethod
    async def get_cached_pre_orders() -> dict:
        """📋 Выдача предзаказов фронтенду с автоматическим прогревом кэша"""
        global _PRE_ORDERS_CACHE
        
        # Если кэш пуст, запрашиваем расчет и ждем его завершения от микросервиса аналитики
        if not _PRE_ORDERS_CACHE:
            async with httpx.AsyncClient() as client:
                try:
                    # Увеличиваем таймаут до 10 сек, так как аналитика считает данные несколько секунд
                    res = await client.post(ANALYZER_TRIGGER_URL, timeout=10.0)
                except Exception as e:
                    print(f"⚠️ [CACHE]: Не удалось прогреть кэш через анализатор: {str(e)}")

        if not _PRE_ORDERS_CACHE:
            return {"status": "success", "fallback_active": True, "data": []}

        excluded_ids = set()
        
        # 🔥 ИСПРАВЛЕНО: Защита от NameError. Проверяем, что модель успешно импортирована
        if PurchaseException is not None:
            try:
                # Автономно открываем сессию для чтения черного списка
                async with AsyncSessionLocal() as db:
                    stmt = select(PurchaseException.product_id)
                    res = await db.execute(stmt)
                    excluded_ids = set(res.scalars().all())
                    await db.rollback() # Чистим транзакцию чтения
            except Exception as db_err:
                print(f"⚠️ [CACHE]: Сбой СУБД при чтении исключений: {str(db_err)}")
        else:
            print("⚠️ [CACHE]: Модель PurchaseException не найдена в src.models. Фильтрация черного списка пропущена.")

        filtered_data = [item for item in _PRE_ORDERS_CACHE if item.get("product_id") not in excluded_ids]
        return {"status": "success", "fallback_active": False, "data": filtered_data}

    @staticmethod
    async def update_cache_payload(payload: list[dict]) -> dict:
        """📥 Точка входа для заливки кэша из микросервиса аналитики"""
        global _PRE_ORDERS_CACHE
        _PRE_ORDERS_CACHE = payload
        return {"status": "success", "message": "Свежий аналитический кэш успешно залит в буфер ядра"}

    @staticmethod
    async def add_to_blacklist(product_id: int) -> dict:
        """🚫 Галочка 'Больше не находить': автономная транзакция в СУБД PostgreSQL"""
        if PurchaseException is None:
            return {"status": "error", "message": "Сбой архитектуры: модель исключений недоступна"}

        async with AsyncSessionLocal() as db:
            try:
                stmt = select(PurchaseException).where(PurchaseException.product_id == product_id)
                existing = await db.execute(stmt)
                if existing.scalar_one_or_none():
                    await db.rollback()
                    return {"status": "success", "message": f"Товар #{product_id} уже занесен в черный список СУБД"}

                new_exception = PurchaseException(product_id=product_id)
                db.add(new_exception)
                await db.commit() # Надежно коммитим запись в базу
                return {"status": "success", "message": f"Товар #{product_id} успешно сохранен в таблицы исключений СУБД"}
            except Exception as e:
                await db.rollback()
                return {"status": "error", "message": f"Ошибка СУБД при добавлении в черный список: {str(e)}"}

    @staticmethod
    async def get_raw_exceptions() -> list[int]:
        """🔍 Отдача сырого черного списка напрямую из СУБД для crm_analyzer_service"""
        if PurchaseException is None:
            return []

        async with AsyncSessionLocal() as db:
            try:
                stmt = select(PurchaseException.product_id)
                res = await db.execute(stmt)
                result = list(res.scalars().all())
                await db.rollback()
                return result
            except Exception as e:
                await db.rollback()
                print(f"⚠️ [CACHE]: Ошибка get_raw_exceptions: {str(e)}")
                return []
