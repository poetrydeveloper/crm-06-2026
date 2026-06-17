# services/qa_orchestrator/features/backend/10_cashbox_reopen_flow.feature
@Feature_Context: Cashbox_Reopen_Flow_Core
Функционал: Кассовый узел — Стадия 4: Переоткрытие смены и дозапись чеков

  @Scenario_ID: CS-0010-01
  Сценарий: Успешный перевод архивного операционного дня в статус активного и проведение дозаписи продаж
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/days/{cash_day_id}/reopen", Component: "CashDayManager.reopen_day" }
    Когда Администратор успешно переоткрывает архивный кассовый день

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/sales", Component: "SalesManager.execute_fifo_sale" }
    Тогда Система разрешает проведение операций
    И Новый чек успешно дозаписывается в СУБД
