# services/qa_orchestrator/features/backend/steps/01_catalog_flow_steps.py (ИСПРАВЛЕННАЯ ЧАСТЬ 1 ИЗ 2)
import httpx
from utils.validators import validate_jsonb_tags, safe_header  # Импортируем утилиту!

GATEWAY_URL = "http://gateway:80"

async def run_01_catalog_flow_assertions() -> list[str]:
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CT-0001-01")}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен через шлюз Nginx")

            # 🔥 ИСПРАВЛЕНО: Текст шага теперь безопасно экранируется утилитой
            sup_step_text = "Создание тестового поставщика QA_Форсаж_Тест"
            sup_headers = {**headers, "X-QA-Step": safe_header(sup_step_text)}
            
            sup_res = await client.post(
                "/api/v1/warehouse/suppliers", 
                json={"name": "QA_Форсаж_Тест"}, 
                headers=sup_headers
            )
            
            if sup_res.status_code == 201:
                supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id", 1)
                results.append("   ✅ Когда Пользователь создает поставщика с именем 'QA_Форсаж_Тест'")
            else:
                return [f"❌ СБОЙ ПОСТАВЩИКА: Код {sup_res.status_code}. Текст: {sup_res.text}"]

            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Toptul"})
            brand_id = brand_res.json().get("brand_id", 1)
            
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Ключи рожковые"})
            category_id = cat_res.json().get("category_id", 1)

# services/qa_orchestrator/features/backend/steps/01_catalog_flow_steps.py (ИСПРАВЛЕННАЯ ЧАСТЬ 2 ИЗ 2)
            # Шаг 3: Запрос на создание товара с умной генерацией тегов
            product_payload = {
                "name": "Ключ рожковый 10мм Toptul",
                "code": "QA-КЛ-10",
                "recommended_retail_price": 350.0,
                "category_id": int(category_id),
                "brand_id": int(brand_id),
                "supplier_id": int(supplier_id)
            }
            
            # 🔥 ИСПРАВЛЕНО: Экранируем кириллицу в названии шага
            prod_step_text = "Отправка запроса на создание товара с автотегами"
            prod_headers = {**headers, "X-QA-Step": safe_header(prod_step_text)}
            prod_res = await client.post("/api/v1/catalog/products", json=product_payload, headers=prod_headers)

            if prod_res.status_code == 201:
                product_id = prod_res.json().get("product_id") or prod_res.json().get("id")
                results.append("   ✅ И Пользователь отправляет запрос на создание товара с именем 'Ключ рожковый 10мм Toptul' и артикулом 'QA-КЛ-10'")
                results.append("   ✅ Тогда Система возвращает статус 201")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ ТОВАРА: Код {prod_res.status_code}. Текст: {prod_res.text}"]

            # Шаг 4: 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ (ИНСПЕКЦИЯ JSONB-КАДРА НА СТОП-СЛОВА)
            inspect_res = await client.get(f"/api/v1/catalog/products/{product_id}", headers=headers)
            if inspect_res.status_code != 200:
                return [f"❌ СБОЙ ИНСПЕКЦИИ СУБД: Товар создан, но ручка чтения вернула {inspect_res.status_code}"]
                
            product_data = inspect_res.json()
            db_tags = product_data.get("search_tags", [])

            expected_words = ["ключ", "рожковый", "10мм", "qa-кл-10"]
            stop_words = ["и"]
            
            is_valid, error_msg = validate_jsonb_tags(db_tags, expected=expected_words, excluded=stop_words)
            
            if is_valid:
                results.append("   ✅ И В сгенерированных тегах присутствуют слова 'ключ', 'рожковый', '10мм', 'qa-кл-10'")
                results.append("   ✅ И В тегах отсутствует предлог 'и'")
            else:
                return [f"❌ {error_msg}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]

    return results