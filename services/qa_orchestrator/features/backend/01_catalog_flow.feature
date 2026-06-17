# services/qa_orchestrator/features/backend/01_catalog_flow.feature
@Feature_Context: Catalog_Tags_Generation_Core
Функционал: Наполнение каталога и автогенерация умных JSONB-тегов

  @Scenario_ID: CT-0001-01
  Сценарий: Успешный цикл добавления товара с автоматической очисткой тегов от стоп-слов
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен через шлюз Nginx

    @Code: { File: "routers/warehouse.py", Router_Route: "POST /api/v1/warehouse/suppliers", Component: "SupplierManager.create_supplier" }
    Когда Пользователь создает поставщика с именем "QA_Форсаж_Тест"

    @Code: { File: "routers/catalog.py", Router_Route: "POST /api/v1/catalog/products", Component: "ProductManager.create_product" }
    И Пользователь отправляет запрос на создание товара с именем "Ключ рожковый 10мм Toptul" и артикулом "QA-КЛ-10"

    @DB_Expect: { Table: "products", Where: "code = 'QA-КЛ-10'", Jsonb_Contains: ["ключ", "рожковый", "10мм", "qa-кл-10"], Jsonb_Excludes: ["и"] }
    Тогда Система возвращает статус 201, в СУБД рождается запись товара, а в JSONB-массиве тегов присутствуют ключевые слова и отсутствуют стоп-слова
