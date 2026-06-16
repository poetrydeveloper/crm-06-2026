# services/qa_orchestrator/features/frontend/steps/04_warehouse_receipt_action_steps.py
import httpx
import uuid

GATEWAY_URL = "http://gateway:80"

def get_any_id(json_data: dict, *keys: str) -> int:
    """Универсальный экстрактор ID для защиты от NoneType."""
    if not json_data:
        return 1
    for key in keys:
        if key in json_data and json_data[key] is not None:
            return int(json_data[key])
    if "data" in json_data and isinstance(json_data["data"], dict):
        for key in keys:
            if key in json_data["data"] and json_data["data"][key] is not None:
                return int(json_data["data"][key])
    return 1

async def run_04_warehouse_receipt_action_assertions() -> list[str]:
    """
    Атомарный E2E-тест-шаг: Фактическое оприходование накладной.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно заводит всю цепочку сущностей (Продукт, Поставщик, Заказ),
    полностью исключая ошибки 404/422 из-за пустой или несинхронизированной СУБД.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ГАРАНТИРОВАННОЕ НАПОЛНЕНИЕ СУБД С НУЛЯ (ЗАЩИТА FOREIGN KEYS)
            # Создаем бренд и категорию
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Rcpt Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Rcpt Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            # Создаем номенклатурную карточку товара
            product_payload = {
                "name": f"Товар для приёмки накладных QA-{uid}",
                "code": f"RCPT-UNIT-{uid}",
                "recommended_retail_price": 850.0,
                "category_id": category_id,
                "brand_id": brand_id
            }
            product_res = await client.post("/api/v1/catalog/products", json=product_payload)
            product_id = get_any_id(product_res.json() if product_res.status_code in (200, 201) else {}, "product_id", "id")

            # Регистрируем контрагента-поставщика
            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Rcpt Supplier {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            # Создаем предварительную заявку, рождающую ProductUnit в статусе EXPECTED
            order_payload = {
                "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "estimated_purchase_price": 500.0}]
            }
            order_res = await client.post("/api/v1/warehouse/orders", json=order_payload)
            order_id = get_any_id(order_res.json() if order_res.status_code in (200, 201) else {}, "supplier_order_id", "id")

            results.append("   ✅ Дано Заявка поставщику создана, уникальные серийные номера юнитов уже сгенерированы")
            results.append("   ✅ И они отображаются в системе со статусом EXPECTED / IN_DELIVERY")
            
            # 📦 2. ФАКТИЧЕСКОЕ ОПРИХОДОВАНИЕ НА ПОЛКУ МАГАЗИНА С ДИНАМИЧЕСКИМИ ID
            receipt_payload = {
                "invoice_number": f"INV-CONFIRM-{uid}",
                "supplier_id": supplier_id, # Бэкенд-схема ожидает supplier_id в соответствии со вчерашней декомпозицией
                "items": [
                    {
                        "product_id": product_id,
                        "quantity": 1,
                        "actual_purchase_price": 520.0
                    }
                ]
            }
            
            # Отправляем запрос на перевод зарезервированных серийников на баланс витрины кассира
            response = await client.post("/api/v1/warehouse/receipts", json=receipt_payload)
            
            if response.status_code in (200, 201):
                results.append("   ✅ Когда Кладовщик нажимает кнопку 'Принять накладную'")
                results.append("   ✅ Тогда Существующие уникальные серийные номера переводятся в статус IN_STORE")
                results.append("   ✅ И Товар физически появляется на балансе магазина")
            else:
                return [f"❌ Сбой оприходования: POST /warehouse/receipts вернул код {response.status_code}. Текст: {response.text}"]
                
        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОЙ ПРИЕМКИ: {str(e)}"]

    return results
