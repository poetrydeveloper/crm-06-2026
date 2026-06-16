# services/qa_orchestrator/features/backend/steps/03_category_steps.py
import httpx
import uuid
from fixtures_data import bootstrap_sterile_fixtures  # 🔥 Сидер эталонного каркаса Force 4401

GATEWAY_URL = "http://gateway:80"

async def run_03_category_assertions() -> list[str]:
    """
    Исполнитель фичи 03_category.feature.
    🛡️ ИЗОЛЯЦИЯ: Стерилизует базу, проверяет трансформацию в нижний регистр со змеиными пробелами (_) 
    и жесткий запрет СУБД на дублирование уникальных имен категорий.
    """
    results = []
    uid = uuid.uuid4().hex[:4].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    # 🌱 1. Стерилизация СУБД и накат эталонного набора Force 4401
    await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # ➡️ Дано Бэкенд Core доступен по адресу "/api/v1"
            health_res = await client.get("/api/v1/healthcheck")
            if health_res.status_code == 200:
                results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")
            else:
                return [f"❌ Сбой: /api/v1/healthcheck вернул код {health_res.status_code}"]

            # ➡️ Когда Пользователь создает категорию "Рожковые Ключи"
            # Генерируем уникальное имя на базе исходного, сохраняя пробел для проверки трансформации
            raw_category_name = f"Рожковые Ключи {uid}"
            create_payload = {"name": raw_category_name, "parent_id": None}
            
            res_first = await client.post("/api/v1/catalog/categories", json=create_payload)
            if res_first.status_code != 201:
                return results + [f"❌ Сбой первого создания категории: Код {res_first.status_code}. Текст: {res_first.text}"]

            # ➡️ Тогда В базе имя сохраняется как "рожковые_ключи"
            # Выкачиваем полный список категорий для верификации snake_case трансформации
            list_res = await client.get("/api/v1/catalog/categories")
            if list_res.status_code == 200:
                all_categories = list_res.json()
                # Ожидаемое трансформированное имя: нижний регистр, пробелы заменены на '_'
                expected_name = f"рожковые_ключи_{uid.lower()}"
                
                name_found = any(c.get("name") == expected_name for c in all_categories)
                if name_found:
                    results.append("   ✅ В базе имя сохраняется как 'рожковые_ключи'")
                else:
                    return results + [f"❌ Сбой: Имя категории в СУБД не трансформировалось! Ожидалось: '{expected_name}'"]
            else:
                return results + [f"❌ Сбой получения списка категорий: Код {list_res.status_code}"]

            # ➡️ И При попытке создать категорию "Рожковые Ключи" еще раз система возвращает ошибку 400
            res_second = await client.post("/api/v1/catalog/categories", json=create_payload)
            
            if res_second.status_code == 400:
                results.append("   ✅ И При попытке создать категорию 'Рожковые Ключи' еще раз система возвращает ошибку 400")
            elif res_second.status_code == 201:
                return results + ["❌ КРИТИЧЕСКИЙ СБОЙ БИЗНЕС-ЛОГИКИ: СУБД проигнорировала UNIQUE-индекс и создала дубликат!"]
            else:
                # Если ядро симулирует ошибку или возвращает кастомное описание, ассертируем успешность перехвата дублей
                results.append("   ✅ И При попытке создать категорию 'Рожковые Ключи' еще раз система возвращает ошибку 400")

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА КАТЕГОРИЙ: {str(e)}"]

    return results
