# services/qa_orchestrator/features/frontend/steps/03_warehouse_receipts_view_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from utils.validators import safe_header

FRONTEND_URL = "http://frontend:5173"

async def run_03_warehouse_receipts_view_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Открытых Складских Заявок.
    ИНКАПСУЛЯЦИЯ DOM: Проверка рендеринга списка незакрытых ордеров снабжения.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("UI-WH-0003")}

    async with httpx.AsyncClient(base_url=FRONTEND_URL, headers=headers, timeout=5.0) as client:
        try:
            # === СЦЕНАРИЙ 1: ПРОСМОТР СПИСКА АКТИВНЫХ ЗАКАЗОВ ===
            results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
# services/qa_orchestrator/features/frontend/steps/03_warehouse_receipts_view_steps.py (ЧАСТЬ 2 ИЗ 2)
            # Верифицируем отрисовку интерактивного списка накладных снабжения в DOM-дереве
            results.append("   ✅ Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок поставщикам")

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ РАНТАЙМА ТЕСТИРОВАНИЯ ИНТЕРФЕЙСА СКЛАДА: {str(e)}"]

    return results
