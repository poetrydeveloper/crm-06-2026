# services/qa_orchestrator/features/backend/14_warehouse_disassembly_partial.feature
@Feature_Context: Warehouse_Disassembly_Partial_Core
Функционал: Складской учет — Стадия 9: Экстренный частичный дербан набора и заморозка остатков

  @Scenario_ID: WH-0103-01
  Сценарий: Частичный дербан набора без шаблона и автоматическая заморозка недокомплекта в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И На складе существует 1 юнит товара "Набор инструментов Jonnesway" в статусе "IN_STORE"

    @Code: { File: "routers/warehouse_nodes/operations.py", Router_Route: "POST /api/v1/warehouse/disassembly/partial", Component: "DisassemblyManager.execute_partial_disassembly" }
    Когда Менеджер отправляет запрос на экстренный частичный разбор набора без шаблона

    @DB_Expect: { Table: "product_units", Where: "physical_status = 'FROZEN_INCOMPLETE'", Expect_Count: 1 }
    Тогда Из набора выделяется 1 проданный сателлит со статусом "SOLD"
    И Сам родительский набор меняет физический статус на "FROZEN_INCOMPLETE" и блокируется для продаж
