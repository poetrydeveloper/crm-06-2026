# services/core/src/components/sales_manager.py
import httpx
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import CashDay, CashEvent, CashEventItem, ProductUnit, PhysicalStatus, CashEventType

class SalesManager:
    @staticmethod
    async def execute_fifo_sale(product_id: int, payload: dict, db: AsyncSession) -> dict:
        day_stmt = select(CashDay).where(CashDay.is_closed == False)
        day_res = await db.execute(day_stmt)
        active_day = day_res.scalar_one_or_none()
        if not active_day:
            raise HTTPException(status_code=400, detail="Кассовая смена не открыта")

        stmt = (
            select(ProductUnit)
            .where(
                ProductUnit.product_id == product_id,
                ProductUnit.physical_status == PhysicalStatus.IN_STORE,
                ProductUnit.is_reserved == False
            )
            .order_by(ProductUnit.created_at.asc())
            .limit(1)
            .with_for_update()
        )
        result = await db.execute(stmt)
        oldest_unit = result.scalar_one_or_none()
        if not oldest_unit:
            raise HTTPException(status_code=404, detail="Нет доступных остатков данного товара на полках магазина")

        sale_price = Decimal(str(payload.get("sale_price", 0)))

        new_event = CashEvent(
            cash_day_id=active_day.id,
            customer_id=payload.get("customer_id"),
            type=CashEventType.SALE,
            total_amount=sale_price,
            amount_cash=Decimal(str(payload.get("amount_cash", 0))),
            amount_card=Decimal(str(payload.get("amount_card", 0))),
            amount_credit=Decimal(str(payload.get("amount_credit", 0)))
        )
        db.add(new_event)
        await db.flush()

        new_item = CashEventItem(
            cash_event_id=new_event.id,
            product_unit_id=oldest_unit.id,
            price_per_unit=sale_price,
            discount_amount=Decimal("0.00")
        )
        db.add(new_item)

        oldest_unit.sold_price = sale_price
        oldest_unit.physical_status = PhysicalStatus.SOLD
        await db.commit()

        try:
            async with httpx.AsyncClient() as client:
                await client.post("http://logger:8001/api/v1/log", json={
                    "service": "core", "operation_code": "0401", "level": "INFO",
                    "message": f"Продажа FIFO: {oldest_unit.unique_serial_number} за {sale_price}"
                }, timeout=1.0)
        except Exception:
            pass

        return {
            "status": "success",
            "message": "Чек продажи успешно пробит по FIFO",
            "saled_unit_serial": oldest_unit.unique_serial_number
        }