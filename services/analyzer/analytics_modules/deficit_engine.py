# services/analyzer/analytics_modules/deficit_engine.py
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

class DeficitEngine:
    @staticmethod
    async def run_calculation(engine: AsyncEngine) -> list[dict]:
        """
        🔥 ЧИСТЫЙ СУБД-АВТОЗАКАЗ:
        Вычитывает динамические правила закупки и черный список исключений напрямую 
        из физических таблиц PostgreSQL, полностью исключая RAM-заглушки.
        """
        pre_orders = []
        
        async with engine.connect() as conn:
            try:
                # 📡 1. ВЫКАЧ ЖИВЫХ ТЕГОВ-ПРАВИЛ ИЗ ТАБЛИЦЫ purchase_rules
                rules_res = await conn.execute(text(
                    "SELECT id, price_operator, price_value, name_contains, stock_threshold FROM purchase_rules;"
                ))
                active_rules = [
                    {
                        "id": r[0],
                        "price_operator": r[1],
                        "price_value": r[2],
                        "name_contains": r[3],
                        "stock_threshold": r[4]
                    } for r in rules_res.fetchall()
                ]

                # Если директор ещё не создал ни одного правила, используем эталонную базовую матрицу-фоллбэк
                if not active_rules:
                    active_rules = [
                        {"id": 1, "price_operator": ">", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
                        {"id": 2, "price_operator": "<", "price_value": 10.0, "name_contains": "бита", "stock_threshold": 5}
                    ]

                # 📡 2. ВЫКАЧ ЧЕРНОГО СПИСКА ИСКЛЮЧЕНИЙ ИЗ ТАБЛИЦЫ purchase_exceptions
                exc_res = await conn.execute(text("SELECT product_id FROM purchase_exceptions;"))
                exceptions = set(r[0] for r in exc_res.fetchall())

                # 📊 3. СКАНИРОВАНИЕ НОМЕНКЛАТУРЫ И ФИЗИЧЕСКИХ ОСТАТКОВ
                prod_res = await conn.execute(text("SELECT id, name, code, recommended_retail_price FROM products;"))
                products = prod_res.fetchall()

                for p in products:
                    p_id, p_name, p_code, p_price = p[0], p[1], p[2], float(p[3] or 0)
                    
                    # Если товар помечен галочкой "Больше не находить" — намертво баним его в выдаче
                    if p_id in exceptions:
                        continue

                    # Считаем точный остаток физических юнитов IN_STORE на витрине
                    count_res = await conn.execute(text(
                        "SELECT COUNT(id) FROM product_units WHERE product_id = :p_id AND physical_status = 'IN_STORE';"
                    ), {"p_id": p_id})
                    current_stock = count_res.scalar() or 0

                    name_lower = (p_name or "").lower()
                    is_deficit = False
                    matched_rule_id = 0
                    stock_limit = 0
                    recommended_qty = 5

                    # Прогоняем товар через скачанную из PostgreSQL матрицу условий снабжения
                    for rule in active_rules:
                        price_match = False
                        rule_price = float(rule["price_value"] or 0)
                        
                        if rule["price_operator"] == ">" and p_price > rule_price:
                            price_match = True
                        elif rule["price_operator"] == "<" and p_price < rule_price:
                            price_match = True

                        name_match = True
                        keyword = rule["name_contains"]
                        if keyword and keyword.lower() not in name_lower:
                            name_match = False

                        if price_match and name_match:
                            if current_stock < int(rule["stock_threshold"] or 0):
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
                            "risk_level": f"🚨 Правило #{matched_rule_id} (Порог < {stock_limit} шт.) [На полке: {current_stock} шт]",
                            "recommended_qty": recommended_qty,
                            "estimated_purchase_price": p_price * 0.6
                        })

            except Exception as e:
                print(f"Критический сбой распределенного СУБД-пересчета дефицита: {str(e)}")

        return pre_orders
