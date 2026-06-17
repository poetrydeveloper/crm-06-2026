# services/qa_orchestrator/features/backend/06_warehouse_receipt.feature
@Feature_Context: Warehouse_Receipt_Core
Функционал: Фактическая приемка накладных и выставление товара на полку розничной сети (Команда 0101)

  @Scenario_ID: WS-0101-01
  Сценарий: Успешный перевод зарожденных юнитов на полку магазина с фиксацией в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И В системе создана заявка поставщику с зарожденными юнитами в статусе "IN_REQUEST" и "EXPECTED"

    @Code: { File: "routers/warehouse_nodes/operations.py", Router_Route: "POST /api/v1/warehouse/receipts", Component: "ReceiptManager.process_receipt" }
    Когда Менеджер отправляет запрос на фактическую приемку (Команда 0101) с фиксацией реальной цены закупки

    @DB_Expect: { Table: "product_units", Where: "logistics_status = 'RECEIVED' AND physical_status = 'IN_STORE'", Expect_Count: 3 }
    Тогда Система возвращает статус 200 OK
    И У этих юнитов logistics_status меняется на "RECEIVED"
    И Физический статус меняется на "IN_STORE"
