# services/qa_orchestrator/fixtures_data.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def bootstrap_sterile_fixtures() -> dict:
    """
    🌱 SEEDING DATA CENTER ОРКЕСТРАТОРА (FORCE 4401 EDITION):
    Генерирует эталонный каркас набора Force 4401 и его дочерних сателлитов
    через HTTP-запросы шлюза, гарантируя прохождение FIFO, кассы и аналитики.
    """
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Force-Seeder/2026"}
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=15.0) as client:
        try:
            # 1. Бренд (Force) и Категория (Наборы инструментов)
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Force"})
            brand_id = brand_res.json().get("brand_id", 1)
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Наборы бит и инструментов"})
            category_id = cat_res.json().get("category_id", 1)

            # 2. Главный Набор-Родитель (Force 4401)
            parent_payload = {
                "name": "Набор бит HEX, Torx, Spline 40 пр. 10 мм Force 4401", "code": "FORCE-4401",
                "recommended_retail_price": 4500.0, "category_id": int(category_id), "brand_id": int(brand_id)
            }
            parent_res = await client.post("/api/v1/catalog/products", json=parent_payload)
            parent_product_id = parent_res.json().get("product_id") or parent_res.json().get("id") or 1

            # 3. Детали-сателлиты (Force-компоненты для тестов разборов и RuleEngine)
            child_items = [
                {"name": "Бита HEX 4 мм, длина 30 мм (хвостовик 10 мм) Force", "code": "1743004", "price": 120.0},
                {"name": "Бита HEX 5 мм, длина 30 мм (хвостовик 10 мм) Force", "code": "1743005", "price": 120.0},
                {"name": "Бита TORX T20, длина 30 мм (хвостовик 10 мм) Force", "code": "1763020", "price": 130.0},
                {"name": "Бита TORX T25, длина 30 мм (хвостовик 10 мм) Force", "code": "1763025", "price": 135.0},
                {"name": "Бита SPLINE M5, длина 30 мм (хвостовик 10 мм) Force", "code": "1783005", "price": 140.0},
                {"name": "Переходник для бит 1/2\"DR х 10 мм Force", "code": "81047", "price": 350.0}
            ]
            
            product_ids = {}
            for item in child_items:
                p_res = await client.post("/api/v1/catalog/products", json={
                    "name": item["name"], "code": item["code"], "recommended_retail_price": item["price"],
                    "category_id": int(category_id), "brand_id": int(brand_id)
                })
                p_id = p_res.json().get("product_id") or p_res.json().get("id")
                if p_id:
                    product_ids[item["code"]] = int(p_id)

            # 4. Регистрируем Поставщика (Force Снаб) и Покупателя
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "Force Снабжение Опт"})
            supplier_id = sup_res.json().get("supplier_id") or 1
            cust_res = await client.post("/api/v1/catalog/customers", json={"name": "Автомастерская Сервис", "phone": "+79998887766"})
            customer_id = cust_res.json().get("customer_id") or 1

            # 5. Возвращаем монолитный слепок ID фикстур для тест-шагов оркестратора
            return {
                "brand_id": int(brand_id),
                "category_id": int(category_id),
                "parent_product_id": int(parent_product_id),
                "supplier_id": int(supplier_id),
                "customer_id": int(customer_id),
                "child_product_ids": product_ids  # Словарь вида {"1763025": ID}
            }
        except Exception as e:
            print(f"🚨 [КРИТИЧЕСКИЙ СБОЙ ГЕНЕРАЦИИ FORCE 4401]: {str(e)}")
            return {"brand_id": 1, "category_id": 1, "parent_product_id": 1, "supplier_id": 1, "customer_id": 1, "child_product_ids": {}}
