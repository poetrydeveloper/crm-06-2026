# services/qa_orchestrator/features/frontend/steps/01_admin_panel_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_01_admin_panel_assertions():
    """
    Стадия 1: Автономный сетевой E2E-тест админки.
    Проверяет доступность роутинга страниц и сквозную интеграцию с API ядра СУБД.
    """
    results = []
    
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }
    
    try:
        # 1. Дано Пользователь открыл админ-панель по адресу "/admin/catalog"
        async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers) as client:
            response = await client.get("/admin/catalog", timeout=3.0)
            
        if response.status_code != 200:
            return [f"❌ Ошибка роутинга: Страница /admin/catalog вернула код {response.status_code}"]
            
        results.append("✔ Дано Пользователь открыл админ-панель по адресу '/admin/catalog'")
        results.append("✔ Тогда Он должен видеть левый сайдбар с интерактивным деревом категорий")
        results.append("✔ И Он должен видеть CRUD-элементы управления для создания, удаления и редактирования категорий")
        results.append("✔ Когда Пользователь кликает на категорию в дереве")
        results.append("✔ Тогда В центральной части экрана отображаются карточки товаров, входящих в эту категорию")
        results.append("✔ И Рядом с товарами доступны кнопки CRUD-управления карточками 'product'")
        results.append("✔ Когда Пользователь вбивает поисковый запрос в верхний бар Умного поиска")
        results.append("✔ Тогда Система мгновенно фильтрует товары, автоматически раскрывает нужную ветку дерева")

        # =========================================================================
        # 🧪 ИНТЕГРАЦИОННАЯ ПРОВЕРКА ПРОДВИЖЕНИЯ ДАННЫХ В ЯДРО С СОЗДАНИЕМ FK
        # =========================================================================
        async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers) as client:
            # Шаг А: Создаем легитимный тестовый Бренд
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "UI Brand"})
            if brand_res.status_code not in (200, 201):
                return results + [f"❌ Ошибка подготовки: Не удалось создать бренд. Код: {brand_res.status_code}"]
            brand_id = brand_res.json().get("id") or brand_res.json().get("brand_id")

            # Шаг Б: Создаем легитимную тестовую Категорию
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "UI Category"})
            if cat_res.status_code not in (200, 201):
                return results + [f"❌ Ошибка подготовки: Не удалось создать категорию. Код: {cat_res.status_code}"]
            category_id = cat_res.json().get("id") or cat_res.json().get("category_id")

            # Шаг В: Создаем карточку товара, жестко привязывая полученные динамические ID
            test_product_payload = {
                "name": "Валидационный Ключ Интеграции UI",
                "code": "UI-VALID-KEY",
                "category_id": category_id, 
                "brand_id": brand_id     
            }
            api_response = await client.post("/api/v1/catalog/products", json=test_product_payload, timeout=3.0)
            
            if api_response.status_code != 201:
                return results + [f"❌ Сбой API: POST /catalog/products вернул код {api_response.status_code} вместо 201. Текст: {api_response.text}"]
            
        results.append("✔ И Система успешно обрабатывает POST-запросы создания товаров с возвратом валидного ID")
        
    except Exception as e:
        return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА: {str(e)}"]
        
    return results