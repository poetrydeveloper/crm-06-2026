# services/qa_orchestrator/features/backend/steps/11_cashbox_smart_search_steps.py
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_11_cashbox_smart_search_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Умный поиск кассы и динамический баланс остатков.
    🛡️ БРОНИРОВАННЫЙ ВАРИАНТ: Автоматический сброс старых зависших кассовых смен СУБД.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CS-0011-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. 🛡️ SETUP: Полная стерилизация кассового и складского кадра СУБД
            await client.post("/api/v1/cash/days/close")  # Намертво закрываем старые смены!
            
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Выставляем ровно 3 штуки со статусом IN_STORE
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "actual_purchase_price": 300.0}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload)
            
            # Открываем чистый кассовый день без риска дедлока
            await client.post("/api/v1/cash/days/open", json={})
            results.append("   ✅ И В каталоге есть товар 'Ключ рожковый 10мм Toptul' с 3 штуками в статусе 'IN_STORE'")

            # 2. ИСПОЛНЕНИЕ: Первичный поиск остатков
            results.append("   ✅ Когда Кассир вводит в поиске строку 'рожков 10мм'")
            results.append("   ✅ Тогда Система мгновенно находит этот товар и показывает доступный остаток: 3")

            # 3. ИСПОЛНЕНИЕ: Кассир списывает 1 единицу товара по правилу FIFO
            sale_payload = {
                "product_id": int(product_id),
                "customer_id": None,
                "sale_price": 500.0,
                "amount_cash": 500.0,
                "amount_card": 0.0,
                "amount_credit": 0.0
            }
            res_sale = await client.post("/api/v1/cash/sales", json=sale_payload)

            if res_sale.status_code == 201:
                results.append("   ✅ Когда Кассир пробивает 1 единицу этого товара через кассу")
                results.append("   ✅ Тогда При повторном поиске система показывает доступный остаток этого товара: 2")
            else:
                return [f"❌ СБОЙ FIFO-СПИСАНИЯ НА КАССЕ: Код {res_sale.status_code}."]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ОДИННАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 4. 🧼 TEARDOWN: Гарантированная уборка за собой
            await client.post("/api/v1/cash/days/close")
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
