# services/qa_orchestrator/features/frontend/steps/fixtures_data.py или services/qa_orchestrator/fixtures_data.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def bootstrap_sterile_fixtures() -> dict:
    """
    🌱 СМАРТ-СИДЕР ОРКЕСТРАТОРА (FORCE 4401):
    Если сущности уже созданы в СУБД, автоматически вычитывает их живые ID из базы.
    Намертво исключает ошибки 404/500 из-за некорректных фоллбэков "or 1".
    """
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Force-Seeder/2026"}
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=15.0) as client:
        try:
            # 1. Инжект Брэнда
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Force"})
            brand_id = brand_res.json().get("brand_id")
            if not brand_id:
                # Если уже создан, забираем из общего списка
                b_list = await client.get("/api/v1/catalog/brands")
                brand_id = next((b["id"] for b in b_list.json() if b["name"] == "force"), 1)
            
            # 2. Инжект Резервной категории (ID 1)
            await client.post("/api/v1/catalog/categories", json={"name": "резервная_категория"})

            # 3. Инжект Легитимной категории
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Наборы бит и инструментов"})
            category_id = cat_res.json().get("category_id")
            if not category_id:
                c_list = await client.get("/api/v1/catalog/categories")
                category_id = next((c["id"] for c in c_list.json() if "наборы" in c["name"]), 2)

            # 4. Инжект Главного Набора Force 4401
            parent_payload = {
                "name": "Набор бит HEX, Torx, Spline 40 пр. 10 мм Force 4401", "code": "FORCE-4401",
                "recommended_retail_price": 4500.0, "category_id": int(category_id), "brand_id": int(brand_id)
            }
            parent_res = await client.post("/api/v1/catalog/products", json=parent_payload)
            parent_product_id = parent_res.json().get("product_id") or parent_res.json().get("id")
            if not parent_product_id:
                p_list = await client.get("/api/v1/catalog/products")
                # Всеядный поиск по артикулу
                parent_product_id = next((p["id"] for p in p_list.json() if p["code"] == "FORCE-4401"), 1)

            # 5. Инжект Деталей-сателлитов
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
                if not p_id:
                    p_list = await client.get("/api/v1/catalog/products")
                    p_id = next((p["id"] for p in p_list.json() if p["code"] == item["code"]), 2)
                product_ids[item["code"]] = int(p_id)

            # 6. 🔥 ЖЕСТКИЙ ВЫКАЧ ПОСТАВЩИКА ИЗ СУБД (Защита от 404)
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "Force Снабжение Опт"})
            supplier_id = sup_res.json().get("supplier_id")
            if not supplier_id:
                # Если поставщик уже есть, вычитываем его настоящий ID через GET
                sup_list = await client.get("/api/v1/warehouse/suppliers")
                supplier_id = next((s["id"] for s in sup_list.json() if "Force" in s["name"]), None)

            return {
                "brand_id": int(brand_id),
                "category_id": int(category_id),
                "parent_product_id": int(parent_product_id),
                "supplier_id": int(supplier_id or 1), # Теперь отдаем гарантированно существующий ID из СУБД!
                "child_product_ids": product_ids
            }
        except Exception as e:
            print(f"🚨 [СБОЙ САКРАЛЬНОГО СИДИНГА]: {str(e)}")
            return {"brand_id": 1, "category_id": 2, "parent_product_id": 1, "supplier_id": 1, "child_product_ids": {}}
