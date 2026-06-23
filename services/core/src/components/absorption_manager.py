# services/core/src/components/absorption_manager.py
import httpx
from decimal import Decimal
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Product, ProductUnit, LogisticsStatus, PhysicalStatus


async def send_absorption_log(parent_name: str, parent_sn: str, satellites_count: int):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log",
                json={
                    "service": "core",
                    "operation_code": "0302",
                    "level": "INFO",
                    "message": f"Комплектация набора {parent_name} (SN: {parent_sn}) завершена. Поглощено деталей: {satellites_count} шт. Сателлиты переведены в ABSORBED."
                },
                timeout=1.0,
            )
        except Exception:
            pass


class AbsorptionManager:
    @staticmethod
    async def execute_set_absorption(parent_product_id: int, satellite_unit_ids: List[int], db: AsyncSession) -> dict:
        """Комплектация набора из одиночных сателлитов (Код 0302)"""
        parent_product = await db.get(Product, parent_product_id)
        if not parent_product:
            raise HTTPException(status_code=404, detail=f"Карточка набора с ID {parent_product_id} не найдена")

        if not satellite_unit_ids:
            raise HTTPException(status_code=400, detail="Список сателлитов для сборки не может быть пустым")

        # Извлекаем и валидируем все сателлиты
        result = await db.execute(
            select(ProductUnit).where(ProductUnit.id.in_(satellite_unit_ids)).with_for_update()
        )
        satellites = result.scalars().all()

        if len(satellites) != len(satellite_unit_ids):
            raise HTTPException(status_code=404, detail="Один или несколько сателлитов не найдены")

        for sat in satellites:
            if sat.physical_status != PhysicalStatus.IN_STORE:
                raise HTTPException(
                    status_code=400,
                    detail=f"Сателлит ID {sat.id} ({sat.unique_serial_number}) недоступен для сборки. Статус: {sat.physical_status}"
                )

        # Ищем существующий разобранный набор этого товара
        parent_unit = (await db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == parent_product_id,
                ProductUnit.physical_status == PhysicalStatus.IN_DISASSEMBLED
            ).with_for_update()
        )).scalar_one_or_none()

        if parent_unit:
            # Восстанавливаем разобранный набор
            parent_unit.physical_status = PhysicalStatus.IN_STORE
            parent_sn = parent_unit.unique_serial_number
        else:
            # Создаём новый набор если нет разобранного
            import uuid
            generated_sn = f"SN-SET-{uuid.uuid4().hex[:8].upper()}"
            total_purchase_price = sum((sat.purchase_price or Decimal("0.00")) for sat in satellites)
            base_supplier_id = next((sat.supplier_id for sat in satellites if sat.supplier_id), None)

            parent_unit = ProductUnit(
                product_id=parent_product_id,
                supplier_id=base_supplier_id,
                unique_serial_number=generated_sn,
                purchase_price=total_purchase_price,
                logistics_status=LogisticsStatus.RECEIVED,
                physical_status=PhysicalStatus.IN_STORE,
                is_reserved=False,
            )
            db.add(parent_unit)
            await db.flush()
            parent_sn = generated_sn

        # Переводим сателлиты в ABSORBED и привязываем к набору
        for sat in satellites:
            sat.physical_status = PhysicalStatus.ABSORBED
            sat.is_reserved = True
            sat.parent_unit_id = parent_unit.id

        await db.commit()
        await send_absorption_log(parent_product.name, parent_sn, len(satellites))

        return {
            "status": "success",
            "message": "Комплектация набора успешно произведена",
            "parent_unit_id": parent_unit.id,
            "parent_serial_number": parent_sn,
        }