# services/core/src/components/cash_day_manager.py
import httpx
from datetime import datetime
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import CashDay

class CashDayManager:
    @staticmethod
    async def open_day(payload: dict, db: AsyncSession) -> dict:
        existing = await db.execute(select(CashDay).where(CashDay.is_closed == False))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="В системе уже есть открытая кассовая смена")

        date_str = payload.get("date")
        parsed_date = datetime.fromisoformat(date_str.replace("Z", "+00:00")) if date_str else datetime.utcnow()
        
        new_day = CashDay(date=parsed_date, is_closed=False, total_revenue=Decimal("0.00"))
        db.add(new_day)
        await db.commit()
        return {"status": "success", "cash_day_id": new_day.id, "message": "Кассовая смена успешно открыта"}

    @staticmethod
    async def close_day(db: AsyncSession) -> dict:
        stmt = select(CashDay).where(CashDay.is_closed == False)
        result = await db.execute(stmt)
        active_day = result.scalar_one_or_none()
        
        if not active_day:
            raise HTTPException(status_code=400, detail="В системе нет открытых кассовых смен")
            
        active_day.is_closed = True
        await db.commit()
        
        try:
            async with httpx.AsyncClient() as client:
                await client.post(
                    "http://logger:8001/api/v1/log", 
                    json={"service": "core", "operation_code": "0401", "level": "INFO", "message": f"Кассовая смена ID {active_day.id} успешно закрыта кассиром"}, 
                    timeout=1.0
                )
        except Exception:
            pass
                
        return {"status": "success", "message": f"Кассовая смена ID {active_day.id} успешно закрыта"}

    @staticmethod
    async def reopen_day(cash_day_id: int, db: AsyncSession) -> dict:
        cash_day = await db.get(CashDay, cash_day_id)
        if not cash_day:
            raise HTTPException(status_code=404, detail=f"Кассовый день с ID {cash_day_id} не найден")
        active_day = await db.execute(select(CashDay).where(CashDay.is_closed == False, CashDay.id != cash_day_id))
        if active_day.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Нельзя переоткрыть этот день, пока в системе активна другая кассовая смена.")
        cash_day.is_closed = False
        await db.commit()
        return {"status": "success", "message": "Кассовый день успешно переоткрыт"}
