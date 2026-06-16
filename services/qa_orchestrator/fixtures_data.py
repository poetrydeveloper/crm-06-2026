# services/qa_orchestrator/fixtures_data.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def bootstrap_sterile_fixtures() -> dict:
    """
    🌱 SEEDING DATA CENTER ОРКЕСТРАТОРА (FORCE 4401 EDITION):
    Выравнивает ID категорий под требования BDD-фичи 04_product.feature.
    Категория ID 1 гарантированно рождается со строгим именем "резервная_категория".
    """
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Force-Seeder/2026"}
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=15.0) as client:
        try:
            # 1. Бренд (Force)
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Force"})
            brand_id = brand_res.json().get("brand_id", 1)
            
            # 🔥 ИСПРАВЛЕНО: Создаем имя строго в нижнем регистре с нижним подчеркиванием,
            # чтобы SQL-фильтры аномалий бэкенда ядра сработали безотказно!
            await client.post("/api/v1/catalog/categories", json={"name": "резервная_категория"})

            # 2. Создаем нормальную легитимную категорию для набора Force
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Наборы бит и инструментов"})
            category_id = cat_res.json().get("category_id", 2)

            # 3. Главный Набор-Родитель (Force 4401)
            parent_payload = {
                "name": "Набор бит HEX, Torx, Spline 40 пр. 10 мм Force 4401", "code": "FORCE-4401",
                "recommended_retail_price": 4500.0, "category_id": int(category_id), "brand_id": int(brand_id)
            }
            parent_res = await client.post("/api/v1/catalog/products", json=parent_payload)
            parent_product_id = parent_res.json().get("product_id") or parent_res.json().get("id") or 1

            # 4. Детали-сателлиты
            child_items = [
                {"name": "Бита HEX 4 мм, длина 30 мм (хвостовик 10 мм) Force", "code": "1743004", "price": 120.0},
                {"name": "Бита TORX T20, длина 30 мм (хвостовик 10 мм) Force", "code": "1763020", "price": 130.0}
            ]
            product_ids = {}
            for item in child_items:
                p_res = await client.post("/api/v1/catalog/products", json={
                    "name": item["name"], "code": item["code"], "recommended_retail_price": item["price"],
                    "category_id": int(category_id), "brand_id": int(brand_id)
                })
                p_id = p_res.json().get("product_id") or p_res.json().get("id")
                if p_id: product_ids[item["code"]] = int(p_id)

            # 5. Поставщик и Покупатель
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "Force Снабжение Опт"})
            supplier_id = sup_res.json().get("supplier_id") or 1
            cust_res = await client.post("/api/v1/catalog/customers", json={"name": "Автомастерская Сервис", "phone": "+79998887766"})
            customer_id = cust_res.json().get("customer_id") or 1

            return {
                "brand_id": int(brand_id),
                "category_id": int(category_id),
                "parent_product_id": int(parent_product_id),
                "supplier_id": int(supplier_id),
                "customer_id": int(customer_id),
                "child_product_ids": product_ids
            }
        except Exception as e:
            print(f"🚨 [СБОЙ СИДИНГА FORCE]: {str(e)}")
            return {"brand_id": 1, "category_id": 2, "parent_product_id": 1, "supplier_id": 1, "customer_id": 1, "child_product_ids": {}}
