# services/analyzer/analytics_modules/deficit_engine.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

class DeficitEngine:
    @staticmethod
    async def run_calculation(engine: AsyncEngine) -> list[dict]:
        """
        Тяжелый аналитический расчет дефицита снабжения розницы.
        Вычитывает остатки напрямую из СУБД Postgres и применяет Rule Engine.
        """
        pre_orders = []
        
        async with engine.connect() as conn:
            try:
                # Читаем карточки продуктов из базы данных
                prod_res = await conn.execute(text("SELECT id, name, code, recommended_retail_price FROM products;"))
                products = prod_res.fetchall()

                # Текущая эталонная матрица правил
                mock_rules = [
                    {"id": 1, "price_operator": ">", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
                    {"id": 2, "price_operator": "<", "price_value": 10.0, "name_contains": "бита", "stock_threshold": 5}
                ]

                for p in products:
                    p_id, p_name, p_code, p_price = p, p, p, float(p or 0)
                    
                    # Считаем остаток физических юнитов на полках (IN_STORE) напрямую в СУБД Postgres
                    count_res = await conn.execute(text(
                        "SELECT COUNT(id) FROM product_units WHERE product_id = :p_id AND physical_status = 'IN_STORE';"
                    ), {"p_id": p_id})
                    current_stock = count_res.scalar() or 0

                    name_lower = (p_name or "").lower()
                    is_deficit = False
                    matched_rule_id = 0
                    stock_limit = 0
                    recommended_qty = 5

                    # Сверяем пороговые значения
                    for rule in mock_rules:
                        price_match = False
                        if rule["price_operator"] == ">" and p_price > rule["price_value"]:
                            price_match = True
                        elif rule["price_operator"] == "<" and p_price < rule["price_value"]:
                            price_match = True

                        name_match = True
                        if rule["name_contains"] and rule["name_contains"] not in name_lower:
                            name_match = False

                        if price_match and name_match:
                            if current_stock < rule["stock_threshold"]:
                                is_deficit = True
                                matched_rule_id = rule["id"]
                                stock_limit = rule["stock_threshold"]
                                recommended_qty = 15 if "бита" in name_lower else 2
                                break

                    if is_deficit:
                        pre_orders.append({
                            "pre_order_id": 6000 + p_id,
                            "product_id": p_id,
                            "product_name": p_name,
                            "product_code": p_code,
                            "risk_level": f"🚨 Сработало Правило #{matched_rule_id} (Порог < {stock_limit} шт.) [В наличии: {current_stock} шт]",
                            "recommended_qty": recommended_qty,
                            "estimated_purchase_price": p_price * 0.6
                        })

            except Exception as e:
                print(f"Критический сбой прямого СУБД-анализа остатков: {str(e)}")

        return pre_orders
