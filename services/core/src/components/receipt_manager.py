# services/core/src/components/receipt_manager.py
import httpx
from datetime import datetime
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Product, Supplier, ProductUnit, LogisticsStatus, PhysicalStatus


async def send_receipt_log(supplier_name: str, accepted_count: int):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log",
                json={
                    "service": "core",
                    "operation_code": "0101",
                    "level": "INFO",
                    "message": f"Накладная принята. Выставлено на полку {accepted_count} ед. товара от поставщика {supplier_name}.",
                },
                timeout=2.0,
            )
        except Exception:
            pass


class ReceiptManager:
    @staticmethod
    async def process_receipt_by_units(
        supplier_id: int, unit_ids: List[int], db: AsyncSession
    ) -> dict:
        """Приёмка товара по конкретным unit_id"""
        supplier = await db.get(Supplier, supplier_id)
        if not supplier:
            raise HTTPException(
                status_code=404, detail=f"Поставщик с ID {supplier_id} не найден"
            )

        if not unit_ids:
            raise HTTPException(status_code=400, detail="Список unit_ids пуст")

        # Находим все указанные юниты
        result = await db.execute(
            select(ProductUnit).where(ProductUnit.id.in_(unit_ids))
        )
        units = {u.id: u for u in result.scalars().all()}

        accepted_count = 0
        accepted_items = []
        errors = []
        now = datetime.now()

        for unit_id in unit_ids:
            unit = units.get(unit_id)
            if not unit:
                errors.append(f"Юнит #{unit_id} не найден")
                continue

            if unit.physical_status != PhysicalStatus.EXPECTED:
                errors.append(
                    f"Юнит #{unit_id} уже имеет статус {unit.physical_status.value}"
                )
                continue

            if unit.supplier_id != supplier_id:
                errors.append(f"Юнит #{unit_id} принадлежит другому поставщику")
                continue

            unit.physical_status = PhysicalStatus.IN_STORE
            unit.logistics_status = LogisticsStatus.RECEIVED
            unit.updated_at = now
            accepted_count += 1

            product = await db.get(Product, unit.product_id)
            accepted_items.append(
                {
                    "unit_id": unit.id,
                    "unique_serial_number": unit.unique_serial_number,
                    "product_name": product.name
                    if product
                    else f"Товар #{unit.product_id}",
                    "accepted_at": now.isoformat(),
                }
            )

        await db.commit()

        if accepted_count > 0:
            await send_receipt_log(supplier.name, accepted_count)

        return {
            "status": "success",
            "message": f"Принято: {accepted_count} шт."
            + (f" (ошибки: {len(errors)})" if errors else ""),
            "supplier_name": supplier.name,
            "accepted_count": accepted_count,
            "accepted_items": accepted_items,
            "errors": errors if errors else None,
        }
