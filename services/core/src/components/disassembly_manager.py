# services/core/src/components/disassembly_manager.py
import uuid
import httpx
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import ProductUnit, ProductAssemblyTemplate, PhysicalStatus, LogisticsStatus

async def send_disassembly_log(operation_code: str, level: str, message: str):
    """Асинхронное межсервисное логирование (Коды 0102, 0103)"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={
                    "service": "core", 
                    "operation_code": operation_code, 
                    "level": level, 
                    "message": message
                }, 
                timeout=1.0
            )
        except Exception:
            pass

class DisassemblyManager:
    @staticmethod
    async def execute_templated_disassembly(unique_serial_number: str, db: AsyncSession) -> dict:
        """Разукомплектация целого набора по жесткому шаблону (Команда 0102)"""
        stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == unique_serial_number).with_for_update()
        result = await db.execute(stmt)
        parent_unit = result.scalar_one_or_none()
        
        if not parent_unit:
            raise HTTPException(status_code=404, detail=f"Набор с серийным номером {unique_serial_number} не найден на складе")
            
        if parent_unit.physical_status != PhysicalStatus.IN_STORE:
            raise HTTPException(status_code=400, detail=f"Набор имеет статус {parent_unit.physical_status}. Разобрать можно только товар в статусе IN_STORE.")

        template_stmt = select(ProductAssemblyTemplate).where(ProductAssemblyTemplate.parent_product_id == parent_unit.product_id)
        template_res = await db.execute(template_stmt)
        templates = template_res.scalars().all()
        
        if not templates:
            raise HTTPException(status_code=400, detail="Для данной карточки товара не зарегистрирован шаблон разукомплектации")

        # Переводим статус родительского набора в заблокированный/расформированный
        parent_unit.physical_status = PhysicalStatus.IN_DISASSEMBLED
        generated_satellites_count = 0
        
        for t in templates:
            for _ in range(t.quantity):
                satellite_sn = f"SN-SAT-{uuid.uuid4().hex[:8].upper()}"
                new_satellite = ProductUnit(
                    product_id=t.child_product_id,
                    supplier_id=parent_unit.supplier_id,
                    unique_serial_number=satellite_sn,
                    purchase_price=Decimal("0.00"),
                    logistics_status=LogisticsStatus.RECEIVED,
                    physical_status=PhysicalStatus.IN_STORE,
                    is_reserved=False,
                    parent_unit_id=parent_unit.id
                )
                db.add(new_satellite)
                generated_satellites_count += 1

        await db.commit()
        await send_disassembly_log(
            "0102", "INFO", 
            f"Проведена разукомплектация набора {parent_unit.unique_serial_number}. Набор списан. На полку выставлено {generated_satellites_count} сателлитов."
        )
        return {
            "status": "success",
            "message": f"Набор успешно расформирован. Сгенерировано и выставлено на полки {generated_satellites_count} сателлитов.",
            "parent_unit_status": parent_unit.physical_status
        }

    @staticmethod
    async def execute_partial_disassembly(unique_serial_number: str, child_product_id: int, db: AsyncSession) -> dict:
        """Частичный дербан набора без шаблона с заморозкой недокомплекта (Команда 0103)"""
        stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == unique_serial_number).with_for_update()
        result = await db.execute(stmt)
        parent_unit = result.scalar_one_or_none()
        
        if not parent_unit:
            raise HTTPException(status_code=404, detail=f"Набор с серийником {unique_serial_number} не найден")
            
        if parent_unit.physical_status != PhysicalStatus.IN_STORE:
            raise HTTPException(status_code=400, detail=f"Набор имеет статус {parent_unit.physical_status}. Вскрыть можно только полный набор.")

        # Блокируем некомплект в СУБД (переводим в LOST по бизнес-логике)
        parent_unit.physical_status = PhysicalStatus.LOST
        
        sold_satellite_sn = f"SN-DERBAN-{uuid.uuid4().hex[:8].upper()}"
        sold_unit = ProductUnit(
            product_id=child_product_id,
            supplier_id=parent_unit.supplier_id,
            unique_serial_number=sold_satellite_sn,
            purchase_price=Decimal("0.00"),
            logistics_status=LogisticsStatus.RECEIVED,
            physical_status=PhysicalStatus.SOLD, # Сразу списывается в чек
            is_reserved=False,
            parent_unit_id=parent_unit.id       
        )
        db.add(sold_unit)
        await db.commit()

        await send_disassembly_log(
            "0103", "WARNING", 
            f"ВНИМАНИЕ: Произведен частичный некомплектный разбор набора {parent_unit.unique_serial_number}. Извлечена деталь {sold_satellite_sn}. Набор заблокирован в статусе LOST."
        )
        return {
            "status": "success",
            "message": "Частичный разбор зафиксирован. Извлеченная деталь списана, набор заморожен.",
            "parent_unit_status": parent_unit.physical_status,
            "extracted_unit_serial": sold_satellite_sn
        }
