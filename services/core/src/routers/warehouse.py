# services/core/src/routers/warehouse.py (ЧАСТЬ 1 из 3)
import uuid
import httpx
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel, Field

from src.database import get_db
from src.models import Product, Supplier, ProductUnit, LogisticsStatus, PhysicalStatus, ProductAssemblyTemplate
from src.schemas.warehouse import CreateSupplierOrder, SupplierOrderResponse, OrderResponseItem

router = APIRouter(prefix="/warehouse", tags=["Склад и Логистика Закупок"])

# --- СХЕМЫ ВАЛИДАЦИИ ПОСТАВЩИКОВ ---
class SupplierCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None

# --- ИСПРАВЛЕННЫЕ СХЕМЫ ДЛЯ АВТОГЕНЕРАЦИИ СЕРИЙНИКОВ ПРИ ПРИЕМКЕ ---
class NewReceiptItem(BaseModel):
    product_id: int = Field(..., description="ID номенклатурной карточки товара")
    quantity: int = Field(..., ge=1, description="Количество принимаемых единиц")
    actual_purchase_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Фактическая цена закупки")

class SupplierInvoiceReceipt(BaseModel):
    supplier_id: int
    items: List[NewReceiptItem]

# --- НОВЫЕ ВАЛИДАЦИОННЫЕ МОДЕЛИ ДЛЯ РАЗУМПЛЕКТАЦИИ ---
class DisassemblyTemplatedPayload(BaseModel):
    unique_serial_number: str = Field(..., description="Серийный номер разбираемого набора")

# ИСПРАВЛЕНО: Добавлена пропущенная Pydantic-модель для частичного разбора (устраняет NameError!)
class DisassemblyPartialPayload(BaseModel):
    unique_serial_number: str = Field(..., description="Серийный номер вскрываемого набора")
    child_product_id: int = Field(..., description="ID детали, которую забирают из набора")

# --- РОУТЕРЫ УПРАВЛЕНИЯ ПОСТАВЩИКАМИ ---
@router.post("/suppliers", status_code=201)
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Supplier).where(Supplier.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Поставщик с таким именем уже существует")

    new_sup = Supplier(name=payload.name, contact_info=payload.contact_info)
    db.add(new_sup)
    await db.commit()
    return {"status": "success", "supplier_id": new_sup.id}

@router.get("/suppliers", response_model=List[dict])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier))
    return [{"id": s.id, "name": s.name, "contact_info": s.contact_info} for s in result.scalars().all()]
# services/core/src/routers/warehouse.py (ЧАСТЬ 2 из 3)

