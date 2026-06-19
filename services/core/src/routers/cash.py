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

router = APIRouter(prefix="/cash", tags=["Кассовый узел и Продажи"])


@router.get("/days/current/sales", status_code=200)
async def get_current_day_sales(db: AsyncSession = Depends(get_db)):
    """📋 Получить все продажи текущей открытой смены"""
    day_stmt = select(CashDay).where(CashDay.is_closed == False)
    day_res = await db.execute(day_stmt)
    active_day = day_res.scalar_one_or_none()

    if not active_day:
        return {"sales": [], "message": "Нет открытой смены"}

    events_stmt = (
        select(CashEvent)
        .where(
            CashEvent.cash_day_id == active_day.id,
            CashEvent.type == CashEventType.SALE
        )
        .order_by(CashEvent.created_at.desc())
    )
    events_res = await db.execute(events_stmt)
    events = events_res.scalars().all()

    sales = []
    for event in events:
        items_stmt = select(CashEventItem).where(CashEventItem.cash_event_id == event.id)
        items_res = await db.execute(items_stmt)
        items = items_res.scalars().all()

        for item in items:
            unit = await db.get(ProductUnit, item.product_unit_id)
            product = await db.get(Product, unit.product_id) if unit else None
            sales.append({
                "time": event.created_at.isoformat(),
                "product_name": product.name if product else "Товар",
                "price": float(item.price_per_unit),
                "serial_number": unit.unique_serial_number if unit else "—",
                "event_id": event.id
            })

    return {"sales": sales, "total": len(sales)}


@router.get("/days", status_code=200)
async def list_cash_days(db: AsyncSession = Depends(get_db)):
    """📋 Получить список всех кассовых дней (история смен)"""
    result = await db.execute(
        select(CashDay).order_by(CashDay.created_at.desc()).limit(100)
    )
    days = result.scalars().all()
    return {
        "days": [
            {
                "id": day.id,
                "created_at": str(day.created_at),
                "status": "ЗАКРЫТА" if day.is_closed else "ОТКРЫТА",
                "total_sales": day.total_revenue
            }
            for day in days
        ],
        "total": len(days)
    }


class CashReturnPayload(BaseModel):
    unique_serial_number: str
    return_reason: str = "Возврат от покупателя"


@router.post("/days/open", status_code=201)
async def open_cash_day(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    return await CashDayManager.open_day(payload, db)


@router.post("/sales", status_code=201)
async def process_cash_sale(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=422, detail="product_id обязателен")
    return await SalesManager.execute_fifo_sale(int(product_id), payload, db)


@router.post("/days/{cash_day_id}/reopen", status_code=200)
async def reopen_cash_day(cash_day_id: int, db: AsyncSession = Depends(get_db)):
    return await CashDayManager.reopen_day(cash_day_id, db)


@router.post("/days/close", status_code=200)
async def close_cash_day_api(db: AsyncSession = Depends(get_db)):
    return await CashDayManager.close_day(db)


@router.get("/returns/check-relation", status_code=200)
async def check_return_item_relation(
    sn: str = Query(..., description="Серийный номер детали"),
    db: AsyncSession = Depends(get_db)
):
    return await ReturnManager.check_unit_relation(sn, db)


@router.post("/returns", status_code=200)
async def process_cash_return(payload: CashReturnPayload, db: AsyncSession = Depends(get_db)):
    day_stmt = select(CashDay).where(CashDay.is_closed == False)
    day_res = await db.execute(day_stmt)
    active_day = day_res.scalar_one_or_none()
    if not active_day:
        raise HTTPException(status_code=400, detail="Кассовая смена не открыта. Возврат невозможен.")
    return await ReturnManager.execute_return(
        payload.unique_serial_number, payload.return_reason, active_day.id, db
    )