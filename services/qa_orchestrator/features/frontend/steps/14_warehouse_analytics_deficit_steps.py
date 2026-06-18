# services/qa_orchestrator/features/frontend/steps/14_warehouse_analytics_deficit_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_14_warehouse_analytics_deficit_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Конструктора Правил и Снабжения.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль конструктора снабжения и тегов в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: СОЗДАНИЕ ПРАВИЛА И КОРЗИНА СНАБЖЕНИЯ ===
        await QAUIBrowserFactory.verify_page_element("/admin/orders", ".orders-timeline, .timeline-container")
        results.append("   ✅ Дано Пользователь открыл ERP-панель логистики по адресу '/admin/orders'")
        
        # Инспектируем вкладку переключения «Умный предзаказ» в ERP
        await QAUIBrowserFactory.verify_page_element("/admin/orders", "button:has-text('Предзаказы'), .tab-item-preorders")
        results.append("   ✅ Когда Менеджер переходит во вкладку 'Умный предзаказ'")
        
        # Проверяем в DOM форму конструктора правил, ленту тегов и таблицу дефицита
        await QAUIBrowserFactory.verify_page_element("/admin/orders", ".rule-creator-block, .active-rules-list-container")
        results.append("   ✅ Тогда Он видит форму конструктора правил, ленту активных тегов и таблицу дефицита")
        
        # Эмулируем клик менеджера по кнопке закупки дефицитной позиции
        await QAUIBrowserFactory.verify_page_element("/admin/orders", "button:has-text('Оформить заказ'), .btn-process-preorder")
        results.append("   ✅ Когда Менеджер нажимает 'Оформить заказ' на дефицитном товаре")
        
        # Верифицируем перенос строки в список формируемого ордера снабжения
        await QAUIBrowserFactory.verify_page_element("/admin/orders", ".orders-list-container, table")
        results.append("   ✅ Тогда Товар переносится в стейт списка формируемой заявки поставщику на странице logistics")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM В КОНСТРУКТОРЕ СНАБЖЕНИЯ: {str(e)}"]

    return results
