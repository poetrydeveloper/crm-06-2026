# 12_cashbox_return_flow_steps.py
import httpx
import uuid
from datetime import datetime

GATEWAY_URL = "http://crm_backend_core:8000/api/v1"

async def run_cashbox_return_flow_assertions():
    """Стадия 7: Автономное тестирование ручки возврата товара по серийному номеру через чистое API"""
    results = []
    uid = uuid.uuid4().hex[:6]
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            # 1. Накатываем инфраструктуру номенклатуры
            brand_res = await client.post("/catalog/brands", json={"name": f"Ret Brand {uid}"})
            brand_id = brand_res.json().get("brand_id")
            category_res = await client.post("/catalog/categories", json={"name": f"Ret Cat {uid}"})
            category_id = category_res.json().get("category_id")
            
            # Указываем жесткий тег "возврат", чтобы потом легко найти товар в каталоге
            prod_payload = {
                "category_id": category_id, "brand_id": brand_id, "code": f"R-{uid}",
                "name": "ключ_на_возврат_toptul", "recommended_retail_price": 600.00, 
                "images": [], "search_aliases": [], "search_tags": ["возврат"]
            }
            prod_res = await client.post("/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id") or prod_res.json().get("id")
            
            sup_res = await client.post("/warehouse/suppliers", json={"name": f"Sup Ret {uid}"})
            supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id")
            
            # 2. ОФИЦИАЛЬНАЯ ПРИЕМКА С АВТОГЕНЕРАЦИЕЙ 1 ЮНИТА НА СКЛАДЕ
            # Наш бэкенд сам сгенерирует UUID-серийник и положит товар на полку в IN_STORE!
            receipt_payload = {
                "supplier_id": supplier_id,
                "invoice_number": f"INV-{uid}",
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 200.00}]
            }
            await client.post("/warehouse/receipts", json=receipt_payload)
            
            # 3. Открываем кассовую смену
            await client.post("/cash/days/open", json={"date": datetime.utcnow().isoformat()})
            
            # 4. Совершаем розничную продажу FIFO
            sale_payload = {
                "product_id": product_id, "customer_id": None, "sale_price": 600.00,
                "amount_cash": 600.00, "amount_card": 0.00, "amount_credit": 0.00
            }
            sale_res = await client.post("/cash/sales", json=sale_payload)
            if sale_res.status_code != 201:
                raise Exception(f"Не удалось продать юнит перед тестом возврата. Код: {sale_res.status_code}, Текст: {sale_res.text}")
                
            # Забираем серийный номер проданного ключа напрямую из ответа кассового чека
            saled_serial = sale_res.json().get("saled_unit_serial")
            if not saled_serial:
                raise Exception("Касса не вернула серийный номер проданного товара!")

            # 5. ВЫЗЫВАЕМ НАШУ НОВУЮ РУЧКУ ВОЗВРАТА ТОВАРА КЛИЕНТА (Операция 0501)
            return_payload = {
                "unique_serial_number": saled_serial,
                "return_reason": "Ошибка подбора размера"
            }
            return_res = await client.post("/cash/returns", json=return_payload)
            if return_res.status_code != 200:
                raise Exception(f"Ручка возврата ответила ошибкой. Код: {return_res.status_code}, Текст: {return_res.text}")
                
            results.append("✔️ Шаг 'Запрос на возврат товара по серийному номеру успешно обработан' — ПРОЙДЕН")

            # 6. ПРОВЕРЯЕМ КОРРЕКТНОСТЬ КАССОВЫХ ОСТАТКОВ ЧЕРЕЗ УМНЫЙ ПОИСК
            search_res = await client.get("/catalog/search", params={"q": "возврат"})
            catalog_output = search_res.json()
            target_product = next((p for p in catalog_output if p.get("id") == product_id), None)
            
            if not target_product or target_product.get("available_qty") != 1:
                raise Exception(f"Остаток не увеличился обратно после возврата! Прилетело: {target_product.get('available_qty') if target_product else 0}")
                
            results.append("✔️ Шаг 'Физический статус юнита возвращен в IN_STORE, остаток равен 1' — ПРОЙДЕН")
            await client.post("/cash/days/close")

        except Exception as e:
            return [f"❌ СБОЙ стадии тестирования возврата товара: {str(e)}"]
            
    return results
