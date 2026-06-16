# services/analyzer/analytics_modules/deficit_engine.py
import httpx
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

# Сервис ядра в docker-compose называется backend
CORE_URL = "http://backend:8000/warehouse"

class DeficitEngine:
    @staticmethod
    async def run_calculation(engine: AsyncEngine) -> list[dict]:
        """
        🔥 УЛЬТРА-ИНТЕЛЛЕКТУАЛЬНЫЙ АВТОЗАКАЗ:
        Выкачивает составленные директором правила по сети, сканирует СУБД 
        и отсекает черный список исключений.
        """
        pre_orders = []
        
        # 📡 1. СЕТЕВОЙ ВЫКАЧ ЖИВЫХ ПРАВИЛ ИЗ КОНСТРУКТОРА ЯДРА
        active_rules = []
        exceptions = set()
        
        async with httpx.AsyncClient() as client:
            try:
                # Скачиваем правила из тегов, отправленные вами с фронтенда
                rules_res = await client.get(f"{CORE_URL}/purchase-rules", timeout=1.5)
                if rules_res.status_code == 200:
                    active_rules = rules_res.json()
                
                # Скачиваем черный список (товары с галочкой "Больше не находить")
                exc_res = await client.get(f"{CORE_URL}/purchase-exceptions-raw", timeout=1.5)
                if exc_res.status_code == 200:
                    exceptions = set(exc_res.json())
            except Exception as e:
                print(f"⚠️ Ошибка сбора конфигурации RuleEngine от ядра: {str(e)}")

        # Если сеть отвалилась, используем железный безопасный фоллбэк розницы
        if not active_rules:
            active_rules = [
                {"id": 1, "price_operator": ">", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
                {"id": 2, "price_operator": "<", "price_value": 10.0, "name_contains": "бита", "stock_threshold": 5}
            ]

        # 🛠️ 2. ПРЯМОЙ СУБД-АНАЛИЗ ОСТАТКОВ
        async with engine.connect() as conn:
            try:
                prod_res = await conn.execute(text("SELECT id, name, code, recommended_retail_price FROM products;"))
                products = prod_res.fetchall()

                for p in products:
                    p_id, p_name, p_code, p_price = p[0], p[1], p[2], float(p[3] or 0)
                    
                    # Если на товар нажата ГАЛОЧКА — полностью баним его в выдачах
                    if p_id in exceptions:
                        continue

                    # Высчитываем реальный розничный остаток на витрине
                    count_res = await conn.execute(text(
                        "SELECT COUNT(id) FROM product_units WHERE product_id = :p_id AND physical_status = 'IN_STORE';"
                    ), {"p_id": p_id})
                    current_stock = count_res.scalar() or 0

                    name_lower = (p_name or "").lower()
                    is_deficit = False
                    matched_rule_id = 0
                    stock_limit = 0
                    recommended_qty = 5

                    # Прогоняем товар через скачанные ЖИВЫЕ правила из конструктора
                    for rule in active_rules:
                        price_match = False
                        rule_price = float(rule.get("price_value", 0))
                        
                        if rule.get("price_operator") == ">" and p_price > rule_price:
                            price_match = True
                        elif rule.get("price_operator") == "<" and p_price < rule_price:
                            price_match = True

                        name_match = True
                        keyword = rule.get("name_contains")
                        if keyword and keyword.lower() not in name_lower:
                            name_match = False

                        if price_match and name_match:
                            if current_stock < int(rule.get("stock_threshold", 0)):
                                is_deficit = True
                                matched_rule_id = rule.get("id", 0)
                                stock_limit = rule.get("stock_threshold", 0)
                                recommended_qty = 15 if "бита" in name_lower else 2
                                break

                    if is_deficit:
                        pre_orders.append({
                            "pre_order_id": 6000 + p_id,
                            "product_id": p_id,
                            "product_name": p_name,
                            "product_code": p_code,
                            "risk_level": f"🚨 Правило #{matched_rule_id} (Порог < {stock_limit} шт.) [На полке: {current_stock} шт]",
                            "recommended_qty": recommended_qty,
                            "estimated_purchase_price": p_price * 0.6
                        })

            except Exception as e:
                print(f"Критический сбой прямого СУБД-анализа остатков: {str(e)}")

        return pre_orders
