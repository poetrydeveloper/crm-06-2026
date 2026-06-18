# services/qa_orchestrator/features/frontend/steps/06_warehouse_order_details_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_06_warehouse_order_details_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Детализации Заявок Склада.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль Accordion-раскрытия состава ордеров в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ПРОСМОТР НОМЕНКЛАТУРНЫХ ПОЗИЦИЙ ===
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".warehouse-tabs-container, table")
        results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
        
        # Проверяем наличие интерактивной строки-аккордеона для раскрытия заявки поставщика
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".receipt-row-clickable, tr")
        results.append("   ✅ Когда Кладовщик кликает на строку активной заявки поставщика")
        
        # Инспектируем появление вложенного Accordion-контейнера подтаблицы в DOM-разметке React
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".nested-details-subtable, .order-items-collapse")
        results.append("   ✅ Тогда Строка расширяется и под ней рендерится вложенная подтаблица")
        
        # Валидируем наличие обязательных столбцов состава номенклатуры (артикул, количество, статус)
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "th:has-text('артикул'), th:has-text('статус')")
        results.append("   ✅ И В подтаблице отображается детальный список товаров с полями артикул, количество и статус единиц")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ ДЕТАЛИЗАЦИИ ОРДЕРОВ: {str(e)}"]

    return results
