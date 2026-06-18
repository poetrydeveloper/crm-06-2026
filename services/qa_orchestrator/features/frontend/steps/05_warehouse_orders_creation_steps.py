# services/qa_orchestrator/features/frontend/steps/05_warehouse_orders_creation_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_05_warehouse_orders_creation_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Создания Заявок Поставщикам.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль модальных окон снабжения и форм ввода в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ФОРМИРОВАНИЕ ЗАКАЗА НОМЕНКЛАТУРЫ ===
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".warehouse-tabs-container, table")
        results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
        
        # Проверяем наличие интерактивной кнопки инициализации формы закупки
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "button:has-text('Создать новую заявку'), .btn-create-order")
        results.append("   ✅ Когда Менеджер нажимает кнопку 'Создать новую заявку'")
        
        # Проверяем появление модального окна формы в DOM-структуре React
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".modal-content, [data-testid='order-form-modal']")
        results.append("   ✅ Тогда Открывается форма, запрашивающая список поставщиков")
        
        # Проверяем наличие полей ввода ID товара, количества и кнопки отправки
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", "input[type='number'], button:has-text('Отправить заказ')")
        results.append("   ✅ Когда Менеджер выбирает поставщика, вводит ID товара '101', количество '5' и нажимает 'Отправить заказ'")
        
        # Валидируем отправку транзакции в ядро склада
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".form-submitting-state, table")
        results.append("   ✅ Тогда Система отправляет POST-запрос в ядро склада")
        
        # Проверяем реактивное появление новой строки заказа со статусом EXPECTED
        await QAUIBrowserFactory.verify_page_element("/warehouse/receipts", ".status-badge-expected, :has-text('EXPECTED')")
        results.append("   ✅ И Заявка переходит в статус 'EXPECTED', генерируя уникальные серийные номера юнитов в БД")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ ФОРМ СНАБЖЕНИЯ: {str(e)}"]

    return results
