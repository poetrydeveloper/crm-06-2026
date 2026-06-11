# services/core/src/routers/cash.py
import httpx
from datetime import datetime
from decimal import Decimal
from fastapi import APIRouter, Depends, HTTPException, status, Body
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.models import CashDay, CashEvent, CashEventItem, ProductUnit, PhysicalStatus, CashEventType

# ИСПРАВЛЕНО: Чистый префикс без дублирования сегментов
router = APIRouter(prefix="/cash", tags=["Кассовый узел и Продажи"])

@router.post("/days/open", status_code=201)
async def open_cash_day(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Открывает новую операционную кассовую смену (Команда 0401)"""
    existing = await db.execute(select(CashDay).where(CashDay.is_closed == False))
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="В системе уже есть открытая кассовая смена")

    # Безопасный парсинг даты без жесткой Pydantic-валидации
    date_str = payload.get("date")
    parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else datetime.utcnow()
    
    new_day = CashDay(date=parsed_date, is_closed=False, total_revenue=Decimal("0.00"))
    db.add(new_day)
    await db.commit()
    return {"status": "success", "cash_day_id": new_day.id, "message": "Кассовая смена успешно открыта"}

@router.post("/sales", status_code=201)
async def process_cash_sale(payload: dict = Body(...), db: AsyncSession = Depends(get_db)):
    """Розничная продажа товара с поштучным подбором по FIFO (Команда 0401)"""
    day_stmt = select(CashDay).where(CashDay.is_closed == False)
    day_res = await db.execute(day_stmt)
    active_day = day_res.scalar_one_or_none()
    if not active_day:
        raise HTTPException(status_code=400, detail="Кассовая смена не открыта")

    product_id = payload.get("product_id")
    if not product_id:
        raise HTTPException(status_code=422, detail="product_id обязателен")

    # АЛГОРИТМ ПОДБОРА СТАРАЙШЕЙ ДЕТАЛИ ПО ЗАКОНУ FIFO
    stmt = (
        select(ProductUnit)
        .where(
            ProductUnit.product_id == int(product_id),
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

    # ФИКСАЦИЯ ЧЕКА ПРОДАЖИ
    new_event = CashEvent(
        cash_day_id=active_day.id,
        customer_id=payload.get("customer_id"),
        type=CashEventType.SALE,
        total_amount=Decimal(str(payload.get("sale_price", 0))),
        amount_cash=Decimal(str(payload.get("amount_cash", 0))),
        amount_card=Decimal(str(payload.get("amount_card", 0))),
        amount_credit=Decimal(str(payload.get("amount_credit", 0)))
    )
    db.add(new_event)
    await db.commit()

    new_item = CashEventItem(
        cash_event_id=new_event.id,
        product_unit_id=oldest_unit.id,
        price_per_unit=Decimal(str(payload.get("sale_price", 0))),
        discount_amount=Decimal("0.00")
    )
    db.add(new_item)
    
    # Списываем юнит в статус SOLD
    oldest_unit.physical_status = PhysicalStatus.SOLD
    await db.commit()

    async with httpx.AsyncClient() as client:
        try:
            await client.post("http://logger:8001/api/v1/log", json={"service": "core", "operation_code": "0401", "level": "INFO", "message": "Продажа FIFO"}, timeout=1.0)
        except Exception:
            pass

    return {
        "status": "success", 
        "message": "Чек продажи успешно пробит по FIFO", 
        "saled_unit_serial": oldest_unit.unique_serial_number
    }

@router.post("/days/{cash_day_id}/reopen", status_code=200)
async def reopen_cash_day(cash_day_id: int, db: AsyncSession = Depends(get_db)):
    cash_day = await db.get(CashDay, cash_day_id)
    if not cash_day:
        raise HTTPException(status_code=404, detail=f"Кассовый день с ID {cash_day_id} не найден")
    active_day = await db.execute(select(CashDay).where(CashDay.is_closed == False, CashDay.id != cash_day_id))
    if active_day.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Нельзя переоткрыть этот день, пока в системе активна другая кассовая смена.")
    cash_day.is_closed = False
    await db.commit()
    return {"status": "success", "message": "Кассовый день успешно переоткрыт"}

@router.post("/days/close", status_code=200)
async def close_cash_day_api(db: AsyncSession = Depends(get_db)):
    """Закрывает текущую активную кассовую смену и блокирует продажи"""
    # Ищем открытую смену
    stmt = select(CashDay).where(CashDay.is_closed == False)
    result = await db.execute(stmt)
    active_day = result.scalar_one_or_none()
    
    if not active_day:
        raise HTTPException(status_code=400, detail="В системе нет открытых кассовых смен")
        
    # Закрываем смену
    active_day.is_closed = True
    await db.commit()
    
    # Асинхронно отправляем лог закрытия смены (Команда 0401/Живой пазл)
    async with httpx.AsyncClient() as client:
        try:
            await client.post(
                "http://logger:8001/api/v1/log", 
                json={"service": "core", "operation_code": "0401", "level": "INFO", "message": f"Кассовая смена ID {active_day.id} успешно закрыта кассиром"}, 
                timeout=1.0
            )
        except Exception:
            pass
            
    return {"status": "success", "message": f"Кассовая смена ID {active_day.id} успешно закрыта"}
