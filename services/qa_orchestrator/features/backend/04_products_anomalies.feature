# services/qa_orchestrator/features/backend/04_products_anomalies.feature
@Feature_Context: Products_Anomalies_Core
Функционал: Контроль карточек товаров, привязанных к резервной категории, и мониторинг аномалий

  @Scenario_ID: PD-0004-01
  Сценарий: Создание товара в резервной категории и автоматическое выявление аномалий номенклатуры в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано В системе создана "резервная_категория" с ID 1, а база данных полностью изолирована

    @Code: { File: "routers/catalog_nodes/products.py", Router_Route: "POST /api/v1/catalog/products", Component: "ProductManager.create_product" }
    Когда Пользователь создает товар "Ключ рожковый" с артикулом "ANOMALY-KEY-4" и category_id равным 1

    @Code: { File: "routers/catalog_nodes/products.py", Router_Route: "GET /api/v1/catalog/products/anomalies", Component: "ProductManager.get_product_anomalies" }
    И Пользователь запрашивает эндпоинт мониторинга аномалий "/api/v1/catalog/products/anomalies"

    @DB_Expect: { Table: "products", Where: "category_id = 1 AND code = 'ANOMALY-KEY-4'", Expect_Count: 1 }
    Тогда Товар успешно создается со статусом 201, а система возвращает этот товар в списке критических предупреждений с флагом has_anomalies = true
