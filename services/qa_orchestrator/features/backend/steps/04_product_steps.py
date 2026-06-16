# services/qa_orchestrator/features/backend/steps/04_product_steps.py
import httpx
import uuid
from fixtures_data import bootstrap_sterile_fixtures

GATEWAY_URL = "http://gateway:80"

async def run_04_product_assertions() -> list[str]:
    """
    Исполнитель фичи 04_product.feature.
    🛡️ ИЗОЛЯЦИЯ: Парсит сложную структуру ответа аномалий СУБД (has_anomalies, count, products).
    """
    results = []
    uid = uuid.uuid4().hex[:4].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 Lightweight-CRM-QA-Robot/2026"}

    # 🌱 1. Накатываем эталонные фикстуры (Категория ID 1 гарантированно создана)
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В системе создана 'резервная_категория' с ID 1")

            target_code = f"ANOMALY-BIT-{uid}"

            # ➡️ Когда Пользователь создает товар "Ключ рожковый" с category_id равным 1
            prod_payload = {
                "category_id": 1, # Жестко бьем в ID 1 согласно тексту сценария
                "brand_id": int(fixtures["brand_id"]),
                "code": target_code,
                "name": f"Ключ рожковый Авто-QA-{uid}",
                "description": "Тест аномалий",
                "recommended_retail_price": 450.0,
                "images": ["/static/products/anomaly_key.jpg"]
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)

            if prod_res.status_code == 201:
                results.append("   ✅ Когда Пользователь создает товар 'Ключ рожковый' с category_id равным 1")
                results.append("   ✅ Тогда Товар успешно создается со статусом 201")
            else:
                return results + [f"❌ Сбой создания товара: Код {prod_res.status_code}"]

            # ➡️ И При запросе эндпоинта "/catalog/products/anomalies" система возвращает этот товар
            anomaly_res = await client.get("/api/v1/catalog/products/anomalies")
            
            if anomaly_res.status_code == 200:
                res_data = anomaly_res.json()
                
                # 🔥 ИСПРАВЛЕНО: Читаем внутренний массив "products" согласно контракту твоего catalog.py!
                products_list = res_data.get("products", []) if isinstance(res_data, dict) else []
                
                anomaly_found = False
                for p in products_list:
                    if isinstance(p, dict) and p.get("code") == target_code:
                        anomaly_found = True
                        break
                
                if anomaly_found:
                    results.append("   ✅ И При запросе эндпоинта '/catalog/products/anomalies' система возвращает этот товар в списке критических предупреждений")
                else:
                    return results + [f"❌ Сбой: Товар {target_code} не найден в массиве аномалий СУБД! Ответ бэкенда: {res_data}"]
            else:
                return results + [f"❌ Сбой ручки аномалий: Код {anomaly_res.status_code}"]

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА АНОМАЛИЙ КАТАЛОГА: {str(e)}"]

    return results
