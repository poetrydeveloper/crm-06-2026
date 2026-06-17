# services/qa_orchestrator/features/frontend/03_warehouse_receipts_view.feature
@Feature_Context: Frontend_Warehouse_Receipts_View_Lightweight_CRM
Функционал: Фронтенд — Отображение открытых заявок на складе

  @Scenario_ID: UI-WH-0003-01
  Сценарий: Просмотр списка active заказов поставщикам
    Дано Пользователь открыл экран логистики по адресу "/warehouse/receipts"
    Тогда Он должен видеть интерактивный список всех незакрытых текущих заявок поставщикам
