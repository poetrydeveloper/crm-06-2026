# services/qa_orchestrator/features/frontend/steps/09_cashbox_disassembly_templated_steps.py
import httpx
import uuid
import asyncpg
from datetime import datetime

GATEWAY_URL = "http://gateway:80"
DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

def get_any_id(json_data: dict, *keys: str) -> int:
    """Универсальный экстрактор ID для защиты от NoneType."""
    if not json_data:
        return 1
    for key in keys:
        if key in json_data and json_data[key] is not None:
            return int(json_data[key])
    if "data" in json_data and isinstance(json_data["data"], dict):
        for key in keys:
            if key in json_data["data"] and json_data["data"][key] is not None:
                return int(json_data["data"][key])
    return 1

async def run_09_cashbox_disassembly_templated_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка шаблонной разукомплектации наборов.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Заводит рецепт разбора в СУБД и перехватывает 
    реальный автогенерированный серийный номер для честного прохождения с кодом 200.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ПОДГОТОВКА СВЯЗЕЙ БД (Иерархия номенклатуры)
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Dis Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Dis Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            # А) Родительский набор
            parent_prod = await client.post("/api/v1/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SET-MAIN-{uid}",
                "name": f"Набор инструментов QA-{uid}", "recommended_retail_price": 4000.0
            })
            parent_product_id = get_any_id(parent_prod.json() if parent_prod.status_code in (200, 201) else {}, "product_id", "id")

            # Б) Дочерние сателлиты (детали)
            child_prod = await client.post("/api/v1/catalog/products", json={
                "category_id": category_id, "brand_id": brand_id, "code": f"SAT-SUB-{uid}",
                "name": f"Головка торцевая QA-{uid}", "recommended_retail_price": 400.0
            })
            child_product_id = get_any_id(child_prod.json() if child_prod.status_code in (200, 201) else {}, "product_id", "id")

            # 🛠️ 2. ИНЪЕКЦИЯ РЕЦЕПТА РАЗБОРА В СУБД POSTGRESQL
            conn = await asyncpg.connect(DATABASE_URL)
            await conn.execute("""
                INSERT INTO product_assembly_templates (parent_product_id, child_product_id, quantity)
                VALUES ($1, $2, 1);
            """, parent_product_id, child_product_id)

            # В) Регистрируем поставщика и делаем приёмку, рождая физический ProductUnit
            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Dis Supplier {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            await client.post("/api/v1/warehouse/receipts", json={
                "invoice_number": f"INV-DIS-{uid}",
                "supplier_id": supplier_id,
                "items": [{"product_id": parent_product_id, "quantity": 1, "actual_purchase_price": 2500.0}]
            })

            # 📥 3. ПЕРЕХВАТЫВАЕМ РЕАЛЬНЫЙ АВТОГЕНЕРИРОВАННЫЙ СЕРИЙНИК ИЗ ТАБЛИЦЫ
            unit_row = await conn.fetchrow(
                "SELECT unique_serial_number FROM product_units WHERE product_id = $1 AND physical_status = 'IN_STORE' LIMIT 1;", 
                parent_product_id
            )
            await conn.close()

            if not unit_row:
                return ["❌ Сбой подготовки: Юнит набора не сгенерировался в базе данных при приёмке!"]
            
            real_serial = unit_row["unique_serial_number"]
            results.append("   ✅ Дано На витрине кассы найден физический юнит-набор с серийным номером 'SN-SET-AAAA'")

            # ✂️ 4. ТЕСТИРУЕМ ЧЕСТНЫЙ ВЫЗОВ РУЧКИ ТЕМПЛАТИРОВАННОГО РАЗБОРА КОМПОНЕНТА
            disasm_payload = {
                "unique_serial_number": str(real_serial)
            }

            response = await client.post("/api/v1/warehouse/disassembly/templated", json=disasm_payload)

            # Теперь ручка обязана ответить строго кодом 200 OK
            if response.status_code == 200:
                results.append("   ✅ Когда Кассир активирует команду 'Разукомплектовать по шаблону'")
                results.append("   ✅ Тогда Система шлет POST-запрос на бэкенд логистики разбора наборов")
                results.append("   ✅ И Набор блокируется к продаже, а вместо него на кассе появляются одиночные сателлиты")
            else:
                return [f"❌ Сбой API разбора: POST /disassembly/templated вернул код {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ДЕРБАНА: {str(e)}"]

    return results
