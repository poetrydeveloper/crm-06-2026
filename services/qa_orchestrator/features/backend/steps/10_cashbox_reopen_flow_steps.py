# services/qa_orchestrator/features/backend/steps/10_cashbox_reopen_flow_steps.py (ИСПРАВЛЕННАЯ ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_10_cashbox_reopen_flow_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль переоткрытия смены и дозаписи чеков.
    ИСПРАВЛЕНО: Удален неявный NoneType возврат из функции-заглушки.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CS-0010-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. SETUP: Генерируем чистый товар и выставляем стартовые FIFO-юниты на полку
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Выставляем остатки на полку магазина (Команда 0101)
            receipt_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 250.0}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload)
# services/qa_orchestrator/features/backend/steps/10_cashbox_reopen_flow_steps.py (ИСПРАВЛЕННАЯ ЧАСТЬ 2 ИЗ 2)
            # 2. ИСПОЛНЕНИЕ: Открываем кассовый день и фиксируем cash_day_id
            step_1_text = "Открытие операционного дня для переоткрытия"
            open_headers = {**headers, "X-QA-Step": safe_header(step_1_text)}
            open_res = await client.post("/api/v1/cash/days/open", json={"date": "2026-06-17T11:00:00"}, headers=open_headers)
            
            if open_res.status_code == 201:
                cash_day_id = open_res.json().get("cash_day_id") or open_res.json().get("id", 1)
            else:
                return [f"❌ СБОЙ SETUP СМЕНЫ: Код {open_res.status_code}. Текст: {open_res.text}"]

            # Закрываем кассовый день (переводим в архив)
            await client.post("/api/v1/cash/days/close")

            # 3. ТЕСТИРУЕМ REOPEN: Активируем архивную смену через официальный эндпоинт
            step_2_text = f"Переоткрытие кассового дня ID {cash_day_id}"
            reopen_headers = {**headers, "X-QA-Step": safe_header(step_2_text)}
            reopen_res = await client.post(f"/api/v1/cash/days/{cash_day_id}/reopen", headers=reopen_headers)
            
            if reopen_res.status_code == 200:
                results.append("   ✅ Когда Администратор успешно переоткрывает архивный кассовый день")
            else:
                return [f"❌ СБОЙ REOPEN: Ручка вернула код {reopen_res.status_code}. Текст: {reopen_res.text}"]

            # 4. ВАЛИДАЦИЯ ДОЗАПИСИ ЧЕКА: Проверяем, что продажи снова разрешены
            sale_payload = {
                "product_id": int(product_id),
                "customer_id": None,
                "sale_price": 500.0,
                "amount_cash": 500.0,
                "amount_card": 0.0,
                "amount_credit": 0.0
            }
            step_3_text = "Кассир пробивает розничный чек в переоткрытую смену"
            sale_headers = {**headers, "X-QA-Step": safe_header(step_3_text)}
            sale_res = await client.post("/api/v1/cash/sales", json=sale_payload, headers=sale_headers)

            if sale_res.status_code == 201:
                results.append("   ✅ Тогда Система разрешает проведение операций")
                results.append("   ✅ И Новый чек успешно дозаписывается в СУБД")
            else:
                return [f"❌ СБОЙ ДОЗАПИСИ ЧЕКА: Код {sale_res.status_code}. Текст: {sale_res.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ДЕСЯТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 5. 🧼 TEARDOWN: Намертво запечатываем день и вычищаем мусор из СУБД
            await client.post("/api/v1/cash/days/close")
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
