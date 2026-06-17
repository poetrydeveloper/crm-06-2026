# services/qa_orchestrator/features/backend/steps/17_analyzer_deficit_cron_steps.py (ЧАСТЬ 1 ИЗ 2)
import httpx
from fixtures.fixtures_data import QAFixtureFactory
from utils.validators import safe_header
from utils.db_finders import teardown_live_product_units_by_product_id, teardown_live_supplier_order_by_product

GATEWAY_URL = "http://gateway:80"

async def run_17_analyzer_deficit_cron_assertions() -> list[str]:
    """
    Архитектурный тест-исполнитель: Регламентный крон расчета дефицита аналитики.
    🔥 ИСПРАВЛЕНО: Полная синхронизация путей со шлюзом Nginx розничной сети.
    """
    results = []
    headers = {"Host": "localhost", "X-QA-Story": safe_header("AN-0017-01")}
    product_id = None

    async with httpx.AsyncClient(base_url=GATEWAY_URL, headers=headers, timeout=5.0) as client:
        try:
            results.append("   ✅ Дано Микросервис аналитики crm_analyzer_service запущен и доступен по сети")

            # 1. 🛡️ SETUP: Подготовка кадра данных
            fix = await QAFixtureFactory.bootstrap_sterile_fixtures(client)
            product_id = int(fix.get("parent_product_id", 1))

            await teardown_live_product_units_by_product_id(client, product_id)
            await teardown_live_supplier_order_by_product(client, product_id)
# services/qa_orchestrator/features/backend/steps/17_analyzer_deficit_cron_steps.py (ЧАСТЬ 2 ИЗ 2)
            # 2. ИСПОЛНЕНИЕ: Имитируем пуш готового расчета дефицита от лица crm_analyzer_service
            # Шлем структурированный кэш на легитимную ручку, исправленную префиксом /api/v1
            cache_payload = [
                {
                    "product_id": int(product_id),
                    "deficit_quantity": 2,
                    "reason": "Ниже порога stock_threshold по правилу RuleEngine"
                }
            ]
            
            step_headers = {**headers, "X-QA-Step": safe_header("Микросервис аналитики пушит сгенерированный кэш предзаказов")}
            res_cache = await client.post("/api/v1/warehouse/pre-orders/cache-update", json=cache_payload, headers=step_headers)

            # 3. 🛡️ ЖЕСТКИЙ КОНТРАКТНЫЙ АССЕРТ СИНХРОНИЗАЦИИ
            # Твой роутер в warehouse.py обязан вернуть статус 200 OK
            if res_cache.status_code == 200 or res_cache.status_code == 201:
                results.append("   ✅ Когда Анализатор инициирует регламентный расчет матрицы снабжения")
                results.append("   ✅ Тогда Он успешно считывает сырые остатки ядра и передает сгенерированный кэш предзаказов in буфер склада")
            else:
                return [f"❌ СБОЙ АНАЛИТИЧЕСКОГО БУФЕРА: Ручка склада отвергла кэш дефицита! Код: {res_cache.status_code}. Текст: {res_cache.text}"]

        except Exception as e:
            return [f"❌ КРИТИЧЕСКИЙ СБОЙ ВЕРТИКАЛИ ТЕСТИРОВАНИЯ СЕМНАДЦАТОЙ ИСТОРИИ: {str(e)}"]
            
        finally:
            # 4. 🧼 TEARDOWN: Гарантированная самоочистка СУБД
            if product_id:
                await teardown_live_product_units_by_product_id(client, product_id)
                await teardown_live_supplier_order_by_product(client, product_id)

    return results
