# services/qa_orchestrator/features/backend/17_analyzer_deficit_cron.feature
@Feature_Context: Analyzer_Deficit_Cron_Core
Функционал: Аналитика — Фоновый расчет дефицита микросервисом crm_analyzer_service

  @Scenario_ID: AN-0017-01
  Сценарий: Проверка автономного сбора остатков и кэширования листа предзаказов в буфере склада
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Микросервис аналитики crm_analyzer_service запущен и доступен по сети

    @Code: { File: "routers/warehouse_nodes/pre_orders.py", Router_Route: "POST /api/v1/warehouse/pre-orders/cache-update", Component: "AnalyzerCacheManager.update_cache_payload" }
    Когда Анализатор инициирует регламентный расчет матрицы снабжения

    @DB_Expect: { Table: "pre_orders_cache", Message: "Кэш дефицита обновлен" }
    Тогда Он успешно считывает сырые остатки ядра и передает сгенерированный кэш предзаказов в буфер склада
