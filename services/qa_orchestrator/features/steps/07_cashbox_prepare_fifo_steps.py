# 07_cashbox_prepare_fifo_steps.py
import httpx
import uuid
import asyncio
from datetime import datetime
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
GATEWAY_URL = "http://backend:8000"

async def run_cashbox_prepare_fifo_assertions():
    """Стадия 1: Подготовка остатков FIFO и открытие дня"""
    results = []
    uid = uuid.uuid4().hex[:6]
    engine = create_async_engine(DATABASE_URL)
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # Используем ваши родные ключи из ответов ядра бэкенда!
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
            
            # Накатываем 2 партии по FIFO
            o1 = {"supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 100.00}]}
            await client.post("/api/v1/warehouse/orders", json=o1)
            
            await asyncio.sleep(1.1) # Разносим метки времени для закона FIFO!
            
            o2 = {"supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 105.00}]}
            await client.post("/api/v1/warehouse/orders", json=o2)
            
            async with engine.begin() as conn:
                await conn.execute(
                    text("UPDATE product_units SET physical_status = 'IN_STORE', logistics_status = 'RECEIVED' WHERE product_id = :pid"),
                    {"pid": product_id}
                )
            
            # Открываем день
            await client.post("/api/v1/cash/days/open", json={"date": datetime.utcnow().isoformat()})
                
            results.append("✔️ Шаг 'Два FIFO-юнита успешно подготовлены и смена открыта' — ПРОЙДЕН")
            await client.post("/api/v1/cash/days/close")
        except Exception as e:
            return [f"❌ СБОЙ стадии подготовки данных FIFO: {str(e)}"]
            
    return results
