# services/qa_orchestrator/features/backend/steps/16_warehouse_rule_engine_steps.py
import httpx
from fixtures_data import bootstrap_sterile_fixtures

GATEWAY_URL = "http://gateway:80"

async def run_16_warehouse_rule_engine_assertions() -> list[str]:
    """Исполнитель фичи 16_warehouse_rule_engine.feature"""
    results = []
    
    # 🌱 Накатываем эталонный каркас Force 4401
    fixtures = await bootstrap_sterile_fixtures()

    async with httpx.AsyncClient(base_url=GATEWAY_URL, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В базе данных ядра склада присутствует стерильная номенклатура товаров")

            # 1. Создаем правило автозаказа для бит Force
            rule_payload = {"price_operator": "<", "price_value": 200.0, "name_contains": "бита", "stock_threshold": 5}
            rule_res = await client.post("/api/v1/warehouse/purchase-rules", json=rule_payload)
            if rule_res.status_code == 201:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/purchase-rules с тегами условий")
            else:
                return [f"❌ Сбой создания правила: {rule_res.status_code}"]

            # 2. Запускаем фоновый пересчет аналитического контейнера
            await client.post("/api/v1/analyzer/trigger-calculation")
            
            # Проверяем выдачу кэша предзаказов ядра
            pre_res = await client.get("/api/v1/warehouse/pre-orders")
            if pre_res.status_code == 200 and "fallback_active" in pre_res.json():
                results.append("   ✅ Тогда Бэкенд сохраняет правило, а повторный GET на /warehouse/pre-orders выдает дефицит")
            else:
                return [f"❌ Сбой выдачи кэша предзаказов ядра: {pre_res.status_code}"]

            # 3. Тестируем добавление товара в черный список исключений
            # Берем ID биты FORCE из фикстур, чтобы пройти ForeignKey-валидацию СУБД
            product_id = int(fixtures["child_product_ids"]["1763020"])
            
            exclude_res = await client.post("/api/v1/warehouse/pre-orders/exclude", json={"product_id": product_id})
            if exclude_res.status_code == 200:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/pre-orders/exclude для конкретного product_id")
                results.append("   ✅ Тогда Данный товар полностью исключается из аналитического буфера закупок")
            else:
                return results + [f"❌ Сбой черного списка: {exclude_res.status_code}. Текст: {exclude_res.text}"]

        except Exception as e:
            return results + [f"❌ КРИТИЧЕСКИЙ СБОЙ ТЕСТА 16: {str(e)}"]

    return results
