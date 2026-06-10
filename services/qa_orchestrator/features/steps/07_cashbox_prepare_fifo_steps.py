# 07_cashbox_prepare_fifo_steps.py
import httpx
import uuid
import asyncio
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

DATABASE_URL = "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
GATEWAY_URL = "http://backend:8000"

async def run_cashbox_prepare_fifo_assertions():
    """Стадия 1: Подготовка остатков FIFO на складе"""
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
                "name": f"Товар {uid}", "recommended_retail_price": 500.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Sup Fi {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            # Заказ 1 (СТАРЫЙ)
            o1 = {"supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 100.00}]}
            await client.post("/api/v1/warehouse/orders", json=o1)
            
            await asyncio.sleep(1.1) # Разносим метки времени
            
            # Заказ 2 (НОВЫЙ)
            o2 = {"supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 105.00}]}
            await client.post("/api/v1/warehouse/orders", json=o2)
            
            # Физически выставляем их на полку
            async with engine.begin() as conn:
                await conn.execute(
                    text("UPDATE product_units SET physical_status = 'IN_STORE', logistics_status = 'RECEIVED' WHERE product_id = :pid"),
                    {"pid": product_id}
                )
            
            # Сохраняем ID сгенерированного товара в глобальный системный файл-буфер /tmp/test_product_id,
            # чтобы следующие независимые шаги 08 и 09 могли обратиться именно к этому товару!
            with open("/tmp/test_product_id", "w") as buf:
                buf.write(str(product_id))
                
            results.append("✔️ Шаг 'Два FIFO-юнита успешно подготовлены и сохранены в СУБД' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ СБОЙ стадии подготовки данных FIFO: {str(e)}"]
            
    return results
