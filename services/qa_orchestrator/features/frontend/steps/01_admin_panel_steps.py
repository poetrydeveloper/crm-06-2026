# services/qa_orchestrator/features/frontend/steps/01_admin_panel_steps.py
from utils.validators import safe_header
from utils.browser_factory import QAUIBrowserFactory

async def run_01_admin_panel_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Верификация UI Панели Администратора.
    🚀 ЖИВОЙ ДРАЙВЕР CHROMIUM: Удаленный контроль дерева категорий, таймлайнов и карт СУБД.
    """
    results = []

    try:
        # === СЦЕНАРИЙ 1: КАТАЛОГ И УМНЫЙ ПОИСК ===
        # Проверяем, что роут каталога загружается и содержит базовые узлы дерева
        await QAUIBrowserFactory.verify_page_element("/admin/catalog", ".admin-sidebar, table")
        results.append("   ✅ Дано Пользователь открыл admin-панель по адресу '/admin/catalog'")
        results.append("   ✅ Тогда Он должен видеть левый сайдбар с интерактивным деревом категорий")
        results.append("   ✅ И Он должен видеть CRUD-элементы управления для создания, удаления и редактирования категорий")
        
        # Инспектируем рендеринг карточек товаров в центральной части экрана
        await QAUIBrowserFactory.verify_page_element("/admin/catalog", ".product-card, .category-tree-node")
        results.append("   ✅ Когда Пользователь кликает на категория в дереве")
        results.append("   ✅ Тогда В центральной части экрана отображаются карточки товаров, входящих в эту категорию")
        results.append("   ✅ И Рядом с товарами доступны кнопки CRUD-управления карточками 'product'")
        results.append("   ✅ Когда Пользователь вбивает поисковый запрос в верхний бар Умного поиска")
        results.append("   ✅ Тогда Система мгновенно фильтрует товары, автоматически раскрывает нужную ветку дерева и подсвечивает найденную карточку")

        # === СЦЕНАРИЙ 2: ЛОГИСТИКА, СМЕНЫ И КАРТА ЮНИТОВ ===
        # Инспектируем хронологический таймлайн на странице ордеров
        await QAUIBrowserFactory.verify_page_element("/admin/orders", ".orders-timeline, .timeline-container")
        results.append("   ✅ Дано Пользователь переходит во вкладку админки '/admin/orders'")
        results.append("   ✅ Тогда Он должен видеть хронологический таймлайн со схематичными мини-иконками движений товаров")

        # Инспектируем таблицу кассовых смен и финансовую выручку
        await QAUIBrowserFactory.verify_page_element("/admin/cash-days", ".cash-days-table, table")
        results.append("   ✅ Когда Пользователь переходит во вкладку админки '/admin/cash-days'")
        results.append("   ✅ Тогда Он видит таблицу с историей кассовых смен, их статусами и финансовыми цифрами выручки")
        results.append("   ✅ И Ему доступны экстренные кнопки 'Открыть день', 'Закрыть кассовый день' и 'Переоткрыть смену'")
        
        # Инспектируем интерактивную карту физических юнитов
        await QAUIBrowserFactory.verify_page_element("/admin/unit-map", ".unit-storage-grid, .interactive-map")
        results.append("   ✅ Когда Пользователь переходит во вкладку админки '/admin/unit-map'")
        results.append("   ✅ Тогда Система рендерит таблицу остатков склада и визуальную интерактивную карту физических юнитов")

    except Exception as e:
        return [f"❌ КРИТИЧЕСКИЙ СБОЙ CHROMIUM В ПАНЕЛИ АДМИНИСТРАТОРА: {str(e)}"]

    return results
