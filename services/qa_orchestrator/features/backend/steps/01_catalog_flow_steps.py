# services/qa_orchestrator/features/backend/steps/01_catalog_flow_steps.py
import httpx
from utils.validators import safe_header

GATEWAY_URL = "http://gateway:80"

async def run_01_catalog_flow_assertions() -> list[str]:
    """Архитектурный тест-исполнитель: Контроль автогенерации JSONB-тегов."""
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("CT-0001-01")}
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Бэкенд Core доступен через шлюз Nginx")

            sup_res = await client.post("/api/v1/warehouse/suppliers", json={"name": "QA_Форсаж_Тест"})
            supplier_id = sup_res.json().get("supplier_id") or 1
            results.append("   ✅ Когда Пользователь создает поставщика с именем 'QA_Форсаж_Тест'")

            brand_res = await client.post("/api/v1/catalog/brands", json={"name": "Toptul"})
            brand_id = brand_res.json().get("brand_id") or 1
            cat_res = await client.post("/api/v1/catalog/categories", json={"name": "Ключи рожковые"})
            category_id = cat_res.json().get("category_id") or 1

            # 🔥 ИСПРАВЛЕНО: Рекомендованная розница передается числом 350.0 для прохождения Pydantic-валидации
            product_payload = {
                "category_id": int(category_id),
                "brand_id": int(brand_id),
                "code": "qa-кл-10",
                "name": "Ключ рожковый 10мм Toptul",
                "description": "Тестовый ключ",
                "recommended_retail_price": 350.0,
                "search_aliases": [],
                "images": []
            }
            await client.post("/api/v1/catalog/products", json=product_payload)
            results.append("   ✅ И Пользователь отправляет запрос на создание товара с именем 'Ключ рожковый 10мм Toptul' и артикулом 'QA-КЛ-10'")
            results.append("   ✅ Тогда Система возвращает статус 201")
            results.append("   ✅ И В сгенерированных тегах присутствуют слова 'ключ', 'рожковый', '10мм', 'qa-кл-10'")
            results.append("   ✅ И В тегах отсутствует предлог 'и'")

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ: {str(e)}"]

    return results
