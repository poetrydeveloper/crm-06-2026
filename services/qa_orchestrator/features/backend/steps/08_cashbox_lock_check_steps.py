# 08_cashbox_lock_check_steps.py
import httpx
import uuid
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
GATEWAY_URL = "http://backend:8000"

async def run_cashbox_lock_check_assertions():
    """Стадия 2: Проверка блокировки чеков при закрытой кассе"""
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
            
            # Гарантируем закрытый кассовый день
            await client.post("/api/v1/cash/days/close")

            # Пробуем продать — ждем ошибку 400
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            res = await client.post("/api/v1/cash/sales", json=sale_payload)
            
            if res.status_code != 400:
                raise Exception(f"Бэкенд вернул HTTP-{res.status_code} вместо HTTP-400.")
                
            results.append("✔️ Шаг 'Блокировка продаж при закрытой смене успешно подтверждена' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ СБОЙ стадии валидации блокировки кассы: {str(e)}"]
            
    return results
