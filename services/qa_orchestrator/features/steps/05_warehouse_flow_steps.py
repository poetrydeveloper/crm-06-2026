# 05_warehouse_flow_steps.py
import httpx
import uuid

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_warehouse_flow_story_assertions():
    """Проверка Истории: Создание заявки поставщику (Команда 0001) со статусом EXPECTED"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # Подготовка: Создаем тестового поставщика и товар
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Flow {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            brand_res = await client.post("/catalog/brands", json={"name": f"Brand Flow {uid}"})
            brand_id = brand_res.json().get("brand_id")
            
            cat_res = await client.post("/catalog/categories", json={"name": f"Cat Flow {uid}"})
            category_id = cat_res.json().get("category_id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"FLW-{uid}",
                "name": f"Товар Потока {uid}", "recommended_retail_price": 500.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            # Действие: Формируем заявку (Команда 0001) по правильному роуту с учетом префиксов
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "estimated_purchase_price": 250.00}]
            }
            res = await client.post("/warehouse/orders", json=order_payload)
            
            if res.status_code != 201:
                raise Exception(f"Бэкенд вернул {res.status_code}: {res.text}")
                
            assert float(res.json().get("total_financial_load")) == 750.00
            results.append("✔️ Шаг 'Заявка создана, финансовая нагрузка рассчитана' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Тест формирования заявки 0001 — СБОЙ ({str(e)})"]
            
    return results
