# services/qa_orchestrator/features/backend/13_warehouse_disassembly_templated.feature
@Feature_Context: Warehouse_Disassembly_Templated_Core
Функционал: Складской учет — Стадия 8: Шаблонная разукомплектация наборов инструментов на сателлиты

  @Scenario_ID: WH-0102-01
  Сценарий: Успешный разбор целого набора инструментов по шаблону на сателлиты с фиксацией в СУБД
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И В системе зарегистрирован жесткий шаблон разбора набора инструментов на 2 сателлита

    @Code: { File: "routers/warehouse_nodes/operations.py", Router_Route: "POST /api/v1/warehouse/disassembly/templated", Component: "DisassemblyManager.execute_templated_disassembly" }
    Когда Кладовщик отправляет запрос на разукомплектацию этого конкретного юнита по шаблону

    @DB_Expect: { Table: "product_units", Where: "physical_status = 'IN_STORE' AND parent_unit_id IS NOT NULL", Expect_Count: 2 }
    Тогда Юнит набора списывается со склада со статусом "IN_DISASSEMBLED"
    И На баланс склада автоматически генерируются 2 новых юнита-сателлита с уникальными серийными номерами в статусе "IN_STORE"
