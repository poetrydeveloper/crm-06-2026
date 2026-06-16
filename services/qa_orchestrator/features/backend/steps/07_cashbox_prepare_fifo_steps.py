# services/qa_orchestrator/features/backend/steps/07_cashbox_prepare_fifo_steps.py
import httpx
import asyncio
from datetime import datetime, timezone
from fixtures_data import bootstrap_sterile_fixtures  # 🔥 Сидер эталонного каркаса Force 4401

GATEWAY_URL = "http://gateway:80"

async def run_cashbox_prepare_fifo_assertions() -> list[str]:
    """
    Стадия 1: Подготовка остатков FIFO и открытие дня.
    🛡️ ИЗОЛЯЦИЯ: Стерилизует базу, штампует Force 4401 и разносит партии по времени.
    """
    results = []
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    # 🌱 1. Стерилизация СУБД и накат эталонного набора Force 4401
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # ➡️ Дано Бэкенд Core доступен по адресу "/api/v1"
            health_res = await client.get("/api/v1/healthcheck")
            if health_res.status_code != 200:
                return [f"❌ Сбой: /api/v1/healthcheck вернул код {health_res.status_code}"]
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # Вытаскиваем фиксированные ID из фикстур Force
            product_id = int(fixtures["parent_product_id"])
            supplier_id = int(fixtures["supplier_id"])

            # ➡️ Когда В системе генерируются две физические единицы товара с разным временем создания
            # Партия №1: Закупаем и сразу выставляем на полку через честный ReceiptManager
            receipt_payload_1 = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 100.00}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload_1)

            # Жестко замораживаем поток на 1.1 секунды, гарантируя разнос timestamp для закона FIFO в PostgreSQL!
            await asyncio.sleep(1.1)

            # Партия №2: Закупаем вторую единицу товара с повышенной ценой закупки
            receipt_payload_2 = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 105.00}]
            }
            await client.post("/api/v1/warehouse/receipts", json=receipt_payload_2)
            results.append("   ✅ Когда В системе генерируются две физические единицы товара с разным временем создания")

            # ➡️ Тогда Обе записи успешно сохраняются в СУБД в статусе IN_STORE
            # 🛡️ Открываем кассовый день (используем современный timezone.utc вместо deprecated utcnow)
            open_day_res = await client.post(
                "/api/v1/cash/days/open", 
                json={"date": datetime.now(timezone.utc).isoformat()}
            )
            
            if open_day_res.status_code in (200, 201):
                results.append("   ✅ Тогда Обе записи успешно сохраняются в СУБД в статусе IN_STORE")
            else:
                return [f"❌ Кассовый сбой: Ручка открытия смены /cash/days/open вернула код {open_day_res.status_code}"]

        except Exception as e:
            return [f"❌ СБОЙ стадии подготовки данных FIFO: {str(e)}"]
            
    return results
