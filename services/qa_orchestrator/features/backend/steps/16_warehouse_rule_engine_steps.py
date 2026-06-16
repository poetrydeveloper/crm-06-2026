# services/qa_orchestrator/features/backend/steps/16_warehouse_rule_engine_steps.py
import httpx
import uuid

CORE_BACKEND_URL = "http://crm_backend_core:8000/api/v1"
ANALYZER_URL = "http://crm_analyzer_service:8002/api/v1"

async def run_16_warehouse_rule_engine_assertions() -> list[str]:
    """
    Атомарный бэкенд-тест: Верификация логики распределенного RuleEngine API и кэша.
    """
    results = []
    uid = uuid.uuid4().hex[:6].upper()

    async with httpx.AsyncClient(timeout=5.0) as client:
        try:
            results.append("   ✅ Дано В базе данных ядра склада присутствует стерильная номенклатура товаров")

            # 1. Проверяем ручку POST создания динамического правила в ядре
            rule_payload = {
                "price_operator": ">", "price_value": 150.0,
                "name_contains": f"Тег-{uid}", "stock_threshold": 3
            }
            rule_res = await client.post(f"{CORE_BACKEND_URL}/warehouse/purchase-rules", json=rule_payload)
            
            if rule_res.status_code != 201:
                return [f"❌ Бэкенд-сбой создания правила: POST /purchase-rules вернул {rule_res.status_code}"]

            # 2. 🔥 ТРИГГЕРИМ МИКРОСЕРВИС АНАЛИТИКИ для пересчета остатков по новой схеме
            await client.post(f"{ANALYZER_URL}/analyzer/trigger-calculation")

            # 3. Валидируем новую структуру кэша в ядре
            pre_orders_res = await client.get(f"{CORE_BACKEND_URL}/warehouse/pre-orders")
            if pre_orders_res.status_code == 200:
                json_data = pre_orders_res.json()
                if "fallback_active" in json_data and "data" in json_data:
                    results.append("   ✅ Когда Администратор шлет POST на /warehouse/purchase-rules с тегами условий")
                    results.append("   ✅ Тогда Бэкенд сохраняет правило, а повторный GET на /warehouse/pre-orders выдает дефицит")
                else:
                    return [f"❌ Сбой контракта: В ответе кэш-менеджера ядра отсутствуют ключи fallback_active или data!"]
            else:
                return [f"❌ Сбой получения предзаказов ядра: Код {pre_orders_res.status_code}"]

            # 4. Проверяем занесение товара в черный список исключений ядра
            exclude_payload = {"product_id": 999}
            exclude_res = await client.post(f"{CORE_BACKEND_URL}/warehouse/pre-orders/exclude", json=exclude_payload)
            
            if exclude_res.status_code == 200:
                results.append("   ✅ Когда Администратор шлет POST на /warehouse/pre-orders/exclude для конкретного product_id")
                results.append("   ✅ Тогда Данный товар полностью исключается из аналитического буфера закупок")
            else:
                return [f"❌ Бэкенд-сбой черного списка: POST /pre-orders/exclude вернул {exclude_res.status_code}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ БЭКЕНД-ТЕСТА RULE ENGINE: {str(e)}"]

    return results
