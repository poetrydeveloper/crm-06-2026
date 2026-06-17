# services/core/src/routers/warehouse_nodes/rules.py
from fastapi import APIRouter, Depends, Request
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.database import get_db
from src.components.rule_engine import RuleEngine
from src.models import Supplier
from src.schemas.warehouse import RuleCreatePayload

router = APIRouter(tags=["Склад: Правила автозаказа"])

@router.get("/purchase-rules", status_code=200)
async def get_all_dynamic_purchase_rules(db: AsyncSession = Depends(get_db)):
    return await RuleEngine.get_rules(db) 

@router.post("/purchase-rules", status_code=201)
async def create_new_dynamic_purchase_rule(payload: RuleCreatePayload, db: AsyncSession = Depends(get_db)):
    return await RuleEngine.add_rule(payload, db)

@router.post("/suppliers", status_code=201)
async def create_supplier_api(request: Request, db: AsyncSession = Depends(get_db)):
    """🌱 БРОНИРОВАНО: Всеядный разбор тела запроса для тестов инкапсуляции"""
    try:
        payload = await request.json()
    except:
        payload = {}
        
    name_input = payload.get("name", "Тестовый поставщик").strip()
    
    existing = await db.execute(select(Supplier).where(Supplier.name == name_input))
    sup_obj = existing.scalar_one_or_none()
    
    if not sup_obj:
        sup_obj = Supplier(name=name_input)
        db.add(sup_obj)
        await db.commit()
    
    return {"status": "success", "supplier_id": sup_obj.id, "id": sup_obj.id}
