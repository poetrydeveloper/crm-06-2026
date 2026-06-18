# services/qa_orchestrator/features/frontend/steps/03_warehouse_receipts_view_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_03_warehouse_receipts_view_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Открытых Складских Заявок.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль реестра накладных снабжения в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ПРОСМОТР СПИСКА АКТИВНЫХ ЗАКАЗОВ ===
        # Проверяем, что роут логистики "/warehouse/receipts" загружается в Chromium
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".warehouse-tabs-container, table")
        results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
        
        # Инспектируем DOM-структуру React на наличие интерактивной таблицы ордеров
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".receipts-table-body, [data-testid='receipts-list']")
        results.append("   ✅ Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок поставщикам")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ НАКЛАДНЫХ: {str(e)}"]

    return results
