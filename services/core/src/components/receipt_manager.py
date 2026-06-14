# services/core/src/components/receipt_manager.py
import uuid
import httpx
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product, Supplier, ProductUnit, LogisticsStatus, PhysicalStatus

async def send_receipt_log(supplier_name: str, accepted_count: int):
    """Асинхронное межсервисное логирование (Код 0101)"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": "0101", 
                    "level": "INFO", 
                    "message": f"Накладная принята. Выставлено на полку {accepted_count} единиц товара с автогенерацией уникальных номеров от поставщика {supplier_name}."
                },
                timeout=2.0
            )
        except Exception:
            pass 

class ReceiptManager:
    @staticmethod
    async def process_receipt(supplier_id: int, items: List, db: AsyncSession) -> dict:
        supplier = await db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail=f"Поставщик с ID {supplier_id} не найден")

        accepted_count = 0
        
        for item in items:
            product = await db.get(Product, item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Карточка товара с ID {item.product_id} не найдена")
                
            for _ in range(item.quantity):
                generated_sn = f"SN-REC-{uuid.uuid4().hex[:8].upper()}"
                new_unit = ProductUnit(
                    product_id=item.product_id,
                    supplier_id=supplier_id,
                    unique_serial_number=generated_sn,
                    purchase_price=item.actual_purchase_price,
                    logistics_status=LogisticsStatus.RECEIVED,
                    physical_status=PhysicalStatus.IN_STORE,
                    is_reserved=False
                )
                db.add(new_unit)
                accepted_count += 1

        await db.commit()
        await send_receipt_log(supplier.name, accepted_count)
        
        return {
            "status": "success", 
            "message": f"Успешно принято на склад, сгенерировано и выставлено на полки {accepted_count} шт. товара",
            "supplier_name": supplier.name
        }
