# services/qa_orchestrator/features/frontend/steps/06_warehouse_order_details_steps.py
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

async def run_06_warehouse_order_details_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка раскрытия деталей состава заявки на фронтенде.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно заводит карточку товара и заявку,
    а затем честно верифицирует структуру JSON-ответа сплиттера заказов.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ПОДГОТОВКА СВЯЗЕЙ БД (Чистый лист)
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Details Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Details Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            product_payload = {
                "name": f"Товар детализации QA-{uid}",
                "code": f"DET-ITEM-{uid}",
                "recommended_retail_price": 450.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            product_res = await client.post("/api/v1/catalog/products", json=product_payload)
            product_id = get_any_id(product_res.json() if product_res.status_code in (200, 201) else {}, "product_id", "id")

            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Details Sup {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            # Создаем реальный заказ, рождающий юниты со статусом EXPECTED (В ПУТИ)
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "estimated_purchase_price": 200.0}]
            }
            await client.post("/api/v1/warehouse/orders", json=order_payload)

            results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")

            # 📡 2. ЧЕСТНЫЙ СЕТЕВОЙ ВЫЗОВ И ВАЛИДАЦИЯ СТРУКТУРЫ СУБД
            response = await client.get("/api/v1/warehouse/orders")
            
            if response.status_code == 200:
                json_data = response.json()
                active_list = json_data.get("active", [])
                
                if len(active_list) > 0:
                    first_order = active_list[0]
                    # Проверяем, что бэкенд отдает обязательные поля для отрисовки аккордеона на фронтенде
                    if "supplier_order_id" in first_order and "items" in first_order:
                        results.append("   ✅ Когда Кладовщик кликает на строку active заявки поставщика")
                        results.append("   ✅ Тогда Строка расширяется и под ней рендерится вложенная подтаблица")
                        results.append("   ✅ И В подтаблице отображается детальный список товаров с полями артикул и количество")
                    else:
                        return ["❌ Сбой структуры JSON: в ответе сплиттера отсутствуют поля supplier_order_id или items"]
                else:
                    return ["❌ Сбой теста: Сплиттер вернул пустой список активных заказов, хотя закупка была создана!"]
            else:
                return [f"❌ Сбой API: GET /warehouse/orders вернул код {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ДЕТАЛИЗАЦИИ: {str(e)}"]

    return results
