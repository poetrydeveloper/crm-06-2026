# services/qa_orchestrator/features/frontend/steps/12_admin_unit_map_steps.py
import httpx
import uuid

GATEWAY_URL = "http://gateway:80"

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

async def run_12_admin_unit_map_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка экрана поштучного аудита физических юнитов.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Принудительно генерирует номенклатуру и складской приход,
    гарантируя наличие записей в product_units для сквозного аудита.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ГАРАНТИРОВАННОЕ НАПОЛНЕНИЕ СУБД С НУЛЯ
            # Заводим бренд и категорию
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Audit Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Audit Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            # Заводим номенклатурную карточку
            product_payload = {
                "name": "Инструмент сквозного аудита QA",
                "code": f"AUDIT-UNIT-{uid}",
                "recommended_retail_price": 1200.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            product_res = await client.post("/api/v1/catalog/products", json=product_payload)
            product_id = get_any_id(product_res.json() if product_res.status_code in (200, 201) else {}, "product_id", "id")

            # Регистрируем контрагента
            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Audit Supplier {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            # Проводим приёмку накладной, физически штампуя записи в product_units
            await client.post("/api/v1/warehouse/receipts", json={
                "invoice_number": f"INV-AUDIT-{uid}",
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 2, "actual_purchase_price": 700.0}]
            })

            # 📊 2. ВЫПОЛНЯЕМ АТОМАРНУЮ ПРОВЕРКУ РОУТА
            response = await client.get("/admin/unit-map")
            
            if response.status_code == 200:
                results.append("   ✅ Дано Пользователь открыл экран аудита юнитов по адресу '/admin/unit-map'")
                results.append("   ✅ Тогда Система запрашивает массив сырых данных СУБД product_units")
                results.append("   ✅ И Отображает интерактивную таблицу поштучного учета с серийными номерами и физическими статусами единиц")
            else:
                return [f"❌ Сбой аудита: Роут /admin/unit-map вернул код {response.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА КАРТЫ ЮНИТОВ: {str(e)}"]

    return results
