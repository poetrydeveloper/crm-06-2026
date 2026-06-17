# services/qa_orchestrator/fixtures/fixtures_data.py
import httpx
from utils.db_finders import find_live_brand_id, find_live_category_id, find_live_product_id, find_live_supplier_id

GATEWAY_URL = "http://gateway:80"

class QAFixtureFactory:
    @staticmethod
    async def bootstrap_sterile_fixtures(client: httpx.AsyncClient) -> dict:
        """🌱 СМАРТ-СИДЕР ОРКЕСТРАТОРА (FORCE 4401) с вынесенными поисковыми компонентами"""
        try:
            # 1. Инжект Брэнда
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Force"})
            brand_id = brand_res.json().get("brand_id") or await find_live_brand_id(client, "force", 1)
            
            # 2. Инжект Резервной категории (ID 1)
            await client.post("/api/v1/catalog/categories", json={"name": "резервная_категория"})

            # 3. Инжект Легитимной категории
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Наборы бит и инструментов"})
            category_id = cat_res.json().get("category_id") or await find_live_category_id(client, "наборы", 2)

            # 4. Инжект Главного Набора Force 4401
            parent_payload = {
                "name": "Набор бит HEX, Torx, Spline 40 пр. 10 мм Force 4401", "code": "FORCE-4401",
                "recommended_retail_price": 4500.0, "category_id": int(category_id), "brand_id": int(brand_id)
            }
            parent_res = await client.post("/api/v1/catalog/products", json=parent_payload)
            parent_product_id = parent_res.json().get("product_id") or parent_res.json().get("id") or await find_live_product_id(client, "FORCE-4401", 1)

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
                p_id = p_res.json().get("product_id") or p_res.json().get("id") or await find_live_product_id(client, item["code"], 2)
                product_ids[item["code"]] = int(p_id)

            # 6. ЖЕСТКИЙ ВЫКАЧ ПОСТАВЩИКА
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "Force Снабжение Опт"})
            supplier_id = sup_res.json().get("supplier_id") or await find_live_supplier_id(client, "Force", 1)

            return {
                "brand_id": int(brand_id), "category_id": int(category_id),
                "parent_product_id": int(parent_product_id), "supplier_id": int(supplier_id),
                "child_product_ids": product_ids
            }
        except Exception as e:
            print(f"🚨 [СБОЙ САКРАЛЬНОГО СИДИНГА]: {str(e)}")
            return {"brand_id": 1, "category_id": 2, "parent_product_id": 1, "supplier_id": 1, "child_product_ids": {}}

    @staticmethod
    async def prepare_linked_brand_with_product(client: httpx.AsyncClient) -> dict:
        """🌱 Кадр СУБД №2: Связанный бренд и товар для защиты Foreign Key (История 2)"""
        brand_res = await client.post("/api/v1/catalog/brands", json={"name": "toptul"})
        brand_id = brand_res.json().get("brand_id") or await find_live_brand_id(client, "toptul", 1)
            
        cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Служебная"})
        category_id = cat_res.json().get("category_id") or await find_live_category_id(client, "Служебная", 1)
        
        await client.post("/api/v1/catalog/products", json={
            "name": "КЛ-10", "code": "КЛ-10", "recommended_retail_price": 100.0, 
            "category_id": int(category_id), "brand_id": int(brand_id)
        })
        return {"brand_id": int(brand_id)}
