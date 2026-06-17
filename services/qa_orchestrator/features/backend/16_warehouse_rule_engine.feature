# services/qa_orchestrator/features/backend/16_warehouse_rule_engine.feature
@Feature_Context: Warehouse_Rule_Engine_Core
Функционал: Бэкенд — Валидация RuleEngine API и фильтрации СУБД

  @Scenario_ID: WH-RULE-01
  Сценарий: Проверка добавления динамических тегов правил и занесения товаров в исключения
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано В базе данных ядра склада присутствует стерильная номенклатура товаров

    @Code: { File: "routers/warehouse_nodes/rules.py", Router_Route: "POST /api/v1/warehouse/purchase-rules", Component: "RuleEngine.add_rule" }
    Когда Администратор шлет POST на /warehouse/purchase-rules с тегами условий стоимости и названий
    Тогда Бэкенд сохраняет правило, а повторный GET на /warehouse/purchase-rules выдает дефицит по новой матрице

    @Code: { File: "routers/warehouse_nodes/pre_orders.py", Router_Route: "POST /api/v1/warehouse/pre-orders/exclude", Component: "AnalyzerCacheManager.add_to_blacklist" }
    Когда Администратор шлет POST на /warehouse/pre-orders/exclude для конкретного product_id
    Тогда Данный товар полностью исключается из аналитического буфера закупок
