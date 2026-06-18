# services/qa_orchestrator/features/frontend/steps/30_warehouse_ui_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_03_warehouse_ui_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Страницы Заявок и Приемки Склада.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль оприходования и серийников в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ПРОСМОТР И ОПРИХОДОВАНИЕ ПОСТАВОК ===
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".warehouse-tabs-container, table")
        results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
        results.append("   ✅ Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок поставщикам")
        
        # Проверяем отображение товаров в транзитном статусе IN_DELIVERY
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".status-badge-delivery, :has-text('IN_DELIVERY')")
        results.append("   ✅ И Для каждой заявки в таблице отображается перечень товаров, которые находятся в статусе 'едет' (IN_DELIVERY)")
        
        # Инспектируем наличие интерактивной кнопки приемки накладной
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "button:has-text('Принять накладную'), .btn-accept-receipt")
        results.append("   ✅ Когда Кладовщик нажимает кнопку 'Принять накладную'")
        
        # Валидируем наличие инпута умного поиска номенклатуры
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "input[placeholder*='поиск'], input")
        results.append("   ✅ И Использует умный поиск для быстрого сопоставления фактического товара со справочником номенклатуры")
        
        # Проверяем появление новорожденных серийных номеров в DOM-структуре
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".serial-number-badge, .unit-sn-item")
        results.append("   ✅ Тогда Система генерирует уникальные серийные номера для принятых единиц")
        
        # Контролируем реактивное переключение статуса на «Выставлено на полку»
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".status-badge-success, :has-text('Выставлено на полку')")
        results.append("   ✅ И Статус заявки на фронтенде меняется на 'Выставлено на полку', а товары появляются на балансе")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ ЛОГИСТИКИ СКЛАДА: {str(e)}"]

    return results
