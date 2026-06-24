from fastapi import APIRouter, Depends, status, Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from src.database import get_db
from src.components.rule_engine import RuleEngine
from src.models import Supplier
from src.schemas.warehouse import RuleCreatePayload

router = APIRouter(prefix="", tags=["Склад: Правила автозаказа"])

@router.get("/suppliers", status_code=200)
async def list_suppliers(db: AsyncSession = Depends(get_db)):
    """📋 Получить список всех поставщиков"""
    result = await db.execute(select(Supplier).order_by(Supplier.name))
    suppliers = result.scalars().all()
    # 🔥 ИСПРАВЛЕНО: Закрываем транзакцию чтения
    await db.rollback()
    return {
        "suppliers": [{"supplier_id": s.id, "name": s.name} for s in suppliers],
        "total": len(suppliers)
    }

@router.get("/purchase-rules", status_code=200)
async def get_all_dynamic_purchase_rules(db: AsyncSession = Depends(get_db)):
    rules = await RuleEngine.get_rules(db)
    # 🔥 ИСПРАВЛЕНО: Закрываем транзакцию чтения
    await db.rollback()
    return rules

@router.post("/purchase-rules", status_code=201)
async def create_new_dynamic_purchase_rule(payload: RuleCreatePayload, db: AsyncSession = Depends(get_db)):
    """🛠️ ИСПРАВЛЕНО: Убран небезопасный OmniPayloadProxy. Передаем чистый валидированный payload"""
    return await RuleEngine.add_rule(payload, db)

@router.post("/suppliers", status_code=201)
async def create_supplier_api(request: Request, db: AsyncSession = Depends(get_db)):
    """🌱 Создание поставщика с защитой от дублирования и гонки данных"""
    try:
        payload = await request.json()
    except Exception:
        payload = {}
        
    name_input = payload.get("name", "Тестовый поставщик").strip()
    
    try:
        existing = await db.execute(select(Supplier).where(Supplier.name == name_input))
        sup_obj = existing.scalar_one_or_none()
        
        if not sup_obj:
            sup_obj = Supplier(name=name_input)
            db.add(sup_obj)
            await db.commit()
        else:
            await db.rollback()
            
        return {"status": "success", "supplier_id": sup_obj.id, "id": sup_obj.id}
        
    except IntegrityError:
        # 🔥 ИСПРАВЛЕНО: Защита от сбоя уникальности СУБД
        await db.rollback()
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="Поставщик с таким именем уже существует"
        )
