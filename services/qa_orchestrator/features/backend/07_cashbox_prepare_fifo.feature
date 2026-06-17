# services/qa_orchestrator/features/backend/07_cashbox_prepare_fifo.feature
@Feature_Context: Cashbox_Prepare_FIFO_Core
Функционал: Кассовый узел — Стадия 1: Подготовка остатков и материализация FIFO-слоя

  @Scenario_ID: CS-0007-01
  Сценарий: Рождение и материализация двух FIFO юнитов на полке магазина с разным временем в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"

    @Code: { File: "routers/warehouse.py", Router_Route: "POST /api/v1/warehouse/receipts", Component: "ReceiptManager.process_receipt" }
    Когда В системе генерируются две физические единицы товара с разным временем создания

    @DB_Expect: { Table: "product_units", Where: "physical_status = 'IN_STORE'", Expect_Count: 2 }
    Тогда Обе записи успешно сохраняются в СУБД в статусе IN_STORE

