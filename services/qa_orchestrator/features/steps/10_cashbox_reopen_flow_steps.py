# 10_cashbox_reopen_flow_steps.py
import httpx
import uuid
from datetime import datetime

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_cashbox_reopen_flow_assertions():
    """Стадия 4: Тестирование ручки /reopen и дозаписи чеков"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            brand_res = await client.post("/catalog/brands", json={"name": f"Fi Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/catalog/categories", json={"name": f"Fi Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"F-{uid}",
                "name": f"Товар_{uid}", "recommended_retail_price": 500.00, "images": [], "search_aliases": []
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id")
            
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Fi {uid}"})
            supplier_id = sup_res.json().get("supplier_id")
            
            # Напрямую генерируем штучный остаток через новую ручку receipts!
            await client.post("/warehouse/receipts", json={
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 200.00}]
            })

            open_res = await client.post("/cash/days/open", json={"date": datetime.utcnow().isoformat()})
            cash_day_id = open_res.json().get("cash_day_id")
            await client.post("/cash/days/close")

            await client.post(f"/cash/days/{cash_day_id}/reopen")

            # Пробиваем чек розничной продажи
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 500.00,
                "amount_cash": 500.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            sale_res = await client.post("/cash/sales", json=sale_payload)
            if sale_res.status_code != 201:
                raise Exception(f"Дозапись не удалась. Код: {sale_res.status_code}")

            results.append("✔️ Шаг 'Переоткрытие кассового дня и дозапись чеков' — ПРОЙДЕН")
            await client.post("/cash/days/close")
        except Exception as e:
            return [f"❌ СБОЙ сценария переоткрытия смены: {str(e)}"]
            
    return results
