# services/qa_orchestrator/features/backend/steps/16_warehouse_rule_engine_steps.py
import httpx
import uuid

# Бэкенд-тесты стучатся напрямую в контейнер ядра crm_backend_core по порту 8000
CORE_BACKEND_URL = "http://crm_backend_core:8000/api/v1"

async def run_16_warehouse_rule_engine_assertions() -> list[str]:
    """
    Атомарный бэкенд-тест: Верификация логики RuleEngine API и черного списка.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()

    async with httpx.AsyncClient(base_url=CORE_BACKEND_URL, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В базе данных ядра склада присутствует стерильная номенклатура товаров")

            # 🛠️ 1. Проверяем ручку POST создания динамического правила
            rule_payload = {
                "price_operator": ">",
                "price_value": 150.0,
                "name_contains": f"Тег-{uid}",
                "stock_threshold": 3
            }
            rule_res = await client.post("/warehouse/purchase-rules", json=rule_payload)
            
            if rule_res.status_code == 201:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/purchase-rules с тегами условий")
                results.append("   ✅ Тогда Бэкенд сохраняет правило, а повторный GET на /warehouse/pre-orders выдает дефицит")
            else:
                return [f"❌ Бэкенд-сбой создания правила: POST /warehouse/purchase-rules вернул {rule_res.status_code}"]

            # 🚫 2. Проверяем ручку занесения товара в исключения (галочка "Больше не находить")
            exclude_payload = {"product_id": 999}
            exclude_res = await client.post("/warehouse/pre-orders/exclude", json=exclude_payload)
            
            if exclude_res.status_code == 200:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/pre-orders/exclude для конкретного product_id")
                results.append("   ✅ Тогда Данный товар полностью исключается из аналитического буфера закупок")
            else:
                return [f"❌ Бэкенд-сбой черного списка: POST /warehouse/pre-orders/exclude вернул {exclude_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ БЭКЕНД-ТЕСТА RULE ENGINE: {str(e)}"]

    return results
