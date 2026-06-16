# services/qa_orchestrator/features/backend/steps/01_catalog_steps.py
import httpx
import uuid
from fixtures_data import bootstrap_sterile_fixtures  # 🔥 Сидер эталонного каркаса Force 4401

GATEWAY_URL = "http://gateway:80"

async def run_01_catalog_assertions() -> list[str]:
    """
    Исполнитель фичи 01_catalog.feature.
    🛡️ ИЗОЛЯЦИЯ: Перед стартом стерилизует СУБД и штампует эталонный набор Force 4401.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()
    browser_headers = {"Host": "localhost", "User-Agent": "Mozilla/5.0 CRM-QA-Robot/2026"}

    # 🌱 1. Стерилизация и накат эталонной номенклатуры (Смена/Касса/FIFO защищены)
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=browser_headers, timeout=5.0) as client:
        try:
            # ➡️ Дано Бэкенд Core доступен через шлюз Nginx
            health_res = await client.get("/api/v1/healthcheck")
            if health_res.status_code == 200:
                results.append("   ✅ Дано Бэкенд Core доступен через шлюз Nginx")
            else:
                return [f"❌ Сбой: /api/v1/healthcheck вернул код {health_res.status_code}"]

            # ➡️ Когда Пользователь создает поставщика с именем "QA_Форсаж_Тест"
            sup_payload = {"name": f"QA_Форсаж_Тест_{uid}", "contact_info": "Тестовый оптовик"}
            sup_res = await client.post("/api/v1/warehouse/suppliers", json=sup_payload)
            if sup_res.status_code == 201:
                results.append("   ✅ Когда Пользователь создает поставщика с именем 'QA_Форсаж_Тест'")
            else:
                return results + [f"❌ Сбой создания поставщика: Код {sup_res.status_code}"]

            # ➡️ И Пользователь отправляет запрос на создание товара с именем "Ключ рожковый 10мм Toptul"
            prod_payload = {
                "category_id": int(fixtures["category_id"]),
                "brand_id": int(fixtures["brand_id"]),
                "code": f"QA-KL-10-{uid}",
                "name": "Ключ рожковый 10мм Toptul и насадка", # Добавили "и" для проверки фильтра предлогов
                "description": "Автоматическое тестирование лексического парсера",
                "recommended_retail_price": 500.0,
                "images": ["/static/products/key10.jpg"]
            }
            prod_res = await client.post("/api/v1/catalog/products", json=prod_payload)

            # ➡️ Тогда Система возвращает статус 201
            if prod_res.status_code == 201:
                results.append("   ✅ Тогда Система возвращает статус 201")
            else:
                return results + [f"❌ Сбой создания товара: Код {prod_res.status_code}. Текст: {prod_res.text}"]

            # Извлекаем автоматически сгенерированные поисковые теги из ответа ядра СУБД
            generated_tags = prod_res.json().get("generated_tags", [])
            
            # ➡️ И В сгенерированных тегах присутствуют слова "ключ", "рожковый", "10мм", "qa-кл-10"
            assert "ключ" in generated_tags
            assert "рожковый" in generated_tags
            assert "10мм" in generated_tags
            assert f"qa-kl-10-{uid}".lower() in generated_tags
            results.append("   ✅ И В сгенерированных тегах присутствуют слова 'ключ', 'рожковый', '10мм'")

            # ➡️ И В тегах отсутствует предлог "и"
            assert "и" not in generated_tags
            results.append("   ✅ И В тегах отсутствует предлог 'и'")

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА КАТАЛОГА: {str(e)}"]

    return results
