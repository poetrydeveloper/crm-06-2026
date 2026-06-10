# category_steps.py
import httpx
import uuid

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_category_story_assertions():
    """Проверка Истории 2: Управление категориями, валидация и блокировки дубликатов"""
    results = []
    uid = uuid.uuid4().hex[:6]
    raw_name = f"Рожковые Ключи {uid}"
    expected_snake_name = f"рожковые_ключи_{uid}"
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        # 1. Тест создания и автоматической трансформации в snake_case
        try:
            res = await client.post("/catalog/categories", json={"name": raw_name, "parent_id": None})
            assert res.status_code == 201
            created_id = res.json().get("category_id")
            assert res.json().get("name") == expected_snake_name
            results.append("✔️ Шаг 'Категория успешно создана и переведена в snake_case' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Тест создания категории — СБОЙ ({str(e)})"]

        # 2. Тест запрета дублирования имен (Должен вернуть 400 Bad Request)
        try:
            res = await client.post("/catalog/categories", json={"name": raw_name, "parent_id": None})
            if res.status_code != 400:
                raise Exception(f"Бэкенд при дублировании вернул статус {res.status_code}: {res.text}")
            results.append("✔️ Шаг 'Запрет создания дубликата категории' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Тест дублирования категории — СБОЙ ({str(e)})"]

        # 3. Тест блокировки удаления категории при наличии связанных товаров
        try:
            # Подготовка: Создаем тестовый бренд
            brand_res = await client.post("/catalog/brands", json={"name": f"Test Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            
            # Подготовка: Создаем товар внутри нашей категории
            prod_payload = {
                "category_id": created_id,
                "brand_id": brand_id,
                "code": f"CAT-DEL-{uid}",
                "name": "Тестовый Товар Для Удаления Категории",
                "recommended_retail_price": 100.00,
                "images": []
            }
            p_res = await client.post("/catalog/products", json=prod_payload)
            if p_res.status_code != 201:
                raise Exception(f"Ошибка подготовки товара: {p_res.text}")
            
            # Действие: Пытаемся удалить категорию, к которой только что привязали товар
            del_res = await client.delete(f"/catalog/categories/{created_id}")
            if del_res.status_code != 400:
                raise Exception(f"Бэкенд разрешил удалить категорию со связями! Статус {del_res.status_code}")
            results.append("✔️ Шаг 'Защита от удаления связанной категории' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Тест блокировки удаления категории — СБОЙ ({str(e)})")
            
    return results
