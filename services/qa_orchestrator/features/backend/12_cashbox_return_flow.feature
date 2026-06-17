# services/qa_orchestrator/features/backend/12_cashbox_return_flow.feature
@Feature_Context: Cashbox_Return_Flow_Core
Функционал: Кассовый узел — Стадия 7: Интеллектуальный возврат штучного товара и корректировка остатков

  @Scenario_ID: CS-0012-01
  Сценарий: Успешный возврат проданного юнита по серийному номеру и корректировка доступных остатков в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И В системе открыт кассовый день и продан 1 юнит товара со статусом "SOLD"

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/returns", Component: "ReturnManager.execute_return" }
    Когда Клиент возвращает этот товар по его уникальному серийному номеру через API

    @DB_Expect: { Table: "product_units", Where: "physical_status = 'IN_STORE' AND logistics_status = 'RECEIVED'", Expect_Count: 1 }
    Тогда Система переводит физический статус юнита обратно в "IN_STORE"
    И При повторном умном поиске этот товар снова отображается как доступный к продаже
