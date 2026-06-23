# services/core/src/routers/cash.py
from fastapi import APIRouter, Depends, HTTPException, Body, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from pydantic import BaseModel
from src.database import get_db
from src.models import CashDay, CashEvent, CashEventItem, CashEventType, ProductUnit, Product
from src.components.cash_day_manager import CashDayManager
from src.components.sales_manager import SalesManager
from src.components.return_manager import ReturnManager
from src.components.cash_adjustments import get_sold_units, adjust_sale

router = APIRouter(prefix="/cash", tags=["Кассовый узел и Продажи"])


@router.get("/days/current/sales", status_code=200)
async def current_sales(db: AsyncSession = Depends(get_db)):
    """📋 Все продажи и возвраты текущей смены"""
    day_stmt = select(CashDay).where(CashDay.is_closed == False)
    day_res = await db.execute(day_stmt)
    active_day = day_res.scalar_one_or_none()
    if not active_day:
        return {"sales": [], "message": "Нет открытой смены"}

    events = (await db.execute(
        select(CashEvent).where(
            CashEvent.cash_day_id == active_day.id,
            CashEvent.type.in_([CashEventType.SALE, CashEventType.RETURN])
        ).order_by(CashEvent.created_at.desc())
    )).scalars().all()

    sales = []
    for event in events:
        items = (await db.execute(
            select(CashEventItem).where(CashEventItem.cash_event_id == event.id)
        )).scalars().all()
        for item in items:
            unit = await db.get(ProductUnit, item.product_unit_id)
            product = await db.get(Product, unit.product_id) if unit else None
            sales.append({
                "time": event.created_at.isoformat(),
                "product_name": product.name if product else "Товар",
                "price": float(event.total_amount),
                "serial_number": unit.unique_serial_number if unit else "—",
                "event_id": event.id,
                "type": event.type.value,
                "description": event.description or "",
            })
    return {"sales": sales, "total": len(sales)}


@router.get("/days/current/units", status_code=200)
async def sold_units(days: int = Query(5, ge=1, le=365), db: AsyncSession = Depends(get_db)):
    return await get_sold_units(days, db)


@router.get("/days", status_code=200)
async def list_cash_days(db: AsyncSession = Depends(get_db)):
    result = await db.execute(select(CashDay).order_by(CashDay.created_at.desc()).limit(100))
    days = result.scalars().all()
    return {
        "days": [{"id": d.id, "created_at": str(d.created_at), "status": "ЗАКРЫТА" if d.is_closed else "ОТКРЫТА", "total_sales": float(d.total_revenue)} for d in days],
        "total": len(days)
    }


class CashReturnPayload(BaseModel):
    unique_serial_number: str
    return_reason: str = "Возврат от покупателя"


@router.post("/days/open", status_code=201)
async def open_day(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    return await CashDayManager.open_day(payload, db)


@router.post("/sales", status_code=201)
async def process_sale(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=422, detail="product_id обязателен")
    return await SalesManager.execute_fifo_sale(int(product_id), payload, db)


@router.post("/sales/adjust", status_code=200)
async def adjust(payload: dict, db: AsyncSession = Depends(get_db)):
    return await adjust_sale(payload, db)


@router.post("/days/{cash_day_id}/reopen", status_code=200)
async def reopen_day(cash_day_id: int, db: AsyncSession = Depends(get_db)):
    return await CashDayManager.reopen_day(cash_day_id, db)


@router.post("/days/close", status_code=200)
async def close_day(db: AsyncSession = Depends(get_db)):
    return await CashDayManager.close_day(db)


@router.get("/returns/check-relation", status_code=200)
async def check_return(sn: str = Query(...), db: AsyncSession = Depends(get_db)):
    return await ReturnManager.check_unit_relation(sn, db)


@router.post("/returns", status_code=200)
async def process_return(payload: CashReturnPayload, db: AsyncSession = Depends(get_db)):
    day = (await db.execute(select(CashDay).where(CashDay.is_closed == False))).scalar_one_or_none()
    if not day:
        raise HTTPException(status_code=400, detail="Смена не открыта")
    return await ReturnManager.execute_return(payload.unique_serial_number, payload.return_reason, day.id, db)