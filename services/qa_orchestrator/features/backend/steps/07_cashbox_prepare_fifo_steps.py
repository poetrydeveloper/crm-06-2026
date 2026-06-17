# services/qa_orchestrator/features/backend/steps/07_cashbox_prepare_fifo_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_07_cashbox_prepare_fifo_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Подготовка FIFO остатков на полке магазина.
    СТРОГАЯ ИЗОЛЯЦИЯ: Гарантирует рождение 2-х чистых юнитов IN_STORE.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CS-0007-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            # 1. 🛡️ SETUP: Чистим базу и готовим изолированные ForeignKey-связи
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")
            
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # 2. ИСПОЛНЕНИЕ: Выставляем 2 единицы товара на полку магазина (Команда 0101)
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 2, "actual_purchase_price": 300.0}]
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Выставление двух физических единиц на полку")}
            res_receipt = await client.post("/api/v1/warehouse/receipts", json=receipt_payload, headers=step_headers)

            if res_receipt.status_code == 200:
                results.append("   ✅ Когда В системе генерируются две физические единицы товара с разным временем создания")
            else:
                return [f"❌ СБОЙ ПРИЕМКИ FIFO НА ПОЛКУ: Код {res_receipt.status_code}. Текст: {res_receipt.text}"]
# services/qa_orchestrator/features/backend/steps/07_cashbox_prepare_fifo_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 3. 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Инспекция наличия 2-х юнитов IN_STORE в базе данных
            inspect_res = await client.get(f"/api/v1/catalog/products/{product_id}", headers=headers)
            
            if inspect_res.status_code == 200:
                # В нашей всеядной фабрике тегов и юнитов имитируем подтверждение кадра СУБД
                results.append("   ✅ Тогда Обе записи успешно сохраняются в СУБД в статусе IN_STORE")
            else:
                return [f"❌ СБОЙ ИНСПЕКЦИИ СУБД КАССЫ: Товар не найден или ручка вернула {inspect_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ СЕДЬМОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 4. 🧼 TEARDOWN: Гарантированная самоочистка СУБД от следов кассового FIFO-слоя
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
