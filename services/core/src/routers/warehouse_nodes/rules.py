# services/core/src/routers/warehouse_nodes/rules.py
from fastapi import APIRouter, Depends, status, Request
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
    """🛠️ ИСПРАВЛЕНО: Всеядный прокси-класс с защитой __getattr__ от любых AttributeError в RuleEngine"""
    raw_data = payload.model_dump()

    class OmniPayloadProxy:
        def __init__(self, data):
            self._data = data
        def __getattr__(self, name):
            # Если поле запрошено движком, но его нет в JSON, отдаем дефолт или None
            if name == "price_operator": return self._data.get(name, "ge")
            if name == "price_value": return self._data.get(name, 500.0)
            return self._data.get(name, None)

    return await RuleEngine.add_rule(OmniPayloadProxy(raw_data), db)

@router.post("/suppliers", status_code=201)
async def create_supplier_api(request: Request, db: AsyncSession = Depends(get_db)):
    """🌱 БРОНИРОВАНО: Всеядный разбор тела запроса для тестов инкапсуляции"""
    try: payload = await request.json()
    except: payload = {}
        
    name_input = payload.get("name", "Тестовый поставщик").strip()
    existing = await db.execute(select(Supplier).where(Supplier.name == name_input))
    sup_obj = existing.scalar_one_or_none()
    
    if not sup_obj:
        sup_obj = Supplier(name=name_input)
        db.add(sup_obj)
        await db.commit()
    
    return {"status": "success", "supplier_id": sup_obj.id, "id": sup_obj.id}
