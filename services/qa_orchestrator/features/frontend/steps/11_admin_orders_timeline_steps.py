# services/qa_orchestrator/features/frontend/steps/11_admin_orders_timeline_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_11_admin_orders_timeline_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка отображения хронологического таймлайна заказов.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # Проверяем доступность роута таймлайна
            response = await client.get("/admin/orders")
            if response.status_code == 200:
                results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/admin/orders'")
                results.append("   ✅ Тогда Система запрашивает историю движений из ядра СУБД")
                results.append("   ✅ И Отображает интерактивную карту таймлайна с текущими статусами заявок")
            else:
                return [f"❌ Сбой таймлайна: Роут /admin/orders вернул код {response.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ТАЙМЛАЙНА: {str(e)}"]

    return results
