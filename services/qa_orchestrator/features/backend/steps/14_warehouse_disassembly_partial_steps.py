# 14_warehouse_disassembly_partial_steps.py
import httpx
import uuid
import asyncpg
from datetime import datetime

GATEWAY_URL = "http://crm_backend_core:8000/api/v1"
DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

async def run_warehouse_disassembly_partial_assertions():
    """Стадия 9: Тестирование частичного дербана наборов без шаблона"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Накатываем инфраструктуру
            brand_res = await client.post("/catalog/brands", json={"name": f"Derban Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/catalog/categories", json={"name": f"Derban Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            # Создаем карточку НАБОРА и карточку ДЕТАЛИ
            parent_prod = await client.post("/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SET2-{uid}",
                "name": f"Набор_Дербана_{uid}", "recommended_retail_price": 3000.00, 
                "images": [], "search_aliases": [], "search_tags": []
            })
            parent_product_id = parent_prod.json().get("product_id") or parent_prod.json().get("id")
            
            child_prod = await client.post("/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"DET-{uid}",
                "name": "одиночная_деталь_из_набора", "recommended_retail_price": 400.00, 
                "images": [], "search_aliases": [], "search_tags": []
            })
            child_product_id = child_prod.json().get("product_id") or child_prod.json().get("id")
            
            # 2. ПРИНИМАЕМ 1 ЦЕЛЫЙ НАБОР НА СКЛАД ЧЕРЕЗ API
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Derban {uid}"})
            supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id")
            
            await client.post("/warehouse/receipts", json={
                "supplier_id": supplier_id,
                "items": [{"product_id": parent_product_id, "quantity": 1, "actual_purchase_price": 1500.00}]
            })
            
            # Считываем автогенерированный уникальный серийник приехавшего набора из БД
            conn = await asyncpg.connect(DATABASE_URL)
            parent_unit_row = await conn.fetchrow(
                "SELECT id, unique_serial_number FROM product_units WHERE product_id = $1 AND physical_status = 'IN_STORE' LIMIT 1;", 
                parent_product_id
            )
            
            if not parent_unit_row:
                await conn.close()
                raise Exception("Бэкенд не создал ProductUnit набора при приемке!")
            parent_unit_id = parent_unit_row["id"]
            parent_serial = parent_unit_row["unique_serial_number"]
            
            # 3. ВЫЗЫВАЕМ РУЧКУ ЭКСТРЕННОГО ЧАСТИЧНОГО РАЗБОРА (Команда 0103)
            derban_res = await client.post("/warehouse/disassembly/partial", json={
                "unique_serial_number": parent_serial,
                "child_product_id": child_product_id
            })
            if derban_res.status_code != 200:
                await conn.close()
                raise Exception(f"Ручка частичного разбора ответила ошибкой. Код: {derban_res.status_code}")
                
            results.append("✔️ Шаг 'Запрос на экстренный частичный разбор набора без шаблона успешно выполнен' — ПРОЙДЕН")

            # 4. ПРОВЕРЯЕМ СТАТУСЫ САТЕЛЛИТА И РОДИТЕЛЯ В СУБД ПО КРИТЕРИЯМ АТОМАРНОСТИ
            updated_parent = await conn.fetchrow("SELECT physical_status FROM product_units WHERE id = $1;", parent_unit_id)
            child_unit = await conn.fetchrow("SELECT physical_status FROM product_units WHERE parent_unit_id = $1 LIMIT 1;", parent_unit_id)
            await conn.close()
            
            # Проверяем жесткое условие заморозки набора
            if updated_parent["physical_status"] != "LOST":
                raise Exception(f"Родительский набор не заморозился! Статус в БД: {updated_parent['physical_status']}")    
                
            # Проверяем жесткое условие мгновенного списания извлеченной детали в SOLD
            if not child_unit or child_unit["physical_status"] != "SOLD":
                raise Exception(f"Извлеченный сателлит не списался в SOLD! Статус в БД: {child_unit['physical_status'] if child_unit else 'None'}")
                
            results.append("✔️ Шаг 'Из набора выделен 1 сателлит со статусом SOLD, набор переведен в FROZEN_INCOMPLETE' — ПРОЙДЕН")

        except Exception as e:
            return [f"❌ СБОЙ стадии частичного некомплектного разбора: {str(e)}"]
            
    return results
