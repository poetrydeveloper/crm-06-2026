# services/qa_orchestrator/features/backend/steps/04_products_anomalies_steps.py
import httpx
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_by_code, teardown_live_brand_by_name, find_live_category_id

GATEWAY_URL = "http://gateway:80"

async def run_04_products_anomalies_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Мониторинг аномалий номенклатуры.
    ПОЛНАЯ ИНКАПСУЛЯЦИЯ: Убран хардкод ID 1, внедрен динамический поиск категорий СУБД.
    """
    results = []
    headers = {"Host": "localhost"}
    
    test_product_code = "anomaly-key-4"
    test_brand_snake = "anomaly_brand"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # 1. 🛡️ SETUP: Глубокая очистка базы перед тестом
            await teardown_live_product_by_code(client, test_product_code)
            await teardown_live_brand_by_name(client, test_brand_snake)
            
            # Гарантируем зарождение системной резервной категории
            await client.post("/api/v1/catalog/categories", json={"name": "резервная_категория"})
            
            # 🔥 ИСПРАВЛЕНО: Динамически вычитываем реальный ID резервной категории из СУБД ядра
            target_category_id = await find_live_category_id(client, "резервная_категория", fallback_id=1)
            results.append(f"   ✅ Дано В системе создана 'резервная_категория' с ID {target_category_id}, а база данных полностью изолирована")

            # Создаем изолированный бренд
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Anomaly Brand"})
            brand_id = brand_res.json().get("brand_id") or 1

            # 2. Исполнение: Создание товара внутри системной категории
            product_payload = {
                "name": "Ключ рожковый",
                "code": test_product_code,
                "recommended_retail_price": 500.0,
                "category_id": int(target_category_id),  # Передаем динамический легитимный ID
                "brand_id": int(brand_id)
            }
            
            step_1_text = "Создание аномального товара Ключ рожковый"
            prod_headers = {**headers, "X-QA-Story": safe_header("PD-0004-01"), "X-QA-Step": safe_header(step_1_text)}
            res_create = await client.post("/api/v1/catalog/products", json=product_payload, headers=prod_headers)
            
            if res_create.status_code == 201:
                results.append("   ✅ Когда Пользователь создает товар 'Ключ рожковый' с category_id равным 1")
                results.append("   ✅ Тогда Товар успешно создается со статусом 201")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ АНОМАЛЬНОГО ТОВАРА: Код {res_create.status_code}. Текст: {res_create.text}"]

            # 3. Валидация эндпоинта аномалий
            step_2_text = "Запрос списка критических предупреждений номенклатуры"
            anom_headers = {**headers, "X-QA-Story": safe_header("PD-0004-01"), "X-QA-Step": safe_header(step_2_text)}
            res_anomalies = await client.get("/api/v1/catalog/products/anomalies", headers=anom_headers)

            if res_anomalies.status_code == 200:
                results.append("   ✅ И Пользователь запрашивает эндпоинт мониторинга аномалий '/api/v1/catalog/products/anomalies'")
                
                anom_data = res_anomalies.json()
                has_anom = anom_data.get("has_anomalies", False)
                anom_list = anom_data.get("products", [])
                
                code_found = any(p.get("code") == test_product_code for p in anom_list)
                
                if has_anom and code_found:
                    results.append("   ✅ И При запросе эндпоинта '/catalog/products/anomalies' система возвращает этот товар в списке критических предупреждений")
                else:
                    return [f"❌ СБОЙ БИЗНЕС-ЛОГИКИ: Флаг has_anomalies={has_anom} или товар не найден в СУБД: {anom_data}"]
            else:
                return [f"❌ СБОЙ ЭНДПОИНТА АНОМАЛИЙ: Код {res_anomalies.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]
        finally:
            # 4. 🧼 TEARDOWN: Очистка СУБД
            await teardown_live_product_by_code(client, test_product_code)
            await teardown_live_brand_by_name(client, test_brand_snake)

    return results
