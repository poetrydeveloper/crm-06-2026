# 02_brand_steps.py
import httpx
import uuid

GATEWAY_URL = "http://backend:8000/api/v1"

async def run_brand_story_assertions():
    results = []
    uid = uuid.uuid4().hex[:6]
    raw_name = f"Форсаж Инструмент {uid}"
    expected_snake_name = f"форсаж_инструмент_{uid}"
    
    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            res = await client.post("/catalog/brands", json={"name": raw_name, "description": "Тест"})
            assert res.status_code == 201
            created_id = res.json().get("brand_id")
            assert res.json().get("name") == expected_snake_name
            results.append("✔️ Шаг 'Бренд успешно создан и переведен в snake_case' — ПРОЙДЕН")
        except Exception as e:
            return [f"❌ Тест создания бренда — СБОЙ ({str(e)})"]

        try:
            up_payload = {"name": f"Новый Форсаж {uid}", "description": "Обновлено"}
            up_res = await client.put(f"/catalog/brands/{created_id}", json=up_payload)
            assert up_res.status_code == 200
            results.append("✔️ Шаг 'Редактирование названия бренда' — ПРОЙДЕН")
        except Exception as e:
            return results + [f"❌ Тест редактирования бренда — СБОЙ ({str(e)})"]
            
    return results
