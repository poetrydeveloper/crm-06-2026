# services/qa_orchestrator/features/backend/steps/01_catalog_flow_steps.py
import httpx
from utils.validators import validate_jsonb_tags, safe_header
from utils.db_finders import teardown_live_product_by_code, teardown_live_brand_by_name, teardown_live_categories_by_name

GATEWAY_URL = "http://gateway:80"

async def run_01_catalog_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль автогенерации JSONB-тегов.
    СТРОГАЯ ИЗОЛЯЦИЯ: Самоочистка на входе и гарантированный Teardown в конце.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CT-0001-01")}
    
    test_product_code = "QA-КЛ-10"
    test_brand_snake = "toptul"
    test_category_snake = "ключи_рожковые"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # 1. 🛡️ SETUP: Принудительно вычищаем СУБД от хвостов этого теста перед стартом
            await teardown_live_product_by_code(client, test_product_code)
            await teardown_live_brand_by_name(client, test_brand_snake)
            await teardown_live_categories_by_name(client, test_category_snake)
            
            results.append("   ✅ Дано Бэкенд Core доступен через шлюз Nginx")

            # 2. Создание поставщика
            sup_headers = {**headers, "X-QA-Step": safe_header("Создание тестового поставщика QA_Форсаж_Тест")}
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "QA_Форсаж_Тест"}, headers=sup_headers)
            
            if sup_res.status_code == 201:
                supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id", 1)
                results.append("   ✅ Когда Пользователь создает поставщика с именем 'QA_Форсаж_Тест'")
            else:
                return [f"❌ СБОЙ ПОСТАВЩИКА: Код {sup_res.status_code}. Текст: {sup_res.text}"]

            # Создание структуры Foreign Key
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Toptul"})
            brand_id = brand_res.json().get("brand_id", 1)
            
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Ключи рожковые"})
            category_id = cat_res.json().get("category_id", 1)

            # 3. Создание товара
            product_payload = {
                "name": "Ключ рожковый 10мм Toptul", "code": test_product_code,
                "recommended_retail_price": 350.0, "category_id": int(category_id),
                "brand_id": int(brand_id), "supplier_id": int(supplier_id)
            }
            
            prod_headers = {**headers, "X-QA-Step": safe_header("Отправка запроса на создание товара с автотегами")}
            prod_res = await client.post("/api/v1/catalog/products", json=product_payload, headers=prod_headers)

            if prod_res.status_code == 201:
                product_id = prod_res.json().get("product_id") or prod_res.json().get("id")
                results.append("   ✅ И Пользователь отправляет запрос на создание товара с именем 'Ключ рожковый 10мм Toptul' и артикулом 'QA-КЛ-10'")
                results.append("   ✅ Тогда Система возвращает статус 201")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ ТОВАРА: Код {prod_res.status_code}. Текст: {prod_res.text}"]

            # 4. Жесткий СУБД-ассерт
            inspect_res = await client.get(f"/api/v1/catalog/products/{product_id}", headers=headers)
            if inspect_res.status_code != 200:
                return [f"❌ СБОЙ ИНСПЕКЦИИ СУБД: Товар создан, но ручка чтения вернула {inspect_res.status_code}"]
                
            db_tags = inspect_res.json().get("search_tags", [])
            is_valid, error_msg = validate_jsonb_tags(db_tags, expected=["ключ", "рожковый", "10мм", test_product_code], excluded=["и"])
            
            if is_valid:
                results.append("   ✅ И В сгенерированных тегах присутствуют слова 'ключ', 'рожковый', '10мм', 'qa-кл-10'")
                results.append("   ✅ И В тегах отсутствует предлог 'и'")
            else:
                return [f"❌ {error_msg}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]
            
        finally:
            # 5. 🧼 TEARDOWN: Полная ликвидация следов жизнедеятельности теста в БД
            await teardown_live_product_by_code(client, test_product_code)
            await teardown_live_brand_by_name(client, test_brand_snake)
            await teardown_live_categories_by_name(client, test_category_snake)

    return results
