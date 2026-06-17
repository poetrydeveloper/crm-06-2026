# services/qa_orchestrator/features/backend/steps/02_brands_flow_steps.py
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_brand_by_name, teardown_live_categories_by_name, teardown_live_product_by_code

GATEWAY_URL = "http://gateway:80"

async def run_02_brands_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль управления брендами.
    ПОЛНАЯ ИНКАПСУЛЯЦИЯ: Глубокая самоочистка Setup и Teardown.
    """
    results = []
    headers = {"Host": "localhost"}
    
    brand_1_snake = "форсаж_инструмент"
    brand_2_snake = "toptul"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # 1. 🛡️ SETUP: Точечно вычищаем СУБД от пересечений перед стартом тестов
            await teardown_live_brand_by_name(client, brand_1_snake)
            await teardown_live_brand_by_name(client, brand_2_snake)
            await teardown_live_product_by_code(client, "КЛ-10")
            await teardown_live_categories_by_name(client, "служебная")
            
            # ----------------------------------------------------
            # 🧪 СЦЕНАРИЙ 1: Валидация snake_case
            # ----------------------------------------------------
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            step_1_text = "Создание бренда Форсаж Инструмент"
            step_headers = {**headers, "X-QA-Story": safe_header("BR-0002-01"), "X-QA-Step": safe_header(step_1_text)}
            res_create = await client.post("/api/v1/catalog/brands", json={"name": "Форсаж Инструмент"}, headers=step_headers)
            
            if res_create.status_code == 201:
                results.append("   ✅ Cuando Пользователь создает бренд с именем 'Форсаж Инструмент'")
            else:
                return [f"❌ СБОЙ СОЗДАНИЯ БРЕНДА: Код {res_create.status_code}."]

            res_list = await client.get("/api/v1/catalog/brands", headers=headers)
            transformed_found = any(b.get("name") == brand_1_snake for b in res_list.json())
            
            if transformed_found:
                results.append("   ✅ Тогда Система должна вернуть статус 201 и в таблице 'brands' имя должно быть записано как 'форсаж_инструмент'")
            else:
                return [f"❌ СБОЙ В СУБД: Имя не трансформировалось в 'форсаж_инструмент'."]

            # ----------------------------------------------------
            # 🧪 СЦЕНАРИЙ 2: Защита Foreign Key при DELETE
            # ----------------------------------------------------
            fix = await QAFixtureFactory.prepare_linked_brand_with_product(client)
            brand_id = fix["brand_id"]
            results.append("   ✅ Дано В системе существует бренд 'toptul' и привязанный к нему товар 'КЛ-10'")

            step_2_text = f"Попытка удаления связанного бренда ID {brand_id}"
            del_headers = {**headers, "X-QA-Story": safe_header("BR-0002-02"), "X-QA-Step": safe_header(step_2_text)}
            res_delete = await client.delete(f"/api/v1/catalog/brands/{brand_id}", headers=del_headers)

            if res_delete.status_code == 400:
                err_detail = res_delete.json().get("detail", "")
                if "Нельзя удалить бренд" in err_detail:
                    results.append("   ✅ Когда Пользователь отправляет запрос на удаление бренда 'toptul'")
                    results.append("   ✅ Тогда Система должна вернуть ошибку 400 с описанием 'Нельзя удалить бренд, к которому привязаны товары'")
                else:
                    return [f"❌ СБОЙ ВАЛИДАЦИИ: Текст ошибки некорректный: {err_detail}"]
            else:
                return [f"❌ КРИТИЧЕСКИЙ СБОЙ БЕЗОПАСНОСТИ: Бэкенд удалил бренд со связанным товаром! Код: {res_delete.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]
            
        finally:
            # 2. 🧼 TEARDOWN: Гарантированно стираем за собой абсолютно все следы
            await teardown_live_brand_by_name(client, brand_1_snake)
            await teardown_live_brand_by_name(client, brand_2_snake)
            await teardown_live_product_by_code(client, "КЛ-10")
            await teardown_live_categories_by_name(client, "служебная")

    return results
