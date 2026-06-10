# 06_warehouse_receipt_steps.py
import httpx
import uuid
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text

# Переключено на asyncpg! Больше никакой psycopg2 не требуется
DATABASE_URL = "postgresql+asyncpg://crm_admin:crm_secure_password@db:5432/crm_main_database"
GATEWAY_URL = "http://backend:8000/api/v1"

async def run_warehouse_receipt_story_assertions():
    results = []
    uid = uuid.uuid4().hex[:6]
    engine = create_async_engine(DATABASE_URL)
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            brand_res = await client.post("/catalog/brands", json={"name": f"Rec Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            
            category_res = await client.post("/catalog/categories", json={"name": f"Rec Category {uid}"})
            category_id = category_res.json().get("category_id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"REC-{uid}",
                "name": f"Товар Приемки {uid}", "recommended_retail_price": 400.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Rec {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 200.00}]
            }
            await client.post("/warehouse/orders", json=order_payload)
            results.append("✔️ Шаг 'В системе создана заявка поставщику' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Ошибка подготовки данных закупки — СБОЙ ({str(e)})"]

        try:
            async with engine.connect() as conn:
                query = text("SELECT unique_serial_number FROM product_units WHERE supplier_id = :sid AND physical_status = 'EXPECTED'")
                db_result = await conn.execute(query, {"sid": supplier_id})
                serial_numbers = [row[0] for row in db_result.fetchall()]
                
            assert len(serial_numbers) == 1
            results.append("✔️ Шаг 'Робот успешно извлек зарожденные серийники из СУБД' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Ошибка прямого извлечения данных из БД — СБОЙ ({str(e)})"]

        try:
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [
                    {"unique_serial_number": serial_numbers[0], "actual_purchase_price": 210.00}
                ]
            }
            res = await client.post("/warehouse/receipts", json=receipt_payload)
            assert res.status_code == 200
            results.append("✔️ Шаг 'Система возвращает статус 200 OK' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Тест вызова эндпоинта приемки /receipts — СБОЙ ({str(e)})"]
            
    return results
