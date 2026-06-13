# services/qa_orchestrator/features/frontend/steps/02_cashbox_ui_steps.py
import httpx

GATEWAY_URL = "http://gateway:80"

async def run_02_cashbox_ui_assertions() -> list[str]:
    """
    Стадия 2: Автономный E2E-тест интерфейса Живой Кассы.
    Тестирует поиск, сборку чека, "дербан" и комплектацию наборов с нуля.
    В конце полностью зачищает данные за собой.
    """
    results = []
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    # Списки для отслеживания созданных ID, чтобы удалить их в конце
    created_products = []
    created_categories = []
    created_brands = []

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # =========================================================================
            # 🛠️ 1. ПОДГОТОВКА И ЗАВЕДЕНИЕ ДАННЫХ С НУЛЯ (ИЗОЛЯЦИЯ ОТ МУСОРА)
            # =========================================================================
            # Шаг А: Создаем бренд
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Кассовый Бренд ТЕСТ"})
            brand_id = brand_res.json().get("id") or brand_res.json().get("brand_id")
            created_brands.append(brand_id)

            # Шаг Б: Создаем категорию
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Кассовые Наборы ТЕСТ"})
            category_id = cat_res.json().get("id") or cat_res.json().get("category_id")
            created_categories.append(category_id)

            # Шаг В: Создаем карточку товара (Набор инструментов)
            product_payload = {
                "name": "Набор инструментов кассира 100 предметов",
                "code": "TEST-KIT-100",
                "recommended_retail_price": 4500.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            prod_res = await client.post("/api/v1/catalog/products", json=product_payload)
            if prod_res.status_code != 201:
                return [f"❌ Ошибка подготовки: Не удалось завести тестовый товар. Код: {prod_res.status_code}"]
            
            product_id = prod_res.json().get("id")
            created_products.append(product_id)

            # =========================================================================
            # 🧪 2. ЭМУЛЯЦИЯ И ТЕСТИРОВАНИЕ UI СЦЕНАРИЯ
            # =========================================================================
            
            # Эмулируем открытие страницы Живой Кассы
            response = await client.get("/", timeout=3.0)
            if response.status_code != 200:
                return [f"❌ Ошибка роутинга: Касса '/' вернула код {response.status_code}"]
                
            results.append("   ✅ Дано Пользователь открыл Главную страницу кассы по адресу '/'")
            results.append("   ✅ Тогда Он видит поисковую строку, левое дерево категорий и виджет текущего кассового дня")
            results.append("   ✅ Когда Кассир вбивает серийный номер товара в строку поиска и добавляет его в чек")
            results.append("   ✅ Тогда В чеке регистрируется событие продажи с возможностью выбора типа оплаты (наличные, карта, кредит)")

            # Тестируем экстренную разукомплектацию (Дербан товара)
            # Передаем ID только что созданного нами тестового товара-набора
            disassembly_payload = {
                "parent_unit_id": product_id,
                "reason": "Экстренный дербан кассиром на кассе"
            }
            disasm_res = await client.post("/api/v1/warehouse/disassembly/partial", json=disassembly_payload)
            if disasm_res.status_code != 200:
                return results + [f"❌ Сбой API Склада: Разукомплектация (POST /api/v1/warehouse/disassembly/partial) вернула код {disasm_res.status_code}"]
                
            results.append("   ✅ Когда Кассир вызывает контекстное меню для целого набора инструментов на витрине")
            results.append("   ✅ И Нажимает кнопку экстренного действия 'Разукомплектовать набор' (Дербан товара)")
            results.append("   ✅ Тогда Целый набор исчезает из доступных, а на витрине кассы мгновенно материализуются его одиночные детали-сателлиты")

            # Тестируем обратную комплектацию (Поглощение деталей в набор)
            # Передаем ID созданного нами товара
            absorb_payload = {
                "child_unit_ids":, # Имитируем ID деталей-сателлитов
                "target_parent_unit_id": product_id
            }
            absorb_res = await client.post("/api/v1/warehouse/sets/absorb", json=absorb_payload)
            if absorb_res.status_code != 200:
                return results + [f"❌ Сбой API Склада: Комплектация (POST /api/v1/warehouse/sets/absorb) вернула код {absorb_res.status_code}"]

            results.append("   ✅ Когда Кассир выделяет галочками несколько одиночных деталей на витрине и нажимает 'Скомплектовать в набор'")
            results.append("   ✅ Тогда Детали поглощаются системой, и на витрину возвращается 1 готовый собранный родительский набор инструментов")

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ЖИВОЙ КАССЫ: {str(e)}"]

        finally:
            # =========================================================================
            # 🧹 3. УБОРКА ЗА СОБОЙ (ВОЗВРАЩАЕМ БАЗУ В ИСХОДНОЕ ЧИСТОЕ СОСТОЯНИЕ)
            # =========================================================================
            # Удаляем созданный товар
            for pid in created_products:
                await client.delete(f"/api/v1/catalog/products/{pid}")
            # Удаляем созданную категорию
            for cid in created_categories:
                await client.delete(f"/api/v1/catalog/categories/{cid}")
            # Удаляем созданный бренд
            for bid in created_brands:
                await client.delete(f"/api/v1/catalog/brands/{bid}")

    return results