@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=SupplierOrderResponse)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    supplier = await db.get(Supplier, payload.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Поставщик с ID {payload.supplier_id} не найден")

    total_financial_load = Decimal("0.00")
    response_items = []

    for item in payload.items:
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")

        subtotal = item.estimated_purchase_price * item.quantity
        total_financial_load += subtotal

        # Поштучное FIFO-зарождение единиц товара
        for _ in range(item.quantity):
            unique_sn = f"SUP-{payload.supplier_id}-{uuid.uuid4().hex[:8].upper()}"
            new_unit = ProductUnit(
                product_id=item.product_id,
                supplier_id=payload.supplier_id,
                unique_serial_number=unique_sn,
                purchase_price=item.estimated_purchase_price,
                logistics_status=LogisticsStatus.IN_REQUEST,
                physical_status=PhysicalStatus.EXPECTED, 
                is_reserved=False
            )
            db.add(new_unit)

        response_items.append(
            OrderResponseItem(
                product_id=product.id,
                product_name=product.name,
                code=product.code,
                quantity=item.quantity,
                estimated_price=item.estimated_purchase_price,
                subtotal=subtotal
            )
        )

    await db.commit()
    
    return SupplierOrderResponse(
        supplier_id=supplier.id,
        supplier_name=supplier.name,
        total_financial_load=total_financial_load,
        items=response_items
    )

# =========================================================================
# 🛑 КОМАНДА 0101: ФАКТИЧЕСКАЯ ПРИЕМКА НА СКЛАД С АВТОГЕНЕРАЦИЕЙ СЕРИЙНИКОВ
# =========================================================================
@router.post("/receipts", status_code=200)
async def process_supplier_invoice_receipt(payload: SupplierInvoiceReceipt, db: AsyncSession = Depends(get_db)):
    """
    Принимает накладную поставщика, автоматически генерирует УНИКАЛЬНЫЕ 
    серийные номера для каждой единицы товара и выставляет их на полку IN_STORE.
    """
    supplier = await db.get(Supplier, payload.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Поставщик с ID {payload.supplier_id} не найден")

    accepted_count = 0
    
    for item in payload.items:
        # Проверяем, что номенклатурный шаблон (карточка) существует в системе
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Карточка товара с ID {item.product_id} не найдена")
            
        # Циклом генерируем столько изолированных уникальных юнитов, сколько приехало в накладной
        for _ in range(item.quantity):
            # Генерируем абсолютно уникальный буквенно-цифровой серийный номер поштучного учета
            generated_sn = f"SN-REC-{uuid.uuid4().hex[:8].upper()}"
            
            new_unit = ProductUnit(
                product_id=item.product_id,
                supplier_id=payload.supplier_id,
                unique_serial_number=generated_sn,     # Жесткая автогенерация уникального номера!
                purchase_price=item.actual_purchase_price,
                logistics_status=LogisticsStatus.RECEIVED,
                physical_status=PhysicalStatus.IN_STORE, # Товар мгновенно материализуется на полке кассира!
                is_reserved=False
            )
            db.add(new_unit)
            accepted_count += 1

    # Намертво сохраняем автогенерированные серийные номера в PostgreSQL
    await db.commit()

    # АСИНХРОННОЕ МЕЖСЕРВИСНОЕ ЛОГИРОВАНИЕ (Код 0101)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": "0101", 
                    "level": "INFO", 
                    "message": f"Накладная принята. Выставлено на полку {accepted_count} единиц товара с автогенерацией уникальных номеров от поставщика {supplier.name}."
                },
                timeout=2.0
            )
        except Exception:
            pass 

    return {
        "status": "success", 
        "message": f"Успешно принято на склад, сгенерировано и выставлено на полки {accepted_count} шт. товара с уникальными серийными номерами",
        "supplier_name": supplier.name
    }
# services/core/src/routers/warehouse.py (ЧАСТЬ 3 из 3)

@router.post("/disassembly/templated", status_code=200)
async def process_templated_disassembly(payload: DisassemblyTemplatedPayload, db: AsyncSession = Depends(get_db)):
    """Разукомплектация целого набора на дочерние сателлиты по жесткому шаблону (Команда 0102)"""
    
    # 1. Ищем физический юнит набора по его серийному номеру
    stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == payload.unique_serial_number).with_for_update()
    result = await db.execute(stmt)
    parent_unit = result.scalar_one_or_none()
    
    if not parent_unit:
        raise HTTPException(status_code=404, detail=f"Набор с серийным номером {payload.unique_serial_number} не найден на складе")
        
    if parent_unit.physical_status != PhysicalStatus.IN_STORE:
        raise HTTPException(status_code=400, detail=f"Набор имеет статус {parent_unit.physical_status}. Разобрать можно только товар в статусе IN_STORE.")

    # 2. Ищем жесткий шаблон разбора для этой карточки товара
    template_stmt = select(ProductAssemblyTemplate).where(ProductAssemblyTemplate.parent_product_id == parent_unit.product_id)
    template_res = await db.execute(template_stmt)
    templates = template_res.scalars().all()
    
    if not templates:
        raise HTTPException(status_code=400, detail="Для данной карточки товара не зарегистрирован шаблон разукомплектации")

    # 3. МЕНЯЕМ СТАТУС НАБОРА НА ВАШ НАТИВНЫЙ СТАТУС РАСФОРМИРОВАНИЯ
    parent_unit.physical_status = PhysicalStatus.IN_DISASSEMBLED

    generated_satellites_count = 0
    
    # 4. ЦИКЛОМ ГЕНЕРИРУЕМ САТЕЛЛИТЫ ПО ШАБЛОНУ
    for t in templates:
        for _ in range(t.quantity):
            # Генерируем уникальный серийный номер для каждого сателлита
            satellite_sn = f"SN-SAT-{uuid.uuid4().hex[:8].upper()}"
            
            new_satellite = ProductUnit(
                product_id=t.child_product_id,
                supplier_id=parent_unit.supplier_id,
                unique_serial_number=satellite_sn,
                purchase_price=Decimal("0.00"), # Цена закупки сателлита высчитывается аналитикой
                logistics_status=LogisticsStatus.RECEIVED,
                physical_status=PhysicalStatus.IN_STORE, # Сателлиты мгновенно падают на полку!
                is_reserved=False,
                parent_unit_id=parent_unit.id # ЖЕСТКАЯ РЕКУРСИВНАЯ ПРИВЯЗКА К НАБОРУ!
            )
            db.add(new_satellite)
            generated_satellites_count += 1
            
    # Намертво фиксируем транзакцию разбора в PostgreSQL (никаких флушей!)
    await db.commit()

    # 5. ОТПРАВЛЯЕМ МЕЖСЕРВИСНЫЙ ЛОГ ТАЙМЛАЙНА (Команда 0102)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": "0102", # Код операции разукомплектации наборов
                    "level": "INFO", 
                    "message": f"Проведена разукомплектация набора {parent_unit.unique_serial_number}. Набор списан. На полку выставлено {generated_satellites_count} сателлитов."
                }, 
                timeout=1.0
            )
        except Exception:
            pass

    return {
        "status": "success",
        "message": f"Набор успешно расформирован. Сгенерировано и выставлено на полки {generated_satellites_count} сателлитов.",
        "parent_unit_status": parent_unit.physical_status
    }

