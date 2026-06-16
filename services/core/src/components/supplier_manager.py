# services/core/src/components/supplier_manager.py
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import Supplier

class SupplierManager:
    @staticmethod
    async def create_supplier(payload, db: AsyncSession) -> dict:
        """🛠️ Атомарное добавление нового контрагента в СУБД"""
        existing = await db.execute(select(Supplier).where(Supplier.name == payload.name))
        if existing.scalar_one_or_none():
            raise HTTPException(status_code=400, detail="Поставщик с таким именем уже существует")
        
        new_sup = Supplier(name=payload.name, contact_info=payload.contact_info)
        db.add(new_sup)
        # Фиксация транзакции автоматически закроется генератором get_db в роутере
        await db.flush()
        return {"status": "success", "supplier_id": new_sup.id}

    @staticmethod
    async def get_all_suppliers(db: AsyncSession) -> list[dict]:
        """📋 Атомарное чтение справочника поставщиков для селектов фронтенда"""
        result = await db.execute(select(Supplier))
        return [{"id": s.id, "name": s.name, "contact_info": s.contact_info} for s in result.scalars().all()]
