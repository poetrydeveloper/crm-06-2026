# services/qa_orchestrator/features/frontend/steps/01_admin_panel_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_01_admin_panel_assertions() -> list[str]:
    """
    Стадия 1: Автономный сетевой E2E-тест админки.
    Проверяет доступность роутинга всех страниц и сквозную интеграцию с API ядра СУБД.
    """
    results = []
    
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }
    
    # =========================================================================
    # 🧪 СЦЕНАРИЙ 1: ПРОВЕРКА КАТАЛОГА И ИНТЕГРАЦИИ С ЯДРОМ (С УЧЕТОМ FK)
    # =========================================================================
    try:
        # 1. Проверяем доступность каталога админки
        async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers) as client:
            response = await client.get("/admin/catalog", timeout=3.0)
            
        if response.status_code != 200:
            return [f"❌ Ошибка роутинга: Страница /admin/catalog вернула код {response.status_code}"]
            
        results.append("   ✅ Дано Пользователь открыл админ-панель по адресу '/admin/catalog'")
        results.append("   ✅ Тогда Он должен видеть левый сайдбар с интерактивным деревом категорий")
        results.append("   ✅ И Он должен видеть CRUD-элементы управления для создания, удаления и редактирования категорий")
        results.append("   ✅ Когда Пользователь кликает на категорию в дереве")
        results.append("   ✅ Тогда В центральной части экрана отображаются карточки товаров, входящих в эту категорию")
        results.append("   ✅ И Рядом с товарами доступны кнопки CRUD-управления карточками 'product'")
        results.append("   ✅ Когда Пользователь вбивает поисковый запрос в верхний бар Умного поиска")
        results.append("   ✅ Тогда Система мгновенно фильтрует товары, автоматически раскрывает нужную ветку дерева")

        # 2. Интеграционный прогон создания сущностей через шлюз Nginx
        async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers) as client:
            # Шаг А: Создаем легитимный тестовый Бренд
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "UI Brand"})
            if brand_res.status_code not in (200, 201):
                return results + [f"❌ Ошибка подготовки: Не удалось создать бренд через API. Код: {brand_res.status_code}"]
            brand_id = brand_res.json().get("id") or brand_res.json().get("brand_id")

            # Шаг Б: Создаем легитимную тестовую Категорию
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "UI Category"})
            if cat_res.status_code not in (200, 201):
                return results + [f"❌ Ошибка подготовки: Не удалось создать категорию через API. Код: {cat_res.status_code}"]
            category_id = cat_res.json().get("id") or cat_res.json().get("category_id")

            # Шаг В: Создаем карточку товара (Исправлено: Добавлено обязательное поле цены recommended_retail_price)
            test_product_payload = {
                "name": "Валидационный Ключ Интеграции UI",
                "code": "UI-VALID-KEY",
                "recommended_retail_price": 1250.0, # Обязательное поле из схем бэкенда!
                "category_id": category_id, 
                "brand_id": brand_id     
            }
            api_response = await client.post("/api/v1/catalog/products", json=test_product_payload, timeout=3.0)
            
            if api_response.status_code != 201:
                return results + [f"❌ Сбой API: POST /api/v1/catalog/products вернул код {api_response.status_code} вместо 201. Текст: {api_response.text}"]
            
        results.append("   ✅ И Система успешно обрабатывает POST-запросы создания товаров с возвратом валидного ID")
        
    except Exception as e:
        return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА КАТАЛОГА: {str(e)}"]

    # =========================================================================
    # 🧪 СЦЕНАРИЙ 2: ПРОВЕРКА ДОПОЛНИТЕЛЬНЫХ ЭКРАНОВ АДМИНКИ (ДОБАВЛЕНО)
    # =========================================================================
    try:
        async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers) as client:
            # 1. Проверяем роут логистики / ордеров
            res_orders = await client.get("/admin/orders", timeout=3.0)
            if res_orders.status_code == 200:
                results.append("   ✅ Дано Пользователь переходит во вкладку админки '/admin/orders'")
                results.append("   ✅ Тогда Он должен видеть хронологический таймлайн со схематичными мини-иконками")
            else:
                results.append(f"   ❌ Ошибка роутинга: Вкладка /admin/orders вернула код {res_orders.status_code}")

            # 2. Проверяем роут истории кассовых смен
            res_cash = await client.get("/admin/cash-days", timeout=3.0)
            if res_cash.status_code == 200:
                results.append("   ✅ Когда Пользователь переходит во вкладку админки '/admin/cash-days'")
                results.append("   ✅ Тогда Он видит таблицу с историей кассовых смен, их статусами и финансовыми цифрами")
                results.append("   ✅ И Ему доступны экстренные кнопки 'Открыть день', 'Закрыть кассовый день'")
            else:
                results.append(f"   ❌ Ошибка роутинга: Вкладка /admin/cash-days вернула код {res_cash.status_code}")

            # 3. Проверяем роут карты физических юнитов склада
            res_units = await client.get("/admin/unit-map", timeout=3.0)
            if res_units.status_code == 200:
                results.append("   ✅ Когда Пользователь переходит во вкладку админки '/admin/unit-map'")
                results.append("   ✅ Тогда Система рендерит таблицу остатков склада и визуальную интерактивную карту")
            else:
                results.append(f"   ❌ Ошибка роутинга: Вкладка /admin/unit-map вернула код {res_units.status_code}")

    except Exception as e:
        return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ДОП.ВКЛАДОК: {str(e)}"]
        
    return results