@router.post("/disassembly/partial", status_code=200)
async def process_partial_disassembly(payload: DisassemblyPartialPayload, db: AsyncSession = Depends(get_db)):
    """Частичный дербан набора без шаблона с заморозкой недокомплекта (Команда 0103)"""
    
    # 1. Ищем физический юнит набора
    stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == payload.unique_serial_number).with_for_update()
    result = await db.execute(stmt)
    parent_unit = result.scalar_one_or_none()
    
    if not parent_unit:
        raise HTTPException(status_code=404, detail=f"Набор с серийником {payload.unique_serial_number} не найден")
        
    if parent_unit.physical_status != PhysicalStatus.IN_STORE:
        raise HTTPException(status_code=400, detail=f"Набор имеет статус {parent_unit.physical_status}. Вскрыть можно только полный набор.")

    # 2. ИСПРАВЛЕНО: Переводим в LOST (Существующий статус для блокировки некомплекта!)
    parent_unit.physical_status = PhysicalStatus.LOST
    
    # 3. ГЕНЕРИРУЕМ И СРАЗУ СПИСЫВАЕМ ИЗВЛЕЧЕННЫЙ ЮНИТ-САТЕЛЛИТ
    sold_satellite_sn = f"SN-DERBAN-{uuid.uuid4().hex[:8].upper()}"
    
    sold_unit = ProductUnit(
        product_id=payload.child_product_id,
        supplier_id=parent_unit.supplier_id,
        unique_serial_number=sold_satellite_sn,
        purchase_price=Decimal("0.00"),
        logistics_status=LogisticsStatus.RECEIVED,
        physical_status=PhysicalStatus.SOLD, # Сразу уходит клиенту
        is_reserved=False,
        parent_unit_id=parent_unit.id       
    )
    db.add(sold_unit)

    await db.commit()

    # 4. ЛОГИРУЕМ ОПЕРАЦИЮ В ТАЙМЛАЙН (Команда 0103)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": "0103", 
                    "level": "WARNING", 
                    "message": f"ВНИМАНИЕ: Произведен частичный некомплектный разбор набора {parent_unit.unique_serial_number}. Извлечена деталь {sold_satellite_sn}. Набор заблокирован в статусе LOST."
                }, 
                timeout=1.0
            )
        except Exception:
            pass

    return {
        "status": "success",
        "message": "Частичный разбор зафиксирован. Извлеченная деталь списана, набор заморожен.",
        "parent_unit_status": parent_unit.physical_status,
        "extracted_unit_serial": sold_satellite_sn
    }
