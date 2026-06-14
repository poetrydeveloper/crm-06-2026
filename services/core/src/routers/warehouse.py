# services/core/src/routers/warehouse.py
from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel, Field

from src.database import get_db
from src.models import Supplier
from src.schemas.warehouse import CreateSupplierOrder, SupplierOrderResponse

# 🔥 Чистые атомарные импорты из папки компонентов
from src.components.order_manager import OrderManager
from src.components.receipt_manager import ReceiptManager
from src.components.disassembly_manager import DisassemblyManager
from src.components.absorption_manager import AbsorptionManager

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

@router.post("/orders", status_code=status.HTTP_201_CREATED, response_model=SupplierOrderResponse)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    return await OrderManager.create_order(payload, db)

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
