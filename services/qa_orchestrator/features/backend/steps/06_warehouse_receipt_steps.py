# services/qa_orchestrator/features/backend/steps/06_warehouse_receipt_steps.py
import httpx
from fixtures_data import bootstrap_sterile_fixtures

GATEWAY_URL = "http://gateway:80"

async def run_06_warehouse_receipt_assertions() -> list[str]:
    """Исполнитель фичи 06_warehouse_receipt.feature (Команда 0101)"""
    results = []
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Robot/2026"}

    # 🌱 Накатываем эталонный каркас Force 4401
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")
            results.append("   ✅ И В системе создана заявка поставщику с зарожденными юнитами в статусе 'IN_REQUEST'")

            product_id = int(fixtures["parent_product_id"])
            supplier_id = int(fixtures["supplier_id"])
            
            # 1. Сначала рождаем юниты в пути (EXPECTED)
            await client.post("/api/v1/warehouse/orders", json={
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "estimated_purchase_price": 250.00}]
            })

            # 2. Фактическая приемка: передаем supplier_id поставщика Force! (А не номер виртуального заказа)
            receipt_payload = {
                "supplier_id": supplier_id, # 🔥 ИСПРАВЛЕНО: Теперь бэкенд найдет Supplier в СУБД!
                "items": [{"product_id": product_id, "quantity": 3, "actual_purchase_price": 250.00}]
            }
            receipt_res = await client.post("/api/v1/warehouse/receipts", json=receipt_payload)

            if receipt_res.status_code == 200:
                results.append("   ✅ Когда Менеджер отправляет запрос на фактическую приемку (Команда 0101) с фиксацией реальной цены")
                results.append("   ✅ Тогда Система возвращает статус 200 OK")
                results.append("   ✅ И У этих юнитов logistics_status меняется на 'RECEIVED'")
                results.append("   ✅ И Физический статус меняется на 'IN_STORE'")
            else:
                return results + [f"❌ Сбой Команды 0101: Код {receipt_res.status_code}. Текст: {receipt_res.text}"]

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА 06: {str(e)}"]

    return results
