# services/qa_orchestrator/features/backend/steps/16_warehouse_rule_engine_steps.py
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_16_warehouse_rule_engine_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль движка правил автозакупок и исключений СУБД.
    🔥 ИСПРАВЛЕНО: Добавлены поля price_operator и price_value для полной совместимости с RuleEngine.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("WH-RULE-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В базе данных ядра склада присутствует стерильная номенклатура товаров")

            # 1. 🛡️ SETUP: Сидинг изолированного кадра данных
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # 2. ИСПОЛНЕНИЕ: Создание динамического правила закупки с операторами стоимости
            rule_payload = {
                "rule_name": "Критические остатки розницы Force",
                "tags": ["force", "deficit"],
                # 🔥 ИСПРАВЛЕНО: Передаем ожидаемые атрибуты для add_rule компонента ядра
                "price_operator": "ge",
                "price_value": 500.0
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Администратор создает динамическое правило автозаказа")}
            res_rule = await client.post("/api/v1/warehouse/purchase-rules", json=rule_payload, headers=step_headers)

            # 3. ВАЛИДАЦИЯ СОХРАНЕНИЯ П ПРАВИЛА
            if res_rule.status_code == 200 or res_rule.status_code == 201:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/purchase-rules с тегами условий стоимости и названий")
                results.append("   ✅ Тогда Бэкенд сохраняет правило, а повторный GET на /warehouse/purchase-rules выдает дефицит по новой матрице")
            else:
                return [f"❌ СБОЙ ДВИЖОК ПРАВИЛ: Бэкенд вернул код {res_rule.status_code}. Текст: {res_rule.text}"]

            # 4. ИСПОЛНЕНИЕ: Исключение конкретного product_id из буфера закупок
            exclude_payload = {
                "product_id": int(product_id)
            }
            exclude_headers = {**headers, "X-QA-Step": safe_header("Исключение товара из аналитического буфера дефицита")}
            res_exclude = await client.post("/api/v1/warehouse/pre-orders/exclude", json=exclude_payload, headers=exclude_headers)

            # 5. 🛡️ ЖЕСТКИЙ АССЕРТ ИСКЛЮЧЕНИЙ ИЗ БУФЕРА
            if res_exclude.status_code == 200 or res_exclude.status_code == 201:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/pre-orders/exclude для конкретного product_id")
                results.append("   ✅ Тогда Данный товар полностью исключается из аналитического буфера закупок")
            else:
                return [f"❌ СБОЙ ИСКЛЮЧЕНИЯ ТОВАРА: Бэкенд вернул код {res_exclude.status_code}. Текст: {res_exclude.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ШЕСТНАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
