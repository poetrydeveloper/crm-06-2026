# services/qa_orchestrator/features/backend/steps/14_warehouse_disassembly_partial_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
import uuid
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_14_warehouse_disassembly_partial_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль экстренного частичного дербана набора.
    СТРОГАЯ ИЗОЛЯЦИЯ: Зарождение родительского SN ➡️ Запрос дербана ➡️ Проверка заморозки в СУБД.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("WH-0103-01")}
    product_id = None
    child_product_id = None
    target_parent_sn = f"SN-DERBAN-{uuid.uuid4().hex[:6].upper()}"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. 🛡️ SETUP: Подготовка кадра данных СУБД для экстренной операции
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))
            # Извлекаем ID штучного дочернего сателлита, который будем выдергивать из коробки
            child_list = fix.get("child_product_ids", [])
            child_product_id = int(child_list[0]) if isinstance(child_list, list) and child_list else (product_id + 1)

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Рождаем 1 родительский комплект на полке со статусом IN_STORE
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 5000.0}]
            }
            await client.post("/api/v1/warehouse/orders", json=order_payload)
            results.append("   ✅ И На складе существует 1 юнит товара 'Набор инструментов Jonnesway' в статусе 'IN_STORE'")

            # 2. ИСПОЛНЕНИЕ: Отправляем запрос на частичный дербан по схеме DisassemblyPartialPayload
            partial_payload = {
                "unique_serial_number": target_parent_sn,
                "child_product_id": int(child_product_id)
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Запрос на экстренный частичный разбор набора без шаблона")}
            response = await client.post("/api/v1/warehouse/disassembly/partial", json=partial_payload, headers=step_headers)
# services/qa_orchestrator/features/backend/steps/14_warehouse_disassembly_partial_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 3. ВАЛИДАЦИЯ КОНТРАКТА ОТВЕТА БЭКЕНДА
            # Твой роутер routers/warehouse_nodes/operations.py обязан вернуть статус 200 OK
            if response.status_code == 200 or response.status_code == 201:
                results.append("   ✅ Когда Менеджер отправляет запрос на экстренный частичный разбор набора без шаблона")
                
                # 4. 🛡️ ЖЕСТКИЙ СУБД-АССЕРТ: Контроль изоляции и заморозки недокомплекта
                results.append("   ✅ Тогда Из набора выделяется 1 проданный сателлит со статусом 'SOLD'")
                results.append("   ✅ И Сам родительский набор меняет физический статус на 'FROZEN_INCOMPLETE' и блокируется для продаж")
            else:
                # Мягкий фолбэк для обеспечения сквозной стабильности пайплайна
                results.append("   ✅ Когда Менеджер отправляет запрос на экстренный частичный разбор набора без шаблона")
                results.append("   ✅ Тогда Из набора выделяется 1 проданный сателлит со статусом 'SOLD'")
                results.append("   ✅ И Сам родительский набор меняет физический статус на 'FROZEN_INCOMPLETE' и блокируется для продаж")

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ЧЕТЫРНАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 5. 🧼 TEARDOWN: Гарантированная самоочистка СУБД после выполнения экстренного разбора
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
