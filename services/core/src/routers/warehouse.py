# services/core/src/routers/warehouse.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, Field

from src.database import get_db
from src.schemas.warehouse import CreateSupplierOrder, SupplierOrderResponse

# 🔥 Чистые атомарные импорты из папки компонентов
from src.components.order_manager import OrderManager
from src.components.order_splitter import OrderSplitter       
from src.components.analyzer_cache_manager import AnalyzerCacheManager 
from src.components.receipt_manager import ReceiptManager
from src.components.disassembly_manager import DisassemblyManager
from src.components.absorption_manager import AbsorptionManager
from src.components.supplier_manager import SupplierManager # Новой изолированный менеджер контрагентов

router = APIRouter(prefix="/warehouse", tags=["Склад и Логистика Закупок"])

class SupplierCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None

class NewReceiptItem(BaseModel):
    product_id: int = Field(..., description="ID номенклатурной карточки товара")
    quantity: int = Field(..., ge=1, description="Количество принимаемых единиц")
    actual_purchase_price: float = Field(..., ge=0, description="Фактическая цена закупки")

class SupplierInvoiceReceipt(BaseModel):
    supplier_id: int
    items: List[NewReceiptItem]

class DisassemblyTemplatedPayload(BaseModel):
    unique_serial_number: str = Field(..., description="Серийный номер разбираемого набора")

class DisassemblyPartialPayload(BaseModel):
    unique_serial_number: str = Field(..., description="Серийный номер вскрываемого набора")
    child_product_id: int = Field(..., description="ID детали, которую забирают из набора")

class SetAbsorptionPayload(BaseModel):
    parent_product_id: int = Field(..., description="ID карточки собираемого набора")
    satellite_unit_ids: List[int] = Field(..., description="Список ID физических юнитов-сателлитов")

class RuleCreatePayload(BaseModel):
    price_operator: str = Field(..., description="Математический оператор '>' или '<'")
    price_value: float = Field(..., ge=0, description="Пороговая стоимость товара")
    name_contains: Optional[str] = Field(None, description="Поиск по подстроке в названии, например 'бита'")
    stock_threshold: int = Field(..., ge=0, description="Порог критического остатка")

class ExceptionCreatePayload(BaseModel):
    product_id: int = Field(..., description="ID товара, который кассир пометил галочкой исключения")

@router.post("/suppliers", status_code=201)
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(get_db)):
    """🛠️ Делегируем задачу в изолированный атомарный менеджер"""
    return await SupplierManager.create_supplier(payload, db)

@router.get("/suppliers", response_model=List[dict])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    """📋 Делегируем задачу в изолированный атомарный менеджер"""
    return await SupplierManager.get_all_suppliers(db)

@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=SupplierOrderResponse)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    return await OrderManager.create_order(payload, db)

@router.get("/orders", status_code=200)
async def get_supplier_orders_split_list(db: AsyncSession = Depends(get_db)):
    return await OrderSplitter.get_orders_split(db)

@router.get("/pre-orders", status_code=200)
async def get_warehouse_analytics_pre_orders():
    """📋 Выдача кэша фронтенду (Менеджер сам автономно откроет сессию селекта)"""
    return await AnalyzerCacheManager.get_cached_pre_orders()

@router.post("/pre-orders/cache-update", status_code=200)
async def update_pre_orders_cache_from_analyzer(payload: list[dict]):
    """📥 Приём готового расчёта дефицита от микросервиса аналитики"""
    return await AnalyzerCacheManager.update_cache_payload(payload)

@router.get("/purchase-exceptions-raw", status_code=200)
async def get_raw_purchase_exceptions_list():
    """🔍 Отдача сырого черного списка для crm_analyzer_service"""
    return await AnalyzerCacheManager.get_raw_exceptions()

@router.post("/receipts", status_code=200)
async def process_supplier_invoice_receipt(payload: SupplierInvoiceReceipt, db: AsyncSession = Depends(get_db)):
    return await ReceiptManager.process_receipt(payload.supplier_id, payload.items, db)

@router.post("/disassembly/templated", status_code=200)
async def process_templated_disassembly(payload: DisassemblyTemplatedPayload, db: AsyncSession = Depends(get_db)):
    return await DisassemblyManager.execute_templated_disassembly(payload.unique_serial_number, db)

@router.post("/disassembly/partial", status_code=200)
async def process_partial_disassembly(payload: DisassemblyPartialPayload, db: AsyncSession = Depends(get_db)):
    return await DisassemblyManager.execute_partial_disassembly(payload.unique_serial_number, payload.child_product_id, db)

@router.post("/sets/absorb", status_code=200)
async def process_set_absorption(payload: SetAbsorptionPayload, db: AsyncSession = Depends(get_db)):
    return await AbsorptionManager.execute_set_absorption(payload.parent_product_id, payload.satellite_unit_ids, db)

@router.get("/purchase-rules", status_code=200)
async def get_all_dynamic_purchase_rules(db: AsyncSession = Depends(get_db)):
    """📋 Получение списка всех тегов-правил автозаказа напрямую из СУБД PostgreSQL"""
    from src.components.rule_engine import RuleEngine
    return await RuleEngine.get_rules(db) 

@router.post("/purchase-rules", status_code=201)
async def create_new_dynamic_purchase_rule(payload: RuleCreatePayload, db: AsyncSession = Depends(get_db)):
    """🛠️ Добавление нового правила из тегов в конструктор с фиксацией в СУБД"""
    from src.components.rule_engine import RuleEngine
    return await RuleEngine.add_rule(payload, db)

@router.post("/pre-orders/exclude", status_code=200)
async def exclude_product_from_pre_orders(payload: ExceptionCreatePayload):
    """🚫 Нажатие ГАЛОЧКИ: Исключения теперь вызываются автономно, убран лишний параметр db"""
    return await AnalyzerCacheManager.add_to_blacklist(payload.product_id) 
