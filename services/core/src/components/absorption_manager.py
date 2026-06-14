# services/core/src/components/absorption_manager.py
import uuid
import httpx
from decimal import Decimal
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.models import Product, ProductUnit, LogisticsStatus, PhysicalStatus

async def send_absorption_log(parent_name: str, parent_sn: str, satellites_count: int):
    """Асинхронное межсервисное логирование операции поглощения (Код 0302)"""
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
                timeout=1.0
            )
        except Exception:
            pass

class AbsorptionManager:
    @staticmethod
    async def execute_set_absorption(parent_product_id: int, satellite_unit_ids: List[int], db: AsyncSession) -> dict:
        """Комлектация набора из одиночных сателлитов (Код 0302)"""
        parent_product = await db.get(Product, parent_product_id)
        if not parent_product:
            raise HTTPException(status_code=404, detail=f"Карточка набора с ID {parent_product_id} не найдена")

        if not satellite_unit_ids:
            raise HTTPException(status_code=400, detail="Список сателлитов для сборки не может быть пустым")

        # Извлекаем и валидируем все сателлиты из базы данных с блокировкой строки
        result = await db.execute(
            select(ProductUnit).where(ProductUnit.id.in_(satellite_unit_ids)).with_for_update()
        )
        satellites = result.scalars().all()

        if len(satellites) != len(satellite_unit_ids):
            raise HTTPException(status_code=404, detail="Один или несколько указанных сателлитов не найдены в СУБД")

        total_purchase_price = Decimal("0.00")
        base_supplier_id = None

        for sat in satellites:
            if sat.physical_status != PhysicalStatus.IN_STORE:
                raise HTTPException(
                    status_code=400, 
                    detail=f"Сателлит ID {sat.id} ({sat.unique_serial_number}) недоступен для сборки. Статус: {sat.physical_status}"
                )
            total_purchase_price += (sat.purchase_price or Decimal("0.00"))
            if sat.supplier_id:
                base_supplier_id = sat.supplier_id

        # Генерируем новый родительский юнит целого набора инструментов с простановкой таймстампа
        generated_parent_sn = f"SN-SET-{uuid.uuid4().hex[:8].upper()}"
        parent_unit = ProductUnit(
            product_id=parent_product_id,
            supplier_id=base_supplier_id,
            unique_serial_number=generated_parent_sn,
            purchase_price=total_purchase_price,
            logistics_status=LogisticsStatus.RECEIVED,
            physical_status=PhysicalStatus.IN_STORE,
            is_reserved=False,
            created_at=func.now(),  # Жесткий обход NOT NULL ограничений СУБД
            updated_at=func.now()
        )
        db.add(parent_unit)
        await db.flush()  # Получаем parent_unit.id до окончательного коммита

        # Переводим сателлиты в состояние ABSORBED и привязываем parent_unit_id
        for sat in satellites:
            sat.physical_status = PhysicalStatus.ABSORBED
            sat.is_reserved = True  # Защита от независимой розничной продажи на кассе
            sat.parent_unit_id = parent_unit.id
            sat.updated_at = func.now()

        await db.commit()
        await send_absorption_log(parent_product.name, generated_parent_sn, len(satellites))

        return {
            "status": "success",
            "message": "Комплектация набора успешно произведена",
            "parent_unit_id": parent_unit.id,
            "parent_serial_number": generated_parent_sn
        }
