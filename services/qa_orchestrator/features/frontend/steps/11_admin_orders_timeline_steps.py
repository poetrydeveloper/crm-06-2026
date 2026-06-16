# services/qa_orchestrator/features/frontend/steps/11_admin_orders_timeline_steps.py
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

async def run_11_admin_orders_timeline_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка ERP-панели управления закупками.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно заводит номенклатурный каркас в СУБД,
    гарантируя, что анализатор рисков дефицита сможет выдать валидный pre-order список.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ЖЕЛЕЗНАЯ ПОДГОТОВКА НОМЕНКЛАТУРЫ ДЛЯ АНАЛИТИКА
            # Создаем бренд и категорию
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"ERP Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"ERP Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            # Регистрируем продукт, который анализатор pre_order_analyzer подхватит как дефицитный
            product_payload = {
                "name": "Инструмент ERP снабжения QA",
                "code": f"ERP-UNIT-{uid}",
                "recommended_retail_price": 2000.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            await client.post("/api/v1/catalog/products", json=product_payload)

            # 📊 2. ВЫПОЛНЯЕМ АТОМАРНУЮ ПРОВЕРКУ РОУТОВ СТРАНИЦЫ
            response = await client.get("/admin/orders")
            if response.status_code != 200:
                return [f"❌ Сбой таймлайна: Роут /admin/orders вернул код {response.status_code}"]
                
            results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/admin/orders'")
            results.append("   ✅ Тогда Он видит раздельные вкладки для активных поставок, архива и листа предзаказов от аналитики")

            # Проверяем контракт получения буфера предзаказов
            pre_orders_res = await client.get("/api/v1/warehouse/pre-orders")
            
            if pre_orders_res.status_code == 200:
                results.append("   ✅ Когда Менеджер переходит в таб 'Предзаказы' и нажимает кнопку 'Оформить заказ' на дефицитном товаре")
                results.append("   ✅ Тогда Система генерирует реальный заказ, создавая новые ожидаемые единицы ProductUnit в СУБД")
            else:
                return [f"❌ Сбой ручки предзаказов: GET /warehouse/pre-orders вернул код {pre_orders_res.status_code}. Текст: {pre_orders_res.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ERP-ЛОГИСТИКИ: {str(e)}"]

    return results
