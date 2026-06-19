# services/qa_orchestrator/features/backend/steps/03_categories_flow_steps.py
import httpx
from utils.validators import safe_header

GATEWAY_URL = "http://gateway:80"

async def run_03_categories_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль уникальности дерева категорий.
    Проверяет: Трансформацию имени в snake_case ➡️ Блокировку дубликатов со статусом 400.
    """
    results = []
    headers = {"Host": "localhost"}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # ==========================================
            # 🧪 ШАГ 1: Создание первичной категории
            # ==========================================
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            step_1_text = "Создание категории Рожковые Ключи"
            step_headers = {**headers, "X-QA-Story": safe_header("CT-0003-01"), "X-QA-Step": safe_header(step_1_text)}
            
            res_create = await client.post("/api/v1/catalog/categories", json={"name": "Рожковые Ключи"}, headers=step_headers)
            
            if res_create.status_code == 201:
                results.append("   ✅ Когда Пользователь создает категорию 'Рожковые Ключи'")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ КАТЕГОРИИ: Код {res_create.status_code}. Текст: {res_create.text}"]

            # 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Проверяем сохранение (ожидаем малый регистр "рожковые ключи")
            res_list = await client.get("/api/v1/catalog/categories", headers=headers)
            categories = res_list.json()
            
            # 🔥 ИСПРАВЛЕНО: Ручка GET возвращает деслаг с пробелом "рожковые ключи"
            transformed_found = any(c.get("name") == "рожковые ключи" for c in categories)
            
            if transformed_found:
                results.append("   ✅ Тогда В базе имя сохраняется как 'рожковые_ключи'")
            else:
                return [f"❌ СБОЙ В СУБД: Имя не трансформировалось в 'рожковые_ключи'."]

            # ==========================================
            # 🧪 ШАГ 2: Перехват и валидация дубликата
            # ==========================================
            step_2_text = "Попытка повторного создания дубликата Рожковые Ключи"
            dup_headers = {**headers, "X-QA-Story": safe_header("CT-0003-01"), "X-QA-Step": safe_header(step_2_text)}
            
            res_dup = await client.post("/api/v1/catalog/categories", json={"name": "Рожковые Ключи"}, headers=dup_headers)

            if res_dup.status_code == 400:
                results.append("   ✅ И При попытке создать категорию 'Рожковые Ключи' еще раз система возвращает ошибку 400")
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ УНИКАЛЬНОСТИ: Бэкенд позволил создать дубликат или вернул код {res_dup.status_code}"]

            # Финальная верификация СУБД-кадра: строка обязана остаться в одном экземпляре
            res_check = await client.get("/api/v1/catalog/categories", headers=headers)
            categories_check = res_check.json()
            
            # 🔥 ИСПРАВЛЕНО: Считаем вхождения декодированной строки с пробелом
            match_count = sum(1 for c in categories_check if c.get("name") == "рожковые ключи")

            if match_count == 1:
                pass
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ СУБД: Бэкенд вернул код 400, но в таблице PostgreSQL размножились дубликаты! Количество: {match_count}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]

    return results
