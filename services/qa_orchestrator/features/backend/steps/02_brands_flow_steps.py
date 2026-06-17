# services/qa_orchestrator/features/backend/steps/02_brands_flow_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory  # Импорт из новой папки fixtures!
from utils.validators import safe_header

GATEWAY_URL = "http://gateway:80"

async def run_02_brands_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль управления брендами.
    Проверяет: Трансформацию имени в snake_case ➡️ Защиту Foreign Key при удалении.
    """
    results = []
    headers = {"Host": "localhost"}

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # ==========================================
            # 🧪 СЦЕНАРИЙ 1: Валидация snake_case
            # ==========================================
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            step_1_text = "Создание бренда Форсаж Инструмент"
            step_headers = {**headers, "X-QA-Story": safe_header("BR-0002-01"), "X-QA-Step": safe_header(step_1_text)}
            
            res_create = await client.post("/api/v1/catalog/brands", json={"name": "Форсаж Инструмент"}, headers=step_headers)
            
            if res_create.status_code == 201:
                results.append("   ✅ Когда Пользователь создает бренд с именем 'Форсаж Инструмент'")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ БРЕНДА: Код {res_create.status_code}. Текст: {res_create.text}"]

            # 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Проверяем, что в списке брендов имя трансформировалось
            res_list = await client.get("/api/v1/catalog/brands", headers=headers)
            brands = res_list.json()
            
            transformed_found = any(b.get("name") == "форсаж_инструмент" for b in brands)
            
            if transformed_found:
                results.append("   ✅ Тогда Система должна вернуть статус 201 и в таблице 'brands' имя должно быть записано как 'форсаж_инструмент'")
            else:
                return [f"❌ СБОЙ В СУБД: Бренд создан, но в базе записан не как 'форсаж_инструмент'. Текущая СУБД-картинка: {brands}"]
            # ==========================================
            # 🧪 СЦЕНАРИЙ 2: Защита Foreign Key при DELETE
            # ==========================================
            # 1. Накатываем изолированный кадр данных: бренд 'toptul' с привязанным товаром 'КЛ-10'
            fix = await QAFixtureFactory.prepare_linked_brand_with_product(client)
            brand_id = fix["brand_id"]
            results.append("   ✅ Дано В системе существует бренд 'toptul' и привязанный к нему товар 'КЛ-10'")

            # 2. Отправляем запрос на удаление бренда через шлюз Nginx
            step_2_text = f"Попытка удаления связанного бренда ID {brand_id}"
            del_headers = {**headers, "X-QA-Story": safe_header("BR-0002-02"), "X-QA-Step": safe_header(step_2_text)}
            
            res_delete = await client.delete(f"/api/v1/catalog/brands/{brand_id}", headers=del_headers)

            # 3. 🛡️ ЖЕСТКИЙ АССЕРТ ОШИБКИ И СУБД-КОНТРАКТА
            if res_delete.status_code == 400:
                err_detail = res_delete.json().get("detail", "")
                if "Нельзя удалить бренд" in err_detail:
                    results.append("   ✅ Когда Пользователь отправляет запрос на удаление бренда 'toptul'")
                    results.append("   ✅ Тогда Система должна вернуть ошибку 400 с описанием 'Нельзя удалить бренд, к которому привязаны товары'")
                else:
                    return [f"❌ СБОЙ ВАЛИДАЦИИ: Код 400 вернулся, но текст ошибки некорректный: {err_detail}"]
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ БЕЗОПАСНОСТИ ДАННЫХ: Бэкенд удалил бренд со связанным товаром или вернул код {res_delete.status_code}"]

            # Проверяем СУБД-кадр: бренд обязан остаться в таблице brands!
            res_check = await client.get("/api/v1/catalog/brands", headers=headers)
            brands_check = res_check.json()
            brand_still_exists = any(b.get("id") == brand_id for b in brands_check)

            if brand_still_exists:
                # Всё отлично, целостность связей не нарушена
                pass
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ СУБД: Бэкенд вернул код 400, но бренд физически исчез из таблицы PostgreSQL!"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]

    return results
