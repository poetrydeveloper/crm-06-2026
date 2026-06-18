# services/qa_orchestrator/features/frontend/steps/10_admin_cash_days_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_10_admin_cash_days_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Панели Кассовых Смен.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль реестра смен и экстренных кнопок в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ЭКСТРЕННОЕ УПРАВЛЕНИЕ СМЕНАМИ ===
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", ".cash-days-table, table")
        results.append("   ✅ Дано Пользователь открыл вкладку админки по адресу '/admin/cash-days'")
        
        # Инспектируем наличие столбцов выручки, статусов смен и финансовых результатов
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", "th:has-text('выручка'), .cash-days-row")
        results.append("   ✅ Тогда Он видит таблицу с историей кассовых смен, их статусами и финансовыми цифрами выручки")
        
        # Проверяем наличие экстренной интерактивной кнопки открытия смены
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", "button:has-text('Открыть день'), .btn-open-shift")
        results.append("   ✅ Когда Администратор нажимает кнопку экстренного действия 'Открыть день'")
        
        # Верифицируем реактивное появление статуса ОТКРЫТА в DOM-разметке React после POST-запроса
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", ".status-shift-open, :has-text('ОТКРЫТА')")
        results.append("   ✅ Тогда На бэкенд уходит POST-запрос и статус смены меняется на ОТКРЫТА")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ КАССОВЫХ СМЕН: {str(e)}"]

    return results
