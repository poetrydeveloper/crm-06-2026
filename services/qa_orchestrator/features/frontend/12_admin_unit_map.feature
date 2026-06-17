# services/qa_orchestrator/features/frontend/12_admin_unit_map.feature
@Feature_Context: Frontend_Admin_Unit_Map_Lightweight_CRM
Функционал: Фронтенд — Карта поштучного учета физических юнитов

  @Scenario_ID: UI-ADM-MAP-0012-01
  Сценарий: Аудит физических экземпляров товара на балансе магазина
    Дано Пользователь открыл экран аудита юнитов по адресу "/admin/unit-map"
    Тогда Система запрашивает массив сырых данных СУБД product_units
    И Отображает интерактивную таблицу поштучного учета с серийными номерами и физическими статусами единиц
