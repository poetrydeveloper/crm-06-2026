# services/qa_orchestrator/features/backend/11_cashbox_smart_search.feature
@Feature_Context: Cashbox_Smart_Search_Core
Функционал: Кассовый узел — Стадия 6: Умный поиск и динамический контроль остатков номенклатуры

  @Scenario_ID: CS-0011-01
  Сценарий: Поиск товара на кассе на лету по фрагментам слов и пересчет available_qty при FIFO-продаже
    @Trace: { Gateway: "location /api/", Target: "backend:8000" }
    Дано Бэкенд Core доступен по адресу "/api/v1"
    И В каталоге есть товар "Ключ рожковый 10мм Toptul" с 3 штуками в статусе "IN_STORE" на стерильной базе

    @Code: { File: "routers/catalog_nodes/search.py", Router_Route: "GET /api/v1/catalog/products/search", Component: "SearchEngine.query_search" }
    Когда Кассир вводит в поиске строку "рожков 10мм"
    Тогда Система мгновенно находит этот товар и показывает доступный остаток: 3

    @Code: { File: "routers/cash.py", Router_Route: "POST /api/v1/cash/sales", Component: "SalesManager.execute_fifo_sale" }
    Когда Кассир пробивает 1 единицу этого товара через кассу

    @Code: { File: "routers/catalog_nodes/search.py", Router_Route: "GET /api/v1/catalog/products/search", Component: "SearchEngine.query_search" }
    Тогда При повторном поиске система показывает доступный остаток этого товара: 2
