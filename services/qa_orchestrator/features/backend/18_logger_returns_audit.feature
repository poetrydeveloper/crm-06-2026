# services/qa_orchestrator/features/backend/18_logger_returns_audit.feature
@Feature_Context: Logger_Returns_Audit_Core
Функционал: Логгер — Аудит истории возвратов брака розничной сети

  @Scenario_ID: LG-0501-01
  Сценарий: Получение выборки кассовых логов операции 0501 для панели директора
    @Trace: { Gateway: "location /api/", Target: "logger_service:8001" }
    Дано В микросервисе логирования crm_logger_service зарегистрированы кассовые события

    @Code: { File: "main.py", Router_Route: "GET /api/v1/logger/audit/0501", Component: "AuditManager.get_logs_by_code" }
    Когда Директор запрашивает историю операций по коду "0501"

    @DB_Expect: { Table: "logger_events", Where: "audit_code = '0501'", Expect_Count: 1 }
    Тогда Логгер возвращает массив записей с серийными номерами и причинами возвратов от клиентов
