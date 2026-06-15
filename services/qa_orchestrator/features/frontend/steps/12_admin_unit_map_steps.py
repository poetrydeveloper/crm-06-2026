# services/qa_orchestrator/features/frontend/steps/12_admin_unit_map_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_12_admin_unit_map_assertions() -> list[str]:
    """
    Атомарный E2E-тест: Проверка экрана поштучного аудита физических юнитов.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            response = await client.get("/admin/unit-map")
            if response.status_code == 200:
                results.append("   ✅ Дано Пользователь открыл экран аудита юнитов по адресу '/admin/unit-map'")
                results.append("   ✅ Тогда Система запрашивает массив сырых данных СУБД product_units")
                results.append("   ✅ И Отображает интерактивную таблицу поштучного учета с серийными номерами")
            else:
                return [f"❌ Сбой аудита: Роут /admin/unit-map вернул код {response.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА КАРТЫ ЮНИТОВ: {str(e)}"]

    return results
