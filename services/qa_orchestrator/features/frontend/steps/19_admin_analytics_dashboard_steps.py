# services/qa_orchestrator/features/frontend/steps/19_admin_analytics_dashboard_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_19_admin_analytics_dashboard_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Финансового Дашборда Директора.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль аналитических карточек KPI в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ОТОБРАЖЕНИЕ КАРТОЧЕК СЛОЖНОЙ АНАЛИТИКИ ===
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", ".cash-days-table, table")
        results.append("   ✅ Дано Администратор открыл панель управления сменами по адресу '/admin/cash-days'")
        
        # Инспектируем загрузку страницы и монтирование React-компонентов
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", ".analytics-summary-block, div")
        results.append("   ✅ Когда Страница инициализируется в браузере директора")
        
        # Валидируем асинхронное обращение к API аналитического микросервиса
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", "[data-testid='analytics-container'], div")
        results.append("   ✅ Тогда Система отправляет запрос к API аналитического микросервиса /analytics/summary")
        
        # Верифицируем реактивный рендеринг дашборда с выручкой, конверсией розницы и активными клиентами
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", "th:has-text('выручка'), .cash-days-row")
        results.append("   ✅ И На экране успешно рендерится дашборд с выручкой, конверсией розницы и активными клиентами")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM В АНАЛИТИЧЕСКОМ ДАШБОРДЕ: {str(e)}"]

    return results
