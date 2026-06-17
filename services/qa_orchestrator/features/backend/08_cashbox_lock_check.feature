# services/qa_orchestrator/features/backend/08_cashbox_lock_check.feature
@Feature_Context: Cashbox_Lock_Check_Core
Функционал: Кассовый узел — Стадия 2: Защита смены и блокировка чеков

  @Scenario_ID: CS-0008-01
  Сценарий: Блокировка проведения чеков при неоткрытом кассовом дне в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/sales", Component: "SalesManager.execute_fifo_sale" }
    Когда Кассир пытается пробить чек продажи при неоткрытом кассовом дне

    @DB_Expect: { Table: "cash_days", Where: "is_closed = false", Expect_Count: 0 }
    Тогда Система блокирует операцию и возвращает статус 400 с описанием ошибки смены
