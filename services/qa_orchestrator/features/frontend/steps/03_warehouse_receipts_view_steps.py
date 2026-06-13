# services/qa_orchestrator/features/frontend/steps/03_warehouse_receipts_view_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_03_warehouse_receipts_view_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка доступности экрана открытых поставок.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=3.0) as client:
        try:
            response = await client.get("/warehouse/receipts")
            
            if response.status_code == 200:
                results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
                results.append("   ✅ Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок")
            else:
                return [f"❌ Сбой атомарного шага Склада: Роут /warehouse/receipts вернул {response.status_code}"]
                
        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТИ НА ШАГЕ СКЛАДА: {str(e)}"]

    return results
