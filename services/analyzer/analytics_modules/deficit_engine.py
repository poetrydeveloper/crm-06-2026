from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncEngine

class DeficitEngine:
    @staticmethod
    async def run_calculation(engine: AsyncEngine) -> list[dict]:
        """
        🔥 СИНХРОНИЗИРОВАННЫЙ СУБД-АВТОЗАКАЗ:
        Поддерживает Enterprise-операторы ge/le и возвращает контрактные поля.
        Оптимизирован для предотвращения InterfaceError (another operation is in progress).
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

                if not active_rules:
                    active_rules = [
                        {"id": 1, "price_operator": "ge", "price_value": 500.0, "name_contains": None, "stock_threshold": 2}
                    ]

                # 📡 2. ВЫКАЧ ЧЕРНОГО СПИСКА ИСКЛЮЧЕНИЙ ИЗ ТАБЛИЦЫ purchase_exceptions
                exc_res = await conn.execute(text("SELECT product_id FROM purchase_exceptions;"))
                exceptions = set(r[0] for r in exc_res.fetchall())

                # 📊 3. СКАНИРОВАНИЕ ОСТАТКОВ ОДНИМ ЗАПРОСОМ (Вместо сотен запросов в цикле!)
                # Группируем по product_id и считаем COUNT для статуса IN_STORE
                stock_res = await conn.execute(text(
                    "SELECT product_id, COUNT(id) FROM product_units WHERE physical_status = 'IN_STORE' GROUP BY product_id;"
                ))
                # Превращаем в быстрый словарь: {product_id: count}
                stock_map = {r[0]: r[1] for r in stock_res.fetchall()}

                # 📊 4. СКАНИРОВАНИЕ НОМЕНКЛАТУРЫ
                prod_res = await conn.execute(text("SELECT id, name, code, recommended_retail_price FROM products;"))
                products = prod_res.fetchall()

                # Закрываем транзакцию/соединение, так как данные уже у нас в памяти,
                # и дальнейшие расчеты не заблокируют СУБД.
                await conn.commit() 

                # 🧮 5. ОБРАБОТКА ДАННЫХ В ПАМЯТИ
                for p in products:
                    p_id, p_name, p_code, p_price = p[0], p[1], p[2], float(p[3] or 0)
                    
                    if p_id in exceptions:
                        continue

                    # Получаем остаток из нашего готового словаря (если товара нет в базе остатков, значит 0)
                    current_stock = stock_map.get(p_id, 0)

                    name_lower = (p_name or "").lower()
                    is_deficit = False
                    matched_rule_id = 0
                    stock_limit = 0

                    for rule in active_rules:
                        price_match = False
                        rule_price = float(rule["price_value"] or 0)
                        op = rule["price_operator"]
                        
                        if op in [">", "ge"] and p_price >= rule_price:
                            price_match = True
                        elif op in ["<", "le"] and p_price <= rule_price:
                            price_match = True
                        elif op is None:
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
                                break

                    if is_deficit:
                        deficit_qty = int(stock_limit) - int(current_stock)
                        if deficit_qty <= 0:
                            deficit_qty = 2

                        pre_orders.append({
                            "product_id": int(p_id),
                            "deficit_quantity": int(deficit_qty),
                            "reason": f"Порог < {stock_limit} шт. по правилу #{matched_rule_id}. На полке: {current_stock} шт."
                        })

            except Exception as e:
                print(f"Критический сбой распределенного СУБД-пересчета дефицита: {str(e)}")

        return pre_orders
