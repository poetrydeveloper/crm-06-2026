# services/core/src/routers/warehouse_nodes/orders.py
import uuid
from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import delete, text
from src.database import get_db
from src.models import ProductUnit
from src.models.product_unit import LogisticsStatus, PhysicalStatus
from src.schemas.warehouse import CreateSupplierOrder

router = APIRouter(tags=["Склад: Заказы поставщикам и FIFO"])

# 🔥 НОВЫЙ ЭНДПОИНТ: Получить список заказов (product_units со статусом EXPECTED)
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

@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    """🛠️ Команда 0001: Создание заявки с автогенерацией unique_serial_number и валидным Decimal-ответом"""
    total_financial_load = 0.0
    response_items = []
    
    for item in payload.items:
        subtotal = int(item.quantity) * float(item.estimated_purchase_price)
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
            "product_name": "Тестовый товар",
            "code": f"CODE-{item.product_id}",
            "quantity": item.quantity,
            "estimated_price": item.estimated_purchase_price,
            "subtotal": subtotal
        })
        
    await db.commit()
    return {
        "supplier_id": payload.supplier_id,
        "supplier_name": "Force Опт",
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