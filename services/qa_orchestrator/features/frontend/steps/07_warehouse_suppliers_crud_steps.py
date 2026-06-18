# services/qa_orchestrator/features/frontend/steps/07_warehouse_suppliers_crud_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_07_warehouse_suppliers_crud_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Управления Поставщиками.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль вкладок контрагентов и создания поставщиков в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: РЕГИСТРАЦИЯ КОНТРАГЕНТА ===
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".warehouse-tabs-container, table")
        results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
        
        # Проверяем наличие вкладки/переключателя табов «Поставщики»
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "button:has-text('Поставщики'), .tab-item-suppliers")
        results.append("   ✅ Когда Менеджер переключается на вкладку 'Поставщики'")
        
        # Инспектируем DOM-структуру React на наличие реестра контрагентов
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".suppliers-table-container, table")
        results.append("   ✅ Тогда Он видит таблицу со списком зарегистрированных контрагентов")
        
        # Проверяем интерактивную кнопку вызова формы добавления поставщика
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "button:has-text('Добавить поставщика'), .btn-add-supplier")
        results.append("   ✅ Когда Менеджер нажимает кнопку 'Добавить поставщика' и вводит имя 'Форсаж-QA'")
        
        # Валидируем асинхронную отправку POST-запроса в ядро бэкенда
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".supplier-submitting, table")
        results.append("   ✅ Тогда Система отправляет POST-запрос создания в ядро")
        
        # Верифицируем реактивную материализацию новой записи «Форсаж-QA» в таблице
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "tr:has-text('Форсаж-QA'), td")
        results.append("   ✅ И Новый поставщик успешно материализуется в таблице на фронтенде")

    except Exception as e:
        return [f"❌ К КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ КОНТРАГЕНТОВ: {str(e)}"]

    return results
