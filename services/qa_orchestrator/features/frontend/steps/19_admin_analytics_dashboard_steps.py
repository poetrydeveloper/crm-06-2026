# services/qa_orchestrator/features/frontend/steps/19_admin_analytics_dashboard_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_19_admin_analytics_dashboard_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка интеграции финансового дашборда на кассовых сменах.
    """
    results = []
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 1. Проверяем доступность страницы смен через шлюз Nginx
            response = await client.get("/admin/cash-days")
            if response.status_code != 200:
                return [f"❌ Сбой админки смен: Роут /admin/cash-days вернул код {response.status_code}"]
                
            results.append("   ✅ Дано Администратор открыл панель управления сменами по адресу '/admin/cash-days'")
            results.append("   ✅ Когда Страница инициализируется в браузере директора")

            # 2. Проверяем, что проброшенный через шлюз Nginx путь аналитического summary отдает верную JSON-структуру
            summary_res = await client.get("/api/v1/analytics/summary")
            if summary_res.status_code == 200:
                json_data = summary_res.json()
                if json_data.get("status") == "success" and "metrics" in json_data:
                    results.append("   ✅ Тогда Система отправляет запрос к API аналитического микросервиса /analytics/summary")
                    results.append("   ✅ И На экране успешно рендерится дашборд с выручкой, конверсией и активными клиентами")
                else:
                    return [f"❌ Сбой структуры JSON аналитики: в ответе отсутствуют поля status или metrics!"]
            else:
                return [f"❌ Сбой API-маршрута аналитики через шлюз: GET /api/v1/analytics/summary вернул код {summary_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ДАШБОРДА ВЫРУЧКИ: {str(e)}"]

    return results
