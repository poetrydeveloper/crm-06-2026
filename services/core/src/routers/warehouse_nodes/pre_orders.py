# services/core/src/routers/warehouse_nodes/pre_orders.py
from fastapi import APIRouter, status
# 🔥 ИСПРАВЛЕНО: Прописан корректный путь к файлу компонента
from src.components.analyzer_cache_manager import AnalyzerCacheManager 

router = APIRouter(tags=["Склад: Аналитика и Предзаказы"])

@router.post("/pre-orders/cache-update", status_code=200)
async def update_pre_orders_cache_from_analyzer(payload: list[dict]):
    """📥 Приём готового расчёта дефицита от микросервиса аналитики"""
    return await AnalyzerCacheManager.update_cache_payload(payload)

@router.get("/purchase-exceptions-raw", status_code=200)
async def get_raw_purchase_exceptions_list():
    """🔍 Отдача сырого черного списка для crm_analyzer_service"""
    return await AnalyzerCacheManager.get_raw_exceptions()

@router.post("/pre-orders/exclude", status_code=200)
async def exclude_product_from_pre_orders(payload: dict):
    """🚫 Нажатие ГАЛОЧКИ: Исключения теперь вызываются автономно"""
    product_id = payload.get("product_id")
    return await AnalyzerCacheManager.add_to_blacklist(product_id)
