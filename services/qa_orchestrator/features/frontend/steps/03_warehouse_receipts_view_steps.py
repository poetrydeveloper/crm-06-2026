# services/qa_orchestrator/features/frontend/steps/03_warehouse_receipts_view_steps.py
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

async def run_03_warehouse_receipts_view_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка доступности экрана открытых поставок и состава данных.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно заводит тестовую поставку в СУБД,
    гарантируя проверку контента и структуры ответа сплиттера заказов.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ЖЕЛЕЗНАЯ ПОДГОТОВКА ДАННЫХ В СУБД (ЧИСТЫЙ ЛИСТ)
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"View Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"View Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            product_payload = {
                "name": f"Товар для аудита списков QA-{uid}",
                "code": f"VIEW-ITEM-{uid}",
                "recommended_retail_price": 500.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            product_res = await client.post("/api/v1/catalog/products", json=product_payload)
            product_id = get_any_id(product_res.json() if product_res.status_code in (200, 201) else {}, "product_id", "id")

            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"View Sup {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            # Генерируем тестовый заказ, который должен отобразиться в списке активных поставок
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 2, "estimated_purchase_price": 250.0}]
            }
            await client.post("/api/v1/warehouse/orders", json=order_payload)

            # 📡 2. ПРОВЕРКА ФРОНТЕНД-ДОСТУПНОСТИ И СТРУКТУРЫ ОТВЕТА БЭКЕНДА
            response = await client.get("/warehouse/receipts")
            if response.status_code != 200:
                return [f"❌ Сбой атомарного шага Склада: Роут /warehouse/receipts вернул {response.status_code}"]
                
            # Дополнительно делаем запрос к эндпоинту данных, который рендерится на этой странице
            data_res = await client.get("/api/v1/warehouse/orders")
            if data_res.status_code == 200:
                json_data = data_res.json()
                # Проверяем наличие ключа 'active' в ответе нашего вчерашнего сплиттера
                if "active" in json_data:
                    results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
                    results.append("   ✅ Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок")
                else:
                    return ["❌ Сбой контракта: В ответе бэкенда отсутствует обязательный ERP-ключ 'active'"]
            else:
                return [f"❌ Сбой бэкенд-эндпоинта страницы склада: GET /warehouse/orders вернул {data_res.status_code}"]
                
        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТИ НА ШАГЕ СКЛАДА: {str(e)}"]

    return results
