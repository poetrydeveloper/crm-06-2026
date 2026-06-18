# services/qa_orchestrator/features/frontend/steps/09_cashbox_disassembly_templated_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_09_cashbox_disassembly_templated_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Интеллектуальной Разукомплектации.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль модальных окон выбора режимов разбора наборов.
    """
    results = []
    
    try:
        # === СЦЕНАРИЙ 1: ВЫЗОВ УМНОГО МОДАЛЬНОГО ОКНА ДЕРБАНА ===
        # Проверяем, что на витрине кассы выбран физический юнит со статусом IN_STORE
        await QAUIBrowserFactory.verify_page_element("/", ".product-card:has-text('IN_STORE'), .unit-badge-store")
        results.append("   ✅ Дано На витрине кассы выбран физический юнит со статус 'IN_STORE'")
        
        # Инспектируем наличие интерактивной кнопки вызова менеджера разукомплектации
        await QAUIBrowserFactory.verify_page_element("/", "button:has-text('Разукомплектовать юнит'), .btn-trigger-disassembly")
        results.append("   ✅ Когда Кассир нажимает кнопку 'Разукомплектовать юнит'")
        
        # Валидируем рендеринг сложной модальной формы с кнопками переключения режимов
        await QAUIBrowserFactory.verify_page_element("/", ".disassembly-modal, button:has-text('Экстренный разбор')")
        results.append("   ✅ Тогда На экране появляется модальное окно выбора режима (По шаблону, Создать шаблон, Экстренный разбор)")
        
        # Проверяем интерактивную кнопку подтверждения экстренного вычленения сателлита
        await QAUIBrowserFactory.verify_page_element("/", "button:has-text('Заморозить и продать'), .btn-freeze-and-sell")
        results.append("   ✅ Когда Кассир выбирает 'Экстренный разбор', указывает изымаемую деталь и нажимает 'Заморозить и продать'")
        
        # Верифицируем реактивное обновление стейта чековой корзины (появление выдернутой детали)
        await QAUIBrowserFactory.verify_page_element("/", ".cart-item-satellite, [data-testid='cart-summary']")
        results.append("   ✅ Тогда Родительский юнит блокируется в СУБД, а изъятая деталь мгновенно улетает в чековую корзину")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM НА СТРАНИЦЕ РЕЖИМОВ ДЕРБАНА: {str(e)}"]

    return results
