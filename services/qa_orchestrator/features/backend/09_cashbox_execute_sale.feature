# services/qa_orchestrator/features/backend/09_cashbox_execute_sale.feature
@Feature_Context: Cashbox_Execute_Sale_Core
Функционал: Кассовый узел — Стадия 3: Продажа FIFO и автоматическое списание старейшего юнита

  @Scenario_ID: CS-0009-01
  Сценарий: Успешное открытие смены и автоматическое FIFO списание самого старого юнита из СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/days/open", Component: "CashDayManager.open_day" }
    Когда Администратор успешно открывает операционный кассовый день

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/sales", Component: "SalesManager.execute_fifo_sale" }
    И Кассир пробивает розничный чек продажи товара

    @DB_Expect: { Table: "product_units", Where: "is_reserved = true OR logistics_status = 'SOLD'", Expect_Count: 1 }
    Тогда Система возвращает статус 201 и списывает строго самую старую деталь из СУБД по правилу FIFO
