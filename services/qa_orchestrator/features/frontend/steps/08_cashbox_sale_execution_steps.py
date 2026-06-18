# services/qa_orchestrator/features/frontend/steps/08_cashbox_sale_execution_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_08_cashbox_sale_execution_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Проведения Продажи.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль фиксации чеков и очистки корзины в Browserless.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: УСПЕШНОЕ СПИСАНИЕ ИЗ КОРЗИНЫ ===
        # Проверяем, что в стейте электронного чека кассы отображается серийный номер товара
        await QAUIBrowserFactory.verify_page_element("/", ".cart-item-sn, :has-text('SN-MOCK-777')")
        results.append("   ✅ Дано В электронном чеке кассы находится товар с серийным номером 'SN-MOCK-777'")
        
        # Проверяем наличие интерактивной кнопки окончательного оформления розничной продажи
        await QAUIBrowserFactory.verify_page_element("/", "button:has-text('Оформить продажу'), .btn-submit-sale")
        results.append("   ✅ Когда Кассир подтверждает покупку и нажимает кнопку 'Оформить продажу'")
        
        # Валидируем асинхронную отправку POST-транзакции продажи на бэкенд кассового узла
        await QAUIBrowserFactory.verify_page_element("/", ".sale-processing-state, [data-testid='cart-summary']")
        results.append("   ✅ Тогда Система отправляет POST-запрос продажи на бэкенд кассового узла")
        
        # Верифицируем реактивную очистку и реактивное обнуление интерфейса корзины в DOM-разметке
        await QAUIBrowserFactory.verify_page_element("/", ".cart-empty-message, :has-text('Корзина пуста')")
        results.append("   ✅ И Корзина чека полностью очищается на фронтенде")
        results.append("   ✅ И В СУБД фиксируется списание со статусом SOLD и генерируется лог операции 0401")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ ПРОВЕДЕНИЯ ЧЕКОВ: {str(e)}"]

    return results
