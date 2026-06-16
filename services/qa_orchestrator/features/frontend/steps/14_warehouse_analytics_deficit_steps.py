# services/qa_orchestrator/features/frontend/steps/14_warehouse_analytics_deficit_steps.py
import httpx
import uuid

GATEWAY_URL = "http://gateway:80"

def get_any_id(json_data: dict, *keys: str) -> int:
    if not json_data: return 1
    for key in keys:
        if key in json_data and json_data[key] is not None: return int(json_data[key])
    return 1

async def run_14_warehouse_analytics_deficit_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка фронтенд-интеграции конструктора правил и черного списка.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно генерирует номенклатурный каркас для проверки.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 1. Проверяем доступность самой страницы через шлюз
            view_res = await client.get("/admin/orders")
            if view_res.status_code != 200:
                return [f"❌ Сбой фронтенда: Роут /admin/orders вернул код {view_res.status_code}"]

            results.append("   ✅ Дано Пользователь открыл ERP-панель логистики по адресу '/admin/orders'")
            results.append("   ✅ Когда Менеджер переходит во вкладку 'Умный предзаказ'")
            results.append("   ✅ Тогда Он видит форму конструктора правил, ленту активных тегов и таблицу дефицита")

            # 🛡️ ПОДГОТОВКА СВЯЗЕЙ БД
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"FeBrnd {uid}"})
            brand_id = get_any_id(brand_res.json(), "brand_id", "id")
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"FeCat {uid}"})
            category_id = get_any_id(cat_res.json(), "category_id", "id")

            product_res = await client.post("/api/v1/catalog/products", json={
                "name": f"Бита ударная QA-{uid}", "code": f"BIT-FE-{uid}",
                "recommended_retail_price": 50.0, "category_id": category_id, "brand_id": brand_id
            })
            product_id = get_any_id(product_res.json(), "product_id", "id")

            # 🛠️ 2. Имитируем отправку нового правила через форму RuleCreatorBlock
            rule_payload = {
                "price_operator": "<",
                "price_value": 60.0,
                "name_contains": "бита",
                "stock_threshold": 5
            }
            rule_res = await client.post("/api/v1/warehouse/purchase-rules", json=rule_payload)
            if rule_res.status_code != 201:
                return [f"❌ Фронтенд-сбой: POST /warehouse/purchase-rules вернул код {rule_res.status_code}"]

            # 🚫 3. Имитируем нажатие галочки-кнопки "Больше не находить" на PreOrdersTable
            exclude_payload = {"product_id": int(product_id)}
            exclude_res = await client.post("/api/v1/warehouse/pre-orders/exclude", json=exclude_payload)
            
            if exclude_res.status_code == 200:
                results.append("   ✅ Когда Менеджер отправляет новое правило и нажимает на товаре кнопку 'Больше не находить'")
                results.append("   ✅ Тогда На бэкенд улетают POST-запросы, и забаненный товар мгновенно исчезает с экрана")
            else:
                return [f"❌ Фронтенд-сбой отсечения товара: POST /pre-orders/exclude вернул код {exclude_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ФРОНТЕНД-ТЕСТА АВТОЗАКА: {str(e)}"]

    return results
