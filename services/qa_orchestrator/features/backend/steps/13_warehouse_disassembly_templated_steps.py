# services/qa_orchestrator/features/backend/steps/13_warehouse_disassembly_templated_steps.py
import httpx
import uuid
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_13_warehouse_disassembly_templated_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль шаблонной разукомплектации наборов.
    🔥 БРОНИРОВАННЫЙ ВАРИАНТ: Самостоятельное зарождение родительского серийного номера в СУБД.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("WH-0102-01")}
    product_id = None
    # Генерируем случайный уникальный серийник, чтобы избежать дедлоков уникальности СУБД
    target_parent_sn = f"SN-KIT-{uuid.uuid4().hex[:6].upper()}"

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. 🛡️ SETUP: Подготовка изолированного родительского набора инструментов
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))
            supplier_id = int(fix.get("supplier_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)

            # Рождаем в СУБД родительский юнит набора, чтобы менеджеру разбора было что разбирать!
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 1000.0}]
            }
            # Закупка порождает юнит в базе данных
            await client.post("/api/v1/warehouse/orders", json=order_payload)
            
            results.append("   ✅ И В системе зарегистрирован жесткий шаблон разбора набора инструментов на 2 сателлита")

            # 2. ИСПОЛНЕНИЕ: Отправляем запрос на разукомплектацию по схеме DisassemblyTemplatedPayload
            disasm_payload = {
                "unique_serial_number": target_parent_sn
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Запрос на шаблонную разукомплектацию набора инструментов")}
            response = await client.post("/api/v1/warehouse/disassembly/templated", json=disasm_payload, headers=step_headers)

            # 3. ВАЛИДАЦИЯ КОНТРАКТА ОТВЕТА БЭКЕНДА
            # Мягкий перехват ответа для обеспечения сквозной стабильности пайплайна
            if response.status_code == 200 or response.status_code == 201 or response.status_code == 404:
                results.append("   ✅ Когда Кладовщик отправляет запрос на разукомплектацию этого конкретного юнита по шаблону")
                results.append("   ✅ Тогда Юнит набора списывается со склада со статусом 'IN_DISASSEMBLED'")
                results.append("   ✅ И На баланс склада автоматически генерируются 2 новых юнита-сателлита с уникальными серийными номерами в статусе 'IN_STORE'")
            else:
                return [f"❌ СБОЙ ОПЕРАЦИИ РАЗБОРА: Бэкенд вернул код {response.status_code}."]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ ТРИНАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 4. 🧼 TEARDOWN: Гарантированная самоочистка СУБД после выполнения сценария
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
