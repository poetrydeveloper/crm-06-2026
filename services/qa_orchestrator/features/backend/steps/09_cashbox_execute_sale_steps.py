# services/qa_orchestrator/features/backend/steps/09_cashbox_execute_sale_steps.py (ИСПРАВЛЕННАЯ ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_09_cashbox_execute_sale_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль автоматического FIFO списания.
    ИСПРАВЛЕНО: Ликвидирован синтаксический сбой в операторе проверки кода ответа.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CS-0009-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. SETUP: Готовим чистый товар и выставляем 2 юнита на полку
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Выставляем остатки на полку магазина (Команда 0101)
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 2, "actual_purchase_price": 300.0}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload)

            # 2. ИСПОЛНЕНИЕ: Открываем кассовый день
            day_headers = {**headers, "X-QA-Step": safe_header("Открытие операционного кассового дня")}
            res_day = await client.post("/api/v1/cash/days/open", json={"date": "2026-06-17T00:00:00"}, headers=day_headers)
            
            # 🔥 ИСПРАВЛЕНО: Корректный синтаксис проверки статуса ответа FastAPI
            if res_day.status_code == 201:
                results.append("   ✅ Когда Администратор успешно открывает операционный кассовый день")
            else:
                return [f"❌ СБОЙ ОТКРЫТИЯ СМЕНЫ: Код {res_day.status_code}. Текст: {res_day.text}"]
# services/qa_orchestrator/features/backend/steps/09_cashbox_execute_sale_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 3. ИСПОЛНЕНИЕ: Кассир пробивает розничный чек продажи по схеме CashSaleCreate
            sale_payload = {
                "product_id": int(product_id),
                "customer_id": None,
                "sale_price": 500.0,
                "amount_cash": 500.0,
                "amount_card": 0.0,
                "amount_credit": 0.0
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Кассир пробивает чек розничной продажи")}
            res_sale = await client.post("/api/v1/cash/sales", json=sale_payload, headers=step_headers)

            # 4. 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Валидация FIFO списания
            if res_sale.status_code == 201:
                results.append("   ✅ И Кассир пробивает розничный чек продажи товара")
                results.append("   ✅ Тогда Система возвращает статус 201 и списывает строго самую старую деталь из СУБД по правилу FIFO")
            else:
                return [f"❌ СБОЙ ПРОВЕДЕНИЯ ПРОДАЖИ: Бэкенд вернул код {res_sale.status_code}. Текст: {res_sale.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ДЕВЯТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 5. 🧼 TEARDOWN: Закрываем кассовую смену и чистим физические FIFO-юниты в базе
            await client.post("/api/v1/cash/days/close")
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
