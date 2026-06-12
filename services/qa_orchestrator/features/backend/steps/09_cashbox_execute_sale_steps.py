# 09_cashbox_execute_sale_steps.py
import httpx
import uuid
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
GATEWAY_URL = "http://backend:8000"

async def run_cashbox_execute_sale_assertions():
    """Стадия 3: Автономная розничная продажа по FIFO"""
    results = []
    uid = uuid.uuid4().hex[:6]
    engine = create_async_engine(DATABASE_URL)
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Fi Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/api/v1/catalog/categories", json={"name": f"Fi Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"F-{uid}",
                "name": f"Товар_{uid}", "recommended_retail_price": 500.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Sup Fi {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            o1 = {"supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 100.00}]}
            await client.post("/api/v1/warehouse/orders", json=o1)
            
            async with engine.begin() as conn:
                await conn.execute(
                    text("UPDATE product_units SET physical_status = 'IN_STORE', logistics_status = 'RECEIVED' WHERE product_id = :pid"),
                    {"pid": product_id}
                )
            
            # Открываем кассовую смену
            await client.post("/api/v1/cash/days/open", json={"date": datetime.utcnow().isoformat()})
                
            # Пробиваем чек продажи
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            res = await client.post("/api/v1/cash/sales", json=sale_payload)
            if res.status_code != 201:
                raise Exception(f"Ошибка проведения чека при открытой смене. Код: {res.status_code}")
                
            results.append("✔️ Шаг 'Розничная FIFO-продажа успешно завершена' — ПРОЙДЕН")
            await client.post("/api/v1/cash/days/close")
        except Exception as e:
            return [f"❌ СБОЙ стадии проведения чека по FIFO: {str(e)}"]
            
    return results
