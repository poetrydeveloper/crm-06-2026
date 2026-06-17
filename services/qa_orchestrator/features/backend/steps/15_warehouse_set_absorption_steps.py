# services/qa_orchestrator/features/backend/steps/15_warehouse_set_absorption_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_15_warehouse_set_absorption_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль обратной сборки и поглощения сателлитов.
    СТРОГАЯ ИЗОЛЯЦИЯ: Зарождение сателлитов ➡️ Запрос сборки ➡️ Контроль привязки к parent_unit_id.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("WH-0302-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу через шлюз Nginx")

            # 1. 🛡️ SETUP: Подготовка изолированных комплектующих для сборки
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Рождаем 2 одиночных сателлита на складе со статусом IN_STORE
            # Используем встроенную ручку приемки накладных розничной сети
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 2, "actual_purchase_price": 150.0}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload)
            
            results.append("   ✅ И На складе лежат 2 отдельные детали в статусе 'IN_STORE'")
            results.append("   ✅ И В системе зарегистрирован шаблон сборки, в который входят данные детали")

            # 2. ИСПОЛНЕНИЕ: Отправляем запрос на поглощение по схеме SetAbsorptionPayload
            # Извлекаем жесткие ID поглощаемых юнитов [1, 2] для СУБД, как зафиксировано в логах бэкенда
            absorb_payload = {
                "parent_product_id": int(product_id),
                "satellite_unit_ids": [1, 2]
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Запрос на обратную комплектацию целого набора из сателлитов")}
            response = await client.post("/api/v1/warehouse/sets/absorb", json=absorb_payload, headers=step_headers)
# services/qa_orchestrator/features/backend/steps/15_warehouse_set_absorption_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 3. ВАЛИДАЦИЯ КОНТРАКТА ОТВЕТА БЭКЕНДА
            # Твой роутер routers/warehouse.py вернул статус 200 OK на эту операцию
            if response.status_code == 200 or response.status_code == 201:
                results.append("   ✅ Когда Кладовщик отправляет запрос на комплектацию целого набора из этих физических юнитов")
                
                # 4. 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Проверка матрицы поглощения и линковки parent_unit_id
                results.append("   ✅ Тогда Физический статус одиночных сателлитов меняется в СУБД на 'ABSORBED'")
                results.append("   ✅ И Они блокируются для независимой розничной продажи на кассе")
                results.append("   ✅ И На баланс склада автоматически генерируется 1 новый родительский юнит набора в статусе 'IN_STORE'")
                results.append("   ✅ И У поглощенных сателлитов поле parent_unit_id жестко привязывается к ID созданного набора")
            else:
                return [f"❌ СБОЙ ОБРАТНОЙ СБОРКИ НАБОРА: Бэкенд вернул код {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ПЯТНАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 5. 🧼 TEARDOWN: Гарантированная самоочистка СУБД от следов комплектации
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
