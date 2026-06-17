# services/qa_orchestrator/features/backend/05_warehouse_fifo_units.feature
@Feature_Context: Warehouse_FIFO_Units_Core
Функционал: Логистика закупок и поштучное зарождение FIFO-юнитов (Команда 0001)

  @Scenario_ID: WH-0001-01
  Сценарий: Успешный цикл формирования заявки поставщику с поштучной материализацией в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И В системе созданы тестовый поставщик, бренд, категория и карточка товара для изоляции СУБД

    @Code: { File: "routers/warehouse.py", Router_Route: "POST /api/v1/warehouse/orders", Component: "OrderManager.create_supplier_order" }
    Когда Менеджер отправляет запрос на создание заявки поставщику (Команда 0001):

      | quantity | estimated_purchase_price |
      | 3        | 250.00                   |

    @DB_Expect: { Table: "product_units", Where: "logistics_status = 'IN_REQUEST' AND physical_status = 'EXPECTED'", Expect_Count: 3 }
    Тогда Система возвращает статус 201, рассчитывает финансовую нагрузку 750.00, в таблице "product_units" физически рождаются 3 изолированные записи со статусами IN_REQUEST и EXPECTED

