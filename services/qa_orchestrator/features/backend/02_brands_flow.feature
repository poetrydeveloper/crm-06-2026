# services/qa_orchestrator/features/backend/02_brands_flow.feature
@Feature_Context: Brands_Management_Core
Функционал: Управление брендами с трансформацией имен в snake_case и защитой связей

  @Scenario_ID: BR-0002-01
  Сценарий: Успешное создание и валидация snake_case имени бренда в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"

    @Code: { File: "routers/catalog_nodes/brands.py", Router_Route: "POST /api/v1/catalog/brands", Component: "BrandManager.create_brand" }
    Когда Пользователь создает бренд с именем "Форсаж Инструмент"

    @DB_Expect: { Table: "brands", Where: "name = 'форсаж_инструмент'", Expect_Count: 1 }
    Тогда Система должна вернуть статус 201 и в таблице "brands" имя должно быть записано как "форсаж_инструмент"

  @Scenario_ID: BR-0002-02
  Сценарий: Запрет удаления бренда при наличии привязанных к нему товаров
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано В системе существует бренд "toptul" и привязанный к нему товар "КЛ-10"

    @Code: { File: "routers/catalog_nodes/brands.py", Router_Route: "DELETE /api/v1/catalog/brands/{id}", Component: "BrandManager.delete_brand" }
    Когда Пользователь отправляет запрос на удаление бренда "toptul"

    @DB_Expect: { Table: "brands", Where: "name = 'toptul'", Expect_Count: 1 }
    Тогда Система должна вернуть ошибку 400 с описанием "Нельзя удалить бренд, к которому привязаны товары"
