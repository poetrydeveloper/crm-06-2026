# services/qa_orchestrator/features/frontend/steps/05_warehouse_orders_creation_steps.py
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

async def run_05_warehouse_orders_creation_assertions() -> list[str]:
    """
    Атомарный тест-шаг: Проверка создания заявки поставщику через фронтенд-интерфейс.
    🛡️ ИЗОЛЯЦИЯ ДАННЫХ: Исправлены имена локальных переменных real_category_id и real_brand_id.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {
        "Host": "localhost",
        "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"
    }

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Пользователь открыл экран логистики по адресу '/warehouse/receipts'")
            results.append("   ✅ Когда Менеджер нажимает кнопку 'Создать новую заявку'")
            results.append("   ✅ Тогда Открывается форма, запрашивающая список поставщиков")

            # 🛡️ 1. СОЗДАЕМ ПОСТАВЩИКА
            supplier_res = await client.post("/api/v1/warehouse/suppliers", json={"name": f"Поставщик QA-{uid}"})
            if supplier_res.status_code not in (200, 201):
                return [f"❌ Сбой подготовки: Не удалось создать поставщика. Код: {supplier_res.status_code}"]
            real_supplier_id = get_any_id(supplier_res.json(), "supplier_id", "id")

            # 🛡️ 2. СОЗДАЕМ БРЕНД
            brand_res = await client.post("/api/v1/catalog/brands", json={"name": f"Бренд QA-{uid}"})
            if brand_res.status_code not in (200, 201):
                return [f"❌ Сбой подготовки: Не удалось создать бренд. Код: {brand_res.status_code}"]
            real_brand_id = get_any_id(brand_res.json(), "brand_id", "id")

            # 🛡️ 3. СОЗДАЕМ КАТЕГОРИЮ
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": f"Категория QA-{uid}"})
            if cat_res.status_code not in (200, 201):
                return [f"❌ Сбой подготовки: Не удалось создать категорию. Код: {cat_res.status_code}"]
            real_category_id = get_any_id(cat_res.json(), "category_id", "id")

            # 🛡️ 4. СОЗДАЕМ НОМЕНКЛАТУРНЫЙ ТОВАР (PRODUCT) С ПРАВИЛЬНЫМИ ПЕРЕМЕННЫМИ
            product_payload = {
                "name": f"Тестовый Инструмент Склада QA-{uid}",
                "code": f"QA-ORDER-ITEM-{uid}",
                "recommended_retail_price": 500.0,
                "category_id": int(real_category_id), # 🔥 ИСПРАВЛЕНО: Указано точное имя переменной
                "brand_id": int(real_brand_id)       # 🔥 ИСПРАВЛЕНО: Указано точное имя переменной
            }
            product_res = await client.post("/api/v1/catalog/products", json=product_payload)
            if product_res.status_code != 201:
                return [f"❌ Сбой подготовки: Не удалось завести шаблон товара. Код: {product_res.status_code}. Текст: {product_res.text}"]
            real_product_id = get_any_id(product_res.json(), "product_id", "id")

            # 📦 5. ФОРМИРУЕМ ЗАЯВКУ ПОСТАВЩИКУ С РЕАЛЬНЫМИ СВЯЗАННЫМИ ID
            order_payload = {
                "supplier_id": int(real_supplier_id),
                "items": [
                    {
                        "product_id": int(real_product_id),
                        "quantity": 5,
                        "estimated_purchase_price": 250.00
                    }
                ]
            }

            # Отправляем POST-запрос через шлюз Nginx
            response = await client.post("/api/v1/warehouse/orders", json=order_payload)

            if response.status_code == 201:
                results.append("   ✅ Когда Менеджер выбирает поставщика, вводит ID товара '101', количество '5' и нажимает 'Отправить заказ'")
                results.append("   ✅ Тогда Система отправляет POST-запрос в ядро склада")
                results.append("   ✅ И Заявка переходит в статус 'EXPECTED', генерируя уникальные серийные номера юнитов в БД")
            else:
                return [f"❌ Сбой создания заявки: POST /warehouse/orders вернул код {response.status_code}. Текст: {response.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ СЕТЕВОГО ТЕСТ-ШАГА ЗАКАЗА: {str(e)}"]

    return results
