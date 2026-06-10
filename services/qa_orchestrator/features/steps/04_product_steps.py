# product_steps.py
import httpx
import uuid

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_product_story_assertions():
    """Проверка Истории 3: Карточки товаров, обязательные связи, images и аномалии"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        # 1. Тест обязательности полей
        try:
            bad_payload = {"category_id": 1, "code": f"ERR-{uid}", "name": "Товар Без Бренда"}
            res = await client.post("/catalog/products", json=bad_payload)
            assert res.status_code == 422
            results.append("✔️ Шаг 'Валидация обязательных полей карточки товара' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Тест валидации полей товара — СБОЙ ({str(e)})"]

        # 2. Тест работы с Резервной категорией (ID=1) и выявления аномалий
        try:
            # Гарантируем наличие резервной категории в СУБД на лету
            # Шлем запрос на создание. Если она уже есть, бэкенд вернет 400, мы это просто пропустим
            await client.post("/catalog/categories", json={"name": "резервная_категория", "parent_id": None})
            
            # Создаем дефолтный бренд
            brand_res = await client.post("/catalog/brands", json={"name": f"Anom Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            
            # Создаем товар в Резервной категории с ID 1
            prod_payload = {
                "category_id": 1,
                "brand_id": brand_id,
                "code": f"ANOM-{uid}",
                "name": "Аномальный Товар",
                "recommended_retail_price": 300.00,
                "images": ["/static/placeholder.png"],
                "search_aliases": []
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            if prod_res.status_code != 201:
                raise Exception(f"Ошибка создания товара в категории 1: {prod_res.status_code} - {prod_res.text}")
                
            created_prod_id = prod_res.json().get("product_id")
            
            # Стучимся в эндпоинт выявления аномалий
            anom_res = await client.get("/catalog/products/anomalies")
            assert anom_res.status_code == 200
            assert anom_res.json().get("has_anomalies") is True
            
            anom_codes = [p["code"] for p in anom_res.json().get("products", [])]
            assert f"ANOM-{uid}" in anom_codes
            results.append("✔️ Шаг 'Система успешно выявила и засигнализировала об аномалии категории' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Тест резервной категории и аномалий — СБОЙ ({str(e)})"]

        # 3. Тест блокировки удаления товара при наличии физических продукт_юнитов
        try:
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Prod Test {uid}"})
            sup_id = sup_res.json().get("supplier_id")
            
            order_payload = {
                "supplier_id": sup_id,
                "items": [{"product_id": created_prod_id, "quantity": 1, "estimated_purchase_price": 150.00}]
            }
            await client.post("/warehouse/orders", json=order_payload)
            
            del_res = await client.delete(f"/catalog/products/{created_prod_id}")
            if del_res.status_code != 400:
                raise Exception(f"Бэкенд разрешил удалить товар со складскими остатками! Статус {del_res.status_code}")
                
            results.append("✔️ Шаг 'Защита от удаления товара с зарожденным складом' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Тест блокировки удаления товара — СБОЙ ({str(e)})")
            
    return results
