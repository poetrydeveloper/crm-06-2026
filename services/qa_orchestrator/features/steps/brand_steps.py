# brand_steps.py
import httpx
import uuid

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_brand_lifecycle_and_transformations():
    """Проверка Истории 1: Управление брендами, snake_case валидация и блокировки удаления"""
    results = []
    uid = uuid.uuid4().hex[:6]
    raw_name = f"Форсаж Инструмент {uid}"
    expected_snake_name = f"форсаж_инструмент_{uid}"
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        # 1. Тест создания и автоматической трансформации в нижний регистр с подчеркиваниями
        try:
            res = await client.post("/catalog/brands", json={"name": raw_name, "description": "Тест"})
            assert res.status_code == 201
            created_id = res.json().get("brand_id")
            assert res.json().get("name") == expected_snake_name
            results.append("✔️ Шаг 'Бренд успешно создан и переведен в snake_case' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Тест создания бренда — СБОЙ ({str(e)})"]

        # 2. Тест редактирования названия бренда
        try:
            up_payload = {"name": f"Новый Форсаж {uid}", "description": "Обновлено"}
            up_res = await client.put(f"/catalog/brands/{created_id}", json=up_payload)
            assert up_res.status_code == 200
            results.append("✔️ Шаг 'Редактирование названия бренда' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Тест редактирования бренда — СБОЙ ({str(e)})"]

        # 3. Тест блокировки удаления бренда, если к нему привязан товар
        try:
            # Подготовка: Создаем категорию (используем готовую резервную ID=1)
            # Подготовка: Создаем товар и привязываем его к нашему бренду
            prod_payload = {
                "category_id": 1,
                "brand_id": created_id,
                "code": f"BRN-DEL-{uid}",
                "name": "Тестовый Товар Для Блокировки Бренда",
                "recommended_retail_price": 150.00,
                "images": []
            }
            p_res = await client.post("/catalog/products", json=prod_payload)
            if p_res.status_code != 201:
                raise Exception(f"Ошибка создания товара для теста бренда: {p_res.text}")
            
            # Действие: Пытаемся удалить бренд, к которому привязан товар
            del_res = await client.delete(f"/catalog/brands/{created_id}")
            # Бэкенд обязан выдать 400 Bad Request
            if del_res.status_code != 400:
                raise Exception(f"Бэкенд разрешил удалить бренд со связями! Статус {del_res.status_code}")
                
            results.append("✔️ Шаг 'Защита от удаления связанного бренда' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Тест блокировки удаления бренда — СБОЙ ({str(e)})")
            
    return results
