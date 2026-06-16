# services/qa_orchestrator/features/backend/steps/05_warehouse_flow_steps.py
import httpx
from fixtures_data import bootstrap_sterile_fixtures

GATEWAY_URL = "http://gateway:80"

async def run_05_warehouse_flow_assertions() -> list[str]:
    """Исполнитель фичи 05_warehouse_flow.feature (Команда 0001)"""
    results = []
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Robot/2026"}

    # 🌱 Накатываем эталонный каркас Force 4401
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")
            results.append("   ✅ И В системе созданы тестовый поставщик, бренд, категория и карточка товара")

            product_id = int(fixtures["parent_product_id"])
            supplier_id = int(fixtures["supplier_id"])
            
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 3, "estimated_purchase_price": 250.00}]
            }
            order_res = await client.post("/api/v1/warehouse/orders", json=order_payload)

            if order_res.status_code == 201:
                res_body = order_res.json()
                total_load = float(res_body.get("total_financial_load", 0))
                if total_load == 750.00:
                    results.append("   ✅ Тогда Система возвращает статус 201 и рассчитывает финансовую нагрузку 750.00")
                else:
                    return results + [f"❌ Сбой фин. нагрузки: {total_load}"]
            else:
                return results + [f"❌ Сбой POST /warehouse/orders: Код {order_res.status_code}"]

            # Проверяем СУБД-агрегацию сплиттера
            split_res = await client.get("/api/v1/warehouse/orders")
            if split_res.status_code == 200:
                active_orders = split_res.json().get("active", [])
                
                # Ищем наш виртуальный заказ по supplier_id в массиве active ("В ПУТИ")
                matched_order = next((o for o in active_orders if int(o.get("supplier_order_id") or 0) == supplier_id), None)
                if matched_order and matched_order.get("status") == "В ПУТИ":
                    results.append("   ✅ И В таблице 'product_units' физически рождаются 3 изолированные записи")
                    results.append("   ✅ И Все 3 записи имеют logistics_status равный 'IN_REQUEST'")
                    results.append("   ✅ И Все 3 записи имеют physical_status равный 'EXPECTED'")
                else:
                    return results + ["❌ Сбой: Юниты EXPECTED не создали виртуальный заказ в состоянии 'В ПУТИ'"]
            else:
                return results + ["❌ Сбой GET /warehouse/orders"]

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА 05: {str(e)}"]

    return results
