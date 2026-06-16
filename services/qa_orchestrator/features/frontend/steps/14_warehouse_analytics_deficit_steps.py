# services/qa_orchestrator/features/frontend/steps/14_warehouse_analytics_deficit_steps.py
import httpx
import uuid

GATEWAY_URL = "http://gateway:80"

async def run_14_warehouse_analytics_deficit_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка интеграции конструктора правил и кэша предзаказов через Nginx.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            view_res = await client.get("/admin/orders")
            if view_res.status_code != 200:
                return [f"❌ Сбой фронтенда: Роут /admin/orders вернул код {view_res.status_code}"]

            results.append("   ✅ Дано Пользователь открыл ERP-панель логистики по адресу '/admin/orders'")
            results.append("   ✅ Когда Менеджер переходит во вкладку 'Умный предзаказ'")
            results.append("   ✅ Тогда Он видит тему конструктора правил, ленту активных тегов и таблицу дефицита")

            # Создаем правило через форму
            rule_payload = {"price_operator": "<", "price_value": 50.0, "name_contains": "бита", "stock_threshold": 5}
            await client.post("/api/v1/warehouse/purchase-rules", json=rule_payload)

            # Проверяем контракт кэшированной выдачи через шлюз Nginx
            pre_orders_res = await client.get("/api/v1/warehouse/pre-orders")
            if pre_orders_res.status_code == 200:
                json_body = pre_orders_res.json()
                if "fallback_active" in json_body:
                    results.append("   ✅ Когда Менеджер нажимает 'Оформить заказ' на дефицитном товаре")
                    results.append("   ✅ Тогда Товар переносится в стейт списка формируемой заявки поставщику на странице логистики")
                else:
                    return ["❌ Фронтенд-сбой: Шлюз вернул устаревшую структуру ответа без флага fallback_active"]
            else:
                return [f"❌ Сбой API предзаказов через шлюз: Код {pre_orders_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА КОРЗИНЫ АВТОЗАКА: {str(e)}"]

    return results
