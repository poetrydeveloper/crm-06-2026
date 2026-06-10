# brand_steps.py
import httpx
from datetime import datetime

GATEWAY_URL = "http://gateway:80/api/v1"

async def test_brand_lifecycle_and_transformations():
    results = []
    timestamp = int(datetime.utcnow().timestamp())
    raw_name = "Форсаж Инструмент"
    expected_snake_name = "форсаж_инструмент"
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        # 1. Проверяем создание и приведение к snake_case
        try:
            res = await client.post("/catalog/brands", json={"name": raw_name, "description": "Тест"})
            assert res.status_code == 201
            
            # Проверяем справочник брендов, изменилось ли имя
            get_res = await client.get("/catalog/brands")
            brands = [b["name"] for b in get_res.json()]
            assert expected_snake_name in brands
            results.append("✔️ Шаг 'Имя бренда успешно трансформировано в snake_case' — ПРОЙДЕН")
        except Exception as e:
            results.append(f"❌ Тест трансформации бренда — СБОЙ ({str(e)})")
            
    return results
