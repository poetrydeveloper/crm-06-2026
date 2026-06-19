# services/core/src/routers/warehouse_nodes/orders.py
import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text
from src.database import get_db
from src.models import Product, Supplier, ProductUnit
from src.models.product_unit import LogisticsStatus, PhysicalStatus
from src.schemas.warehouse import CreateSupplierOrder

router = APIRouter(tags=["Склад: Заказы поставщикам и FIFO"])

@router.get("/orders", status_code=200)
async def list_supplier_orders(db: AsyncSession = Depends(get_db)):
    """📋 Получить список заказов поставщикам (EXPECTED)"""
    result = await db.execute(
        text("""
            SELECT 
                supplier_id,
                DATE(created_at) as order_date,
                COUNT(*) as total_units,
                SUM(purchase_price) as total_amount
            FROM product_units 
            WHERE physical_status = 'EXPECTED'
            GROUP BY supplier_id, DATE(created_at)
            ORDER BY order_date DESC 
            LIMIT 100
        """)
    )
    orders = [
        {
            "supplier_id": row[0],
            "order_date": str(row[1]),
            "total_units": row[2],
            "total_amount": float(row[3]) if row[3] else 0
        }
        for row in result
    ]
    return {"orders": orders, "total": len(orders)}


@router.get("/orders/{supplier_id}/items", status_code=200)
async def get_order_items(supplier_id: int, db: AsyncSession = Depends(get_db)):
    """📋 Получить состав заявки — все EXPECTED юниты поставщика"""
    result = await db.execute(
        select(ProductUnit)
        .where(
            ProductUnit.supplier_id == supplier_id,
            ProductUnit.physical_status == PhysicalStatus.EXPECTED
        )
        .order_by(ProductUnit.created_at.desc())
    )
    units = result.scalars().all()

    items = []
    for unit in units:
        product = await db.get(Product, unit.product_id)
        items.append({
            "unit_id": unit.id,
            "product_id": unit.product_id,
            "product_name": product.name.replace("_", " ") if product else f"Товар #{unit.product_id}",
            "product_code": product.code if product else "—",
            "unique_serial_number": unit.unique_serial_number,
            "purchase_price": float(unit.purchase_price) if unit.purchase_price else 0.0,
            "physical_status": unit.physical_status.value if unit.physical_status else "EXPECTED",
        })

    return {"supplier_id": supplier_id, "items": items, "total": len(items)}


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    """🛠️ Команда 0001: Создание заявки с автогенерацией unique_serial_number"""
    supplier = await db.get(Supplier, payload.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Поставщик с ID {payload.supplier_id} не найден")

    total_financial_load = 0.0
    response_items = []

    for item in payload.items:
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")

        subtotal = float(item.quantity) * float(item.estimated_purchase_price)
        total_financial_load += subtotal

        for _ in range(item.quantity):
            generated_sn = f"SN-ORD-{uuid.uuid4().hex[:8].upper()}"
            unit = ProductUnit(
                product_id=item.product_id,
                supplier_id=payload.supplier_id,
                unique_serial_number=generated_sn,
                purchase_price=item.estimated_purchase_price,
                logistics_status=LogisticsStatus.IN_REQUEST,
                physical_status=PhysicalStatus.EXPECTED,
                is_reserved=False
            )
            db.add(unit)

        response_items.append({
            "product_id": item.product_id,
            "product_name": product.name,
            "code": product.code,
            "quantity": item.quantity,
            "estimated_price": float(item.estimated_purchase_price),
            "subtotal": subtotal
        })

    await db.commit()
    return {
        "supplier_id": payload.supplier_id,
        "supplier_name": supplier.name,
        "total_financial_load": total_financial_load,
        "items": response_items
    }


@router.delete("/units/debug-clear", status_code=200)
async def debug_clear_units(product_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ProductUnit).where(ProductUnit.product_id == product_id))
    await db.commit()
    return {"status": "cleared"}


@router.delete("/orders/debug-clear", status_code=200)
async def debug_clear_orders(product_id: int, db: AsyncSession = Depends(get_db)):
    return {"status": "cleared"}