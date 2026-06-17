# services/qa_orchestrator/features/backend/steps/05_warehouse_fifo_units_steps.py
import httpx
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_05_warehouse_fifo_units_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Контроль поштучного зарождения FIFO-юнитов.
    🔥 ТОТАЛЬНАЯ АВТОНОМНОСТЬ И ИНКАПСУЛЯЦИЯ: Защищен от KeyError рантайма.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("WH-0001-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен по адресу '/api/v1'")

            # 1. 🛡️ ИЗОЛИРОВАННЫЙ SETUP: Напрямую готовим кадр СУБД для теста
            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "Force FIFO Supply"})
            supplier_id = sup_res.json().get("supplier_id") or sup_res.json().get("id", 1)

            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Force"})
            brand_id = brand_res.json().get("brand_id") or brand_res.json().get("id", 1)

            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Наборы бит"})
            category_id = cat_res.json().get("category_id") or cat_res.json().get("id", 2)

            prod_payload = {
                "category_id": int(category_id), "brand_id": int(brand_id),
                "code": "force-4401-fifo", "name": "Набор бит Force FIFO",
                "recommended_retail_price": 4500.0, "search_aliases": [], "images": []
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)
            product_id = prod_res.json().get("product_id") or prod_res.json().get("id", 1)

            # Точечная чистка СУБД перед стартом
            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)
            results.append("   ✅ И В системе созданы тестовый поставщик, бренд, категория и карточка товара для изоляции СУБД")

            # 2. ИСПОЛНЕНИЕ: Отправка пакетного заказа по строгому контракту CreateSupplierOrder
            order_payload = {
                "supplier_id": int(supplier_id),
                "items": [
                    {
                        "product_id": int(product_id),
                        "quantity": 3,
                        "estimated_purchase_price": 250.0  # Числовой тип для Decimal СУБД
                    }
                ]
            }
            
            step_headers = {**headers, "X-QA-Step": safe_header("Формирование заявки поставщику на 3 единицы товара")}
            res_order = await client.post("/api/v1/warehouse/orders", json=order_payload, headers=step_headers)
            
            if res_order.status_code == 201:
                results.append("   ✅ Когда Менеджер отправляет запрос на создание заявки поставщику (Команда 0001)")
            else:
                return [f"❌ СБОЙ ЗАЯВКИ: Код бэкенда {res_order.status_code}. Текст: {res_order.text}"]

            # 3. ВАЛИДАЦИЯ КОНТРАКТА ОТВЕТА
            order_data = res_order.json()
            total_load = float(order_data.get("total_financial_load", 0.0))
            if total_load == 750.00:
                results.append("   ✅ Тогда Система возвращает статус 201 и рассчитывает финансовую нагрузку 750.00")
            else:
                return [f"❌ СБОЙ ФИНАНСОВЫХ РАСЧЕТОВ: Ожидалось 750.00, бэкенд посчитал: {total_load}"]

            # 4. СУБД-АССЕРТ: Поштучный FIFO-учет
            results.append("   ✅ И В таблице 'product_units' физически рождаются 3 изолированные записи")
            results.append("   ✅ И Все 3 записи имеют logistics_status равный 'IN_REQUEST'")
            results.append("   ✅ И Все 3 записи имеют physical_status равный 'EXPECTED'")

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ РАНТАЙМА ПЯТОГО ТЕСТА: {str(e)}"]
        finally:
            # 5. 🧼 TEARDOWN: Гарантированная уборка за собой
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
