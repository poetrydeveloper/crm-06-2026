# services/core/src/routers/warehouse.py
import uuid
from typing import List, Optional
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from pydantic import BaseModel

from src.database import get_db
from src.models import Product, Supplier, ProductUnit, LogisticsStatus, PhysicalStatus
from src.schemas.warehouse import CreateSupplierOrder, SupplierOrderResponse, OrderResponseItem

router = APIRouter(prefix="/warehouse", tags=["Склад и Логистика Закупок"])

class SupplierCreate(BaseModel):
    name: str
    contact_info: Optional[str] = None

@router.post("/suppliers", status_code=201)
async def create_supplier(payload: SupplierCreate, db: AsyncSession = Depends(get_db)):
    existing = await db.execute(select(Supplier).where(Supplier.name == payload.name))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Поставщик с таким именем уже существует")

    new_sup = Supplier(name=payload.name, contact_info=payload.contact_info)
    db.add(new_sup)
    await db.flush()
    await db.commit()
    return {"status": "success", "supplier_id": new_sup.id}

@router.get("/suppliers", response_model=List[dict])
async def get_suppliers(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(Supplier))
    return [{"id": s.id, "name": s.name, "contact_info": s.contact_info} for s in result.scalars().all()]

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

    await db.flush()
    await db.commit() # ВНЕДРЕНО: Жесткая фиксация в БД, чтобы данные были видны роутеру удаления
    return SupplierOrderResponse(
        supplier_id=supplier.id,
        supplier_name=supplier.name,
        total_financial_load=total_financial_load,
        items=response_items
    )
