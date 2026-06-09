import httpx
from datetime import datetime

GATEWAY_URL = "http://gateway:80"

async def run_catalog_story_assertions():
    """Функция-исполнитель, которая прогоняет сквозной сценарий по шагам"""
    results = []
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        
        # Шаг 1: Дано Бэкенд Core доступен
        try:
            res = await client.get("/api/v1/healthcheck")
            assert res.status_code == 200
            results.append("✔️ Шаг 'Дано Бэкенд Core доступен' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Шаг 'Дано Бэкенд Core доступен' — СБОЙ ({str(e)})")
            return results

        # Шаг 2: Когда Пользователь создает поставщика
        try:
            sup_data = {"name": f"QA_Форсаж_{int(datetime.utcnow().timestamp())}", "contact_info": "test"}
            res = await client.post("/api/warehouse/suppliers", json=sup_data)
            assert res.status_code == 201
            results.append("✔️ Шаг 'Когда Пользователь создает поставщика' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Шаг 'Когда Пользователь создает поставщика' — СБОЙ ({str(e)})")
            return results

        # Шаг 3: И Создает товар
        try:
            prod_payload = {
                "category_id": 1,
                "brand_id": None,
                "code": f"QA-{int(datetime.utcnow().timestamp())}",
                "name": "Ключ рожковый 10мм Toptul",
                "description": "Тест",
                "recommended_retail_price": 500.00,
                "search_aliases": ["ск 10"]
            }
            res = await client.post("/api/catalog/products", json=prod_payload)
            
            # Шаг 4: Тогда Система возвращает статус 201
            assert res.status_code == 201
            results.append("✔️ Шаг 'Тогда Система возвращает статус 201' — ПРОЙДЕН")
            
            generated_tags = res.json().get("generated_tags", [])
            
            # Шаг 5: И В тегах присутствуют нужные слова
            assert "ключ" in generated_tags
            assert "рожковый" in generated_tags
            assert "10мм" in generated_tags
            results.append("✔️ Шаг 'И В тегах присутствуют ключевые слова' — ПРОЙДЕН")
            
            # Шаг 6: И В тегах отсутствует предлог из 1 буквы
            assert "и" not in generated_tags
            results.append("✔️ Шаг 'И В тегах отсутствует предлог' — ПРОЙДЕН")
            
        except Exception as e:
            results.append(f"❌ Сбой на этапе работы с товаром ({str(e)})")
            
    return results