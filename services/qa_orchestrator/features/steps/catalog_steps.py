# catalog_steps.py
import httpx
import uuid

# Тестовый робот идет напрямую к бэкенду ядра по внутренней Docker-сети
CORE_DIRECT_URL = "http://backend:8000/api/v1"

async def run_catalog_story_assertions():
    """Функция-исполнитель, которая прогоняет сквозной сценарий по шагам"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=CORE_DIRECT_URL, timeout=5.0) as client:
        
        # Шаг 1: Дано Бэкенд Core доступен
        try:
            res = await client.get("/healthcheck")
            assert res.status_code == 200
            results.append("✔️ Шаг 'Дано Бэкенд Core доступен' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Шаг 'Дано Бэкенд Core доступен' — СБОЙ ({str(e)})"]

        # Шаг 2: Когда Пользователь создает поставщика
        try:
            sup_data = {"name": f"QA_Форсаж_{uid}", "contact_info": "test"}
            res = await client.post("/warehouse/suppliers", json=sup_data)
            assert res.status_code == 201
            results.append("✔️ Шаг 'Когда Пользователь создает поставщика' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Шаг 'Когда Пользователь создает поставщика' — СБОЙ ({str(e)})"]

        # Шаг 2.1: Создание дефотного Бренда (Трансформируется в snake_case)
        created_brand_id = None
        try:
            brand_data = {"name": f"QA Toptul {uid}"}
            res = await client.post("/catalog/brands", json=brand_data)
            assert res.status_code == 201
            created_brand_id = res.json().get("brand_id")
            results.append("✔️ Шаг 'Подготовка: Дефолтный бренд создан' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Шаг 'Подготовка: Создание бренда' — СБОЙ ({str(e)})"]

        # Шаг 2.2: Создание дефолтной Категории (Трансформируется в snake_case)
        created_category_id = None
        try:
            category_data = {"name": f"QA Ключи {uid}", "parent_id": None}
            res = await client.post("/catalog/categories", json=category_data)
            assert res.status_code == 201
            created_category_id = res.json().get("category_id")
            results.append("✔️ Шаг 'Подготовка: Дефолтная категория создана' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Шаг 'Подготовка: Создание категории' — СБОЙ ({str(e)})"]

        # Шаг 3: И Создает товар (Передаем ОБЯЗАТЕЛЬНЫЙ brand_id и массив images)
        try:
            prod_payload = {
                "category_id": created_category_id,
                "brand_id": created_brand_id,
                "code": f"QA-{uid}",
                "name": "Ключ рожковый 10мм Toptul",
                "description": "Тест",
                "recommended_retail_price": 500.00,
                "search_aliases": ["ск 10"],
                "images": ["/static/products/key10_main.jpg", "https://external-storage.com"]
            }
            res = await client.post("/catalog/products", json=prod_payload)
            
            # Шаг 4: Тогда Система возвращает статус 201
            if res.status_code != 201:
                raise Exception(f"Бэкенд вернул статус {res.status_code}: {res.text}")
            results.append("✔️ Шаг 'Тогда Система возвращает статус 201' — ПРОЙДЕН")
            
            generated_tags = res.json().get("generated_tags", [])
            
            # Шаг 5: И В тегах присутствуют нужные слова
            assert "ключ" in generated_tags
            assert "рожковый" in generated_tags
            assert "10мм" in generated_tags
            results.append("✔️ Шаг 'И В тегах присутствуют ключевые слова' — ПРОЙДЕН")
            
            # Шаг 6: И В тегах отсутствует предлог из 1 буквы
            assert "и" not in generated_tags
            results.append("✔️ Шаг 'И В тегах отсутствует предлог' — ПРОЙДЕН")
            
        except Exception as e:
            results.append(f"❌ Сбой на этапе работы с товаром ({str(e)})")
            
    return results
