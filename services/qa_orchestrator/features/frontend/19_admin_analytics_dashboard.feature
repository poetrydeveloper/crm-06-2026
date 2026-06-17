# services/qa_orchestrator/features/frontend/19_admin_analytics_dashboard.feature
@Feature_Context: Frontend_Admin_Analytics_Dashboard_Lightweight_CRM
Функционал: Фронтенд — Финансовый дашборд и метрики смен директора

  @Scenario_ID: UI-ADM-ANL-0019-01
  Сценарий: Отображение карточек сложной аналитики выручки от crm_analyzer_service
    Дано Администратор открыл панель управления сменами по адресу "/admin/cash-days"
    Когда Страница инициализируется в браузере директора
    Тогда Система отправляет запрос к API аналитического микросервиса /analytics/summary
    И На экране успешно рендерится дашборд с выручкой, конверсией розницы и активными клиентами
