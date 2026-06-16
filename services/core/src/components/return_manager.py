# services/core/src/components/return_manager.py
import httpx
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import ProductUnit, PhysicalStatus, CashDay, CashEvent, CashEventType

async def send_return_timeline_log(message: str):
    """Асинхронное логирование операции возврата (Команда 0501)"""
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={"service": "core", "operation_code": "0501", "level": "INFO", "message": message},
                timeout=1.0
            )
        except Exception:
            pass

class ReturnManager:
    @staticmethod
    async def check_unit_relation(serial_number: str, db: AsyncSession) -> dict:
        """🔍 Проверка: Был ли товар извлечен из набора, который сейчас в LOST"""
        stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == serial_number)
        res = await db.execute(stmt)
        unit = res.scalar_one_or_none()
        
        if not unit:
            return {"has_parent_relation": False, "message": "Товар с таким серийным номером не найден в системе"}
            
        if unit.parent_unit_id:
            parent_stmt = select(ProductUnit).where(ProductUnit.id == unit.parent_unit_id)
            parent_res = await db.execute(parent_stmt)
            parent = parent_res.scalar_one_or_none()
            
            if parent and parent.physical_status == PhysicalStatus.LOST:
                return {
                    "has_parent_relation": True,
                    "parent_unit_id": parent.id,
                    "parent_serial_number": parent.unique_serial_number,
                    "message": f"ВНИМАНИЕ: Эта деталь привязана к вскрытому некомплектному набору {parent.unique_serial_number}! Вы можете вернуть её, а затем собрать набор обратно."
                }
                
        return {"has_parent_relation": False, "message": "Товар является независимой розничной единицей"}

    @staticmethod
    async def execute_return(serial_number: str, return_reason: str, active_day_id: int, db: AsyncSession) -> dict:
        """🔄 Проведение транзакции возврата в СУБД с отрицательным чеком"""
        stmt = select(ProductUnit).where(ProductUnit.unique_serial_number == serial_number).with_for_update()
        result = await db.execute(stmt)
        unit = result.scalar_one_or_none()

        if not unit:
            raise HTTPException(status_code=404, detail=f"Товар с серийным номером {serial_number} не найден в системе")

        if unit.physical_status != PhysicalStatus.SOLD:
            raise HTTPException(status_code=400, detail=f"Товар имеет статус {unit.physical_status}. Возврат оформляется только для проданных товаров (SOLD).")

        # Возвращаем деталь на полку магазина
        unit.physical_status = PhysicalStatus.IN_STORE
        
        # Создаем запись о кассовом событии возврата с отрицательной выручкой
        return_event = CashEvent(
            cash_day_id=active_day_id,
            customer_id=None,
            type=CashEventType.SALE, 
            total_amount=-unit.purchase_price, 
            amount_cash=-unit.purchase_price,
            amount_card=Decimal("0.00"),
            amount_credit=Decimal("0.00")
        )
        db.add(return_event)
        await db.commit()

        # Лог в таймлайн
        log_msg = f"Оформлен возврат товара. Юнит {unit.unique_serial_number} вернулся на полку. Причина: {return_reason}"
        await send_return_timeline_log(log_msg)

        return {
            "status": "success",
            "message": f"Товар {unit.unique_serial_number} успешно принят обратно на баланс магазина",
            "current_physical_status": unit.physical_status
        }
