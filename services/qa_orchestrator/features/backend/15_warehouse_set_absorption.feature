# services/qa_orchestrator/features/backend/15_warehouse_set_absorption.feature
@Feature_Context: Warehouse_Set_Absorption_Core
Функционал: Складской учет — Стадия 15: Обратная сборка и поглощение сателлитов в набор

  @Scenario_ID: WH-0302-01
  Сценарий: Успешная комплектация целого набора инструментов из одиночных деталей-сателлитов (Команда 0302)
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу через шлюз Nginx
    И На складе лежат 2 отдельные детали в статусе "IN_STORE"
    И В системе зарегистрирован шаблон сборки, в который входят данные детали

    @Code: { File: "routers/warehouse_nodes/operations.py", Router_Route: "POST /api/v1/warehouse/sets/absorb", Component: "AbsorptionManager.execute_set_absorption" }
    Когда Кладовщик отправляет запрос на комплектацию целого набора из этих физических юнитов

    @DB_Expect: { Table: "product_units", Where: "physical_status = 'ABSORBED' AND parent_unit_id IS NOT NULL", Expect_Count: 2 }
    Тогда Физический статус одиночных сателлитов меняется в СУБД на "ABSORBED"
    И Они блокируются для независимой розничной продажи на кассе
    И На баланс склада автоматически генерируется 1 новый родительский юнит набора в статусе "IN_STORE"
    И У поглощенных сателлитов поле parent_unit_id жестко привязывается к ID созданного набора
