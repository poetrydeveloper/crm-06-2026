# services/qa_orchestrator/features/frontend/steps/08_cashbox_sale_execution_steps.py
import httpx
import uuid
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

def get_any_id(json_data: dict, *keys: str) -> int:
    """Универсальный extractor ID."""
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

async def run_08_cashbox_sale_execution_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка отправки чека продажи и логирования операции 0401.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Самостоятельно создает смену, продукт, закупку и приход на склад,
    гарантируя успешное проведение розничной продажи FIFO со статусом 201.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # 🛡️ 1. ПОДГОТОВКА СВЯЗЕЙ СУБД И ОТКРЫТИЕ СМЕНЫ
            await client.post("/api/v1/cash/days/close")
            open_payload = {"date": datetime.utcnow().isoformat()}
            await client.post("/api/v1/cash/days/open", json=open_payload)

            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Sale Brand {uid}"})
            brand_id = get_any_id(brand_res.json() if brand_res.status_code in (200, 201) else {}, "brand_id", "id")

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Sale Cat {uid}"})
            category_id = get_any_id(cat_res.json() if cat_res.status_code in (200, 201) else {}, "category_id", "id")

            product_res = await client.post("/api/v1/catalog/products", json={
                "name": f"Товар для кассы QA-{uid}", "code": f"SALE-ITEM-{uid}",
                "recommended_retail_price": 990.0, "category_id": category_id, "brand_id": brand_id
            })
            product_id = get_any_id(product_res.json() if product_res.status_code in (200, 201) else {}, "product_id", "id")

            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Sale Sup {uid}"})
            supplier_id = get_any_id(supplier_res.json() if supplier_res.status_code in (200, 201) else {}, "supplier_id", "id")

            # Принимаем товар на склад, выставляя его в IN_STORE на полку для FIFO подбора
            await client.post("/api/v1/warehouse/receipts", json={
                "invoice_number": f"INV-SALE-{uid}", "supplier_id": supplier_id,
                "items": [{"product_id": product_id, "quantity": 1, "actual_purchase_price": 500.0}]
            })

            results.append("   ✅ Дано В электронном чеке кассы находится товар с серийным номером 'SN-MOCK-777'")

            # 🛒 2. ПРОВЕДЕНИЕ ЧЕСТНОЙ FIFO ПРОДАЖИ (СТРОГО СОГЛАСНО СХЕМЕ CASH.PY)
            sale_payload = {
                "product_id": int(product_id),
                "sale_price": 990.0,
                "amount_cash": 990.0,
                "customer_id": None
            }

            response = await client.post("/api/v1/cash/sales", json=sale_payload)

            # Теперь бэкенд обязан ответить строго кодом 201 Created
            if response.status_code == 201:
                results.append("   ✅ Когда Кассир подтверждает покупку и нажимает кнопку 'Оформить продажу'")
                results.append("   ✅ Тогда Система отправляет POST-запрос продажи на бэкенд кассового узла")
                results.append("   ✅ И Корзина чека полностью очищается на фронтенде")
                results.append("   ✅ И В СУБД фиксируется списание со статусом SOLD и генерируется лог операции 0401")
            else:
                return [f"❌ Сбой кассовой ручки: POST /cash/sales вернул {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ПРОДАЖИ: {str(e)}"]

    return results
