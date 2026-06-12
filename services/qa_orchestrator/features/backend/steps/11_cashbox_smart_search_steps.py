# 11_cashbox_smart_search_steps.py
import httpx
import uuid
from datetime import datetime

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_cashbox_smart_search_assertions():
    """Стадия 6: Тестирование умного поиска уникальных автогенерируемых остатков"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            sup = await client.post("/warehouse/suppliers", json={"name": f"Поставщик Поиск {uid}"})
            supplier_id = sup.json().get("supplier_id")
            brand = await client.post("/catalog/brands", json={"name": f"Бренд Поиск {uid}"})
            brand_id = brand.json().get("brand_id")
            cat = await client.post("/catalog/categories", json={"name": f"Категория Поиск {uid}"})
            category_id = cat.json().get("category_id") or cat.json().get("id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"Q-{uid}",
                "name": "ключ_рожковый_10мм_toptul", "recommended_retail_price": 500.00, 
                "images": [], "search_aliases": ["ск 10"], "search_tags": ["ключ", "рожковый", "10мм", "toptul"]
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            # Официальная приемка на склад с автогенерацией СРАЗУ 3 ЮНИТОВ
            await client.post("/warehouse/receipts", json={
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "actual_purchase_price": 100.00}]
            })
            
            await client.post("/cash/days/open", json={"date": datetime.utcnow().isoformat()})

            # Вызываем умный поиск
            search_res = await client.get("/catalog/search", params={"q": "рожков 10мм"})
            if search_res.status_code != 200:
                raise Exception(f"Ошибка ручки поиска. Код: {search_res.status_code}")
            
            catalog_output = search_res.json()
            target_product = next((p for p in catalog_output if p.get("id") == product_id), None)
            
            if not target_product:
                raise Exception("Товар не найден через умный поиск по фразе 'рожков 10мм'!")
                
            if target_product.get("available_qty") != 3:
                raise Exception(f"Неверный поштучный остаток! Ожидали 3, прилетело: {target_product.get('available_qty')}")
                
            results.append("✔️ Шаг 'Изолированный умный поиск физических остатков' — ПРОЙДЕН")
            await client.post("/cash/days/close")

        except Exception as e:
            return [f"❌ СБОЙ атомарной стадии умного поиска: {str(e)}"]
            
    return results
