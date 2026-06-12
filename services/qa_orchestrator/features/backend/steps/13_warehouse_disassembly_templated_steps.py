# 13_warehouse_disassembly_templated_steps.py
import httpx
import uuid
import asyncpg
from datetime import datetime

GATEWAY_URL = "http://crm_backend_core:8000/api/v1"
DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

async def run_warehouse_disassembly_templated_assertions():
    """Стадия 8: Изолированное тестирование разукомплектации наборов по шаблону"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Накатываем инфраструктуру
            brand_res = await client.post("/catalog/brands", json={"name": f"Set Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/catalog/categories", json={"name": f"Set Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            # А) Создаем карточку НАБОРА инструментов
            parent_prod = await client.post("/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SET-{uid}",
                "name": f"Набор_инструментов_{uid}", "recommended_retail_price": 2000.00, 
                "images": [], "search_aliases": [], "search_tags": []
            })
            parent_product_id = parent_prod.json().get("product_id") or parent_prod.json().get("id")
            
            # Б) Создаем 2 карточки отдельных сателлитов (головки/ключи)
            child1_prod = await client.post("/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SAT1-{uid}",
                "name": "головка_сателлит_12мм", "recommended_retail_price": 300.00, 
                "images": [], "search_aliases": [], "search_tags": ["сателлит"]
            })
            child1_id = child1_prod.json().get("product_id") or child1_prod.json().get("id")
            
            child2_prod = await client.post("/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SAT2-{uid}",
                "name": "головка_сателлит_14мм", "recommended_retail_price": 350.00, 
                "images": [], "search_aliases": [], "search_tags": ["сателлит"]
            })
            child2_id = child2_prod.json().get("product_id") or child2_prod.json().get("id")
            
            # 2. РЕГИСТРИРУЕМ ШАБЛОН РАЗБОРА В СУБД (QA-робот настраивает связи)
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.execute("""
                INSERT INTO product_assembly_templates (parent_product_id, child_product_id, quantity)
                VALUES ($1, $2, 1), ($1, $3, 1);
            """, parent_product_id, child1_id, child2_id)
            
            # 3. ПРИНИМАЕМ 1 ЦЕЛЫЙ НАБОР НА СКЛАД ЧЕРЕЗ НАШУ НОВУЮ АВТОГЕНЕРАЦИЮ
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Set {uid}"})
            supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id")
            
            await client.post("/warehouse/receipts", json={
                "supplier_id": supplier_id,
                "items": [{"product_id": parent_product_id, "quantity": 1, "actual_purchase_price": 1000.00}]
            })
            
            # Считываем автогенерированный уникальный серийник приехавшего набора
            parent_unit_row = await conn.fetchrow(
                "SELECT unique_serial_number FROM product_units WHERE product_id = $1 AND physical_status = 'IN_STORE' LIMIT 1;", 
                parent_product_id
            )
            await conn.close()
            
            if not parent_unit_row:
                raise Exception("Бэкенд не создал ProductUnit набора при приемке накладной!")
            parent_serial = parent_unit_row["unique_serial_number"]
            
            # 4. ВЫЗЫВАЕМ НАШУ НОВУЮ РУЧКУ РАЗБОРА НАБОРА ПО ШАБЛОНУ (Команда 0102)
            dis_res = await client.post("/warehouse/disassembly/templated", json={
                "unique_serial_number": parent_serial
            })
            if dis_res.status_code != 200:
                raise Exception(f"Ручка разбора набора ответила ошибкой. Код: {dis_res.status_code}, Текст: {dis_res.text}")
                
            results.append("✔️ Шаг 'Запрос на разукомплектацию набора по шаблону успешно выполнен' — ПРОЙДЕН")

            # 5. ПРОВЕРЯЕМ МАТЕРИАЛИЗАЦИЮ САТЕЛЛИТОВ ЧЕРЕЗ УМНЫЙ ПОИСК КАССЫ
            search_res = await client.get("/catalog/search", params={"q": "сателлит"})
            catalog_output = search_res.json()
            
            # Проверяем, что в выдаче поиска по запросу 'сателлит' лежат обе наши новые головки с остатком 1
            found_ids = [p.get("id") for p in catalog_output if p.get("available_qty") == 1]
            if child1_id not in found_ids or child2_id not in found_ids:
                raise Exception(f"Сателлиты не появились на остатках кассы! Найдено уникальных id: {found_ids}")
                
            results.append("✔️ Шаг 'Набор переведен в IN_DISASSEMBLED, сателлиты успешно выставлены в IN_STORE' — ПРОЙДЕН")

        except Exception as e:
            return [f"❌ СБОЙ стадии разукомплектации набора по шаблону: {str(e)}"]
            
    return results
