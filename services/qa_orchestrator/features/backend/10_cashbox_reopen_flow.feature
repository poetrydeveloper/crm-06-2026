# 10_cashbox_reopen_flow_steps.py
import httpx
import uuid
import asyncpg
from datetime import datetime

GATEWAY_URL = "http://backend:8000"
DATABASE_URL = "postgresql://crm_admin:crm_secure_password@db:5432/crm_main_database"

async def run_cashbox_reopen_flow_assertions():
    """Стадия 4: Тестирование ручки /reopen и дозаписи чеков строго через API ядра"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Накатываем инфраструктуру
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Fi Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/api/v1/catalog/categories", json={"name": f"Fi Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"F-{uid}",
                "name": f"Товар_{uid}", "recommended_retail_price": 500.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Sup Fi {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            # 2. Формируем заявку поставщику (в этот момент ядро само генерирует ProductUnit в статусе IN_REQUEST)
            await client.post("/api/v1/warehouse/orders", json={
                "supplier_id": supplier_id, "items": [{"product_id": product_id, "quantity": 1}]
            })
            
            # 3. Как QA-оркестратор вытаскиваем из СУБД сгенерированный серийный номер для накладной
            conn = await asyncpg.connect(DATABASE_URL)
            serial_row = await conn.fetchrow("SELECT unique_serial_number FROM product_units WHERE product_id = $1 LIMIT 1;", product_id)
            await conn.close()
            
            if not serial_row:
                raise Exception("Ядро бэкенда не создало ProductUnit при формировании заказа!")
            serial_number = serial_row["unique_serial_number"]
            
            # 4. ОФИЦИАЛЬНО ПРИНИМАЕМ НАКЛАДНУЮ ПО ВСЕМ ПРАВИЛАМ СКЛАДА!
            receipt_payload = {
                "supplier_id": supplier_id,
                "invoice_number": f"INV-{uid}",
                "items": [{"unique_serial_number": serial_number, "actual_purchase_price": 100.00}]
            }
            receipt_res = await client.post("/api/v1/warehouse/receipts", json=receipt_payload)
            if receipt_res.status_code != 200:
                raise Exception(f"Ручка приемки склада отвергла накладную! Код: {receipt_res.status_code}, Текст: {receipt_res.text}")

            # 5. Открываем день, фиксируем cash_day_id и закрываем кассу
            open_res = await client.post("/api/v1/cash/days/open", json={"date": datetime.utcnow().isoformat()})
            cash_day_id = open_res.json().get("cash_day_id")
            await client.post("/api/v1/cash/days/close")

            # 6. Переоткрываем кассу через официальный /reopen
            await client.post(f"/api/v1/cash/days/{cash_day_id}/reopen")

            # 7. Проверяем дозапись чека по FIFO
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            sale_res = await client.post("/api/v1/cash/sales", json=sale_payload)
            if sale_res.status_code != 201:
                raise Exception(f"Дозапись не удалась. Код: {sale_res.status_code}, Текст: {sale_res.text}")

            results.append("✔️ Шаг 'Переоткрытие кассового дня и дозапись чеков' — ПРОЙДЕН")
            await client.post("/api/v1/cash/days/close")
        except Exception as e:
            return [f"❌ СБОЙ сценария переоткрытия смены: {str(e)}"]
            
    return results
