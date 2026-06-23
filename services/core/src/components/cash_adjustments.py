# services/core/src/components/cash_adjustments.py
import httpx
from datetime import datetime, timedelta
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import CashDay, CashEvent, CashEventItem, CashEventType, ProductUnit, Product, PhysicalStatus


async def get_sold_units(days: int, db: AsyncSession) -> dict:
    since_date = datetime.utcnow() - timedelta(days=days)

    items_stmt = (
        select(CashEventItem, CashEvent, ProductUnit, Product)
        .join(CashEvent, CashEventItem.cash_event_id == CashEvent.id)
        .join(ProductUnit, CashEventItem.product_unit_id == ProductUnit.id)
        .join(Product, ProductUnit.product_id == Product.id)
        .where(
            CashEvent.type == CashEventType.SALE,
            CashEvent.created_at >= since_date
        )
        .order_by(CashEvent.created_at.desc())
    )
    result = await db.execute(items_stmt)
    rows = result.all()

    units = []
    seen = set()
    for item, event, unit, product in rows:
        if unit.id in seen:
            continue
        seen.add(unit.id)
        actual_price = float(unit.sold_price) if unit.sold_price else float(unit.purchase_price or 0)
        units.append({
            "unit_id": unit.id,
            "unique_serial_number": unit.unique_serial_number,
            "product_name": product.name if product else "Товар",
            "product_code": product.code if product else "—",
            "sold_price": actual_price,
            "sold_at": event.created_at.isoformat(),
            "event_id": event.id,
        })

    return {"units": units, "total": len(units)}


async def adjust_sale(payload: dict, db: AsyncSession) -> dict:
    unit_id = payload.get("unit_id")
    action = payload.get("action")
    new_price = payload.get("new_price")

    if not unit_id or not action:
        raise HTTPException(status_code=422, detail="unit_id и action обязательны")

    unit = await db.get(ProductUnit, unit_id)
    if not unit:
        raise HTTPException(status_code=404, detail="Юнит не найден")

    if unit.physical_status != PhysicalStatus.SOLD:
        raise HTTPException(status_code=400, detail=f"Юнит не в статусе SOLD, а {unit.physical_status.value}")

    day_stmt = select(CashDay).where(CashDay.is_closed == False)
    day_res = await db.execute(day_stmt)
    active_day = day_res.scalar_one_or_none()
    if not active_day:
        raise HTTPException(status_code=400, detail="Нет открытой смены")

    actual_price = float(unit.sold_price) if unit.sold_price else float(unit.purchase_price or 0)

    if action == "return":
        unit.physical_status = PhysicalStatus.IN_STORE

        event = CashEvent(
            cash_day_id=active_day.id,
            customer_id=None,
            type=CashEventType.RETURN,
            total_amount=-actual_price,
            amount_cash=-actual_price,
            amount_card=0,
            amount_credit=0,
            description="Возврат товара",
        )
        db.add(event)
        await db.flush()

        db.add(CashEventItem(
            cash_event_id=event.id,
            product_unit_id=unit.id,
            price_per_unit=-actual_price,
            discount_amount=0,
        ))

        await log_operation("0501", f"Возврат юнита {unit.unique_serial_number} на сумму {actual_price}")
        await db.commit()

        return {"status": "success", "message": "Юнит возвращён на полку", "event_type": "RETURN", "amount": -actual_price}

    elif action == "change_price":
        diff = new_price - actual_price
        unit.sold_price = new_price

        event = CashEvent(
            cash_day_id=active_day.id,
            customer_id=None,
            type=CashEventType.SALE,
            total_amount=diff,
            amount_cash=diff,
            amount_card=0,
            amount_credit=0,
            description=f"Изменение цены с {actual_price} на {new_price}",
        )
        db.add(event)
        await db.flush()

        db.add(CashEventItem(
            cash_event_id=event.id,
            product_unit_id=unit.id,
            price_per_unit=diff,
            discount_amount=0,
        ))

        await log_operation("0201", f"Изменение цены юнита {unit.unique_serial_number}: {actual_price} -> {new_price}")
        await db.commit()

        return {"status": "success", "message": f"Цена изменена с {actual_price} на {new_price}", "event_type": "SALE", "amount": diff}

    raise HTTPException(status_code=400, detail="Неизвестное действие")


async def log_operation(code: str, message: str):
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log",
                json={"service": "core", "operation_code": code, "level": "INFO", "message": message},
                timeout=1.0,
            )
        except Exception:
            pass