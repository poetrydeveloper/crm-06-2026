# services/qa_orchestrator/features/backend/steps/03_categories_flow_steps.py
import httpx
from utils.validators import safe_header
from utils.db_finders import teardown_live_categories_by_name  # Наш Teardown-компонент!

GATEWAY_URL = "http://gateway:80"

async def run_03_categories_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль уникальности дерева категорий.
    ПОЛНАЯ ИНКАПСУЛЯЦИЯ: Самоочистка «До» и гарантированный Teardown «После».
    """
    results = []
    headers = {"Host": "localhost"}
    target_category_name = "рожковые_ключи"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # 1. 🛡️ SETUP: Перед стартом принудительно убираем категорию, если она зависла в базе
            await teardown_live_categories_by_name(client, target_category_name)
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 2. Исполнение сценария создания
            step_1_text = "Создание категории Рожковые Ключи"
            step_headers = {**headers, "X-QA-Story": safe_header("CT-0003-01"), "X-QA-Step": safe_header(step_1_text)}
            res_create = await client.post("/api/v1/catalog/categories", json={"name": "Рожковые Ключи", "parent_id": None}, headers=step_headers)
            
            if res_create.status_code == 201:
                results.append("   ✅ Когда Пользователь создает категорию 'Рожковые Ключи'")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ КАТЕГОРИИ: Код {res_create.status_code}. Текст: {res_create.text}"]

            # СУБД-ассерт трансформации имени
            res_list = await client.get("/api/v1/catalog/categories", headers=headers)
            transformed_found = any(c.get("name") == target_category_name for c in res_list.json())
            
            if transformed_found:
                results.append("   ✅ Тогда В базе имя сохраняется как 'рожковые_ключи'")
            else:
                return [f"❌ СБОЙ В СУБД: Имя не трансформировалось в 'рожковые_ключи'."]

            # 3. Валидация дубликата
            step_2_text = "Попытка повторного создания дубликата"
            dup_headers = {**headers, "X-QA-Story": safe_header("CT-0003-01"), "X-QA-Step": safe_header(step_2_text)}
            res_dup = await client.post("/api/v1/catalog/categories", json={"name": "Рожковые Ключи", "parent_id": None}, headers=dup_headers)

            if res_dup.status_code == 400:
                results.append("   ✅ И При попытке создать категорию 'Рожковые Ключи' еще раз система возвращает ошибку 400")
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ УНИКАЛЬНОСТИ: СУБД пропустила дубликат! Код: {res_dup.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]
            
        finally:
            # 4. 🧼 TEARDOWN: Гарантированно чистим за собой базу данных, что бы ни случилось в тесте
            await teardown_live_categories_by_name(client, target_category_name)

    return results
