# services/core/src/components/rule_engine.py
from decimal import Decimal
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product, ProductUnit, PhysicalStatus

# Хранилище в оперативной памяти (буфер) для защиты от поломок миграций Alembic в QA-окружении
MOCK_RULES = [
    {"id": 1, "price_operator": ">", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
    {"id": 2, "price_operator": "<", "price_value": 10.0, "name_contains": "бита", "stock_threshold": 5}
]
MOCK_EXCEPTIONS = set()  # Сюда улетают product_id при нажатии галочки "Больше не находить"

class RuleEngine:
    @staticmethod
    async def add_rule(payload, db: AsyncSession) -> dict:
        """🛠️ Добавление нового правила из тегов в матрицу снабжения"""
        rule_id = len(MOCK_RULES) + 1
        MOCK_RULES.append({
            "id": rule_id,
            "price_operator": payload.price_operator,
            "price_value": payload.price_value,
            "name_contains": payload.name_contains.lower() if payload.name_contains else None,
            "stock_threshold": payload.stock_threshold
        })
        return {"status": "success", "rule_id": rule_id, "message": "Правило успешно интегрировано"}

    @staticmethod
    async def get_rules() -> list[dict]:
        """📋 Получение всех активных тегов-правил"""
        return MOCK_RULES

    @staticmethod
    async def add_exception(product_id: int) -> dict:
        """🚫 Занесение product_id в черный список исключений по клику на галочку"""
        MOCK_EXCEPTIONS.add(product_id)
        return {"status": "success", "message": f"Товар #{product_id} заблокирован в предзаказах"}

    @staticmethod
    async def get_exceptions() -> list[int]:
        return list(MOCK_EXCEPTIONS)

    @staticmethod
    async def evaluate_deficit_pre_orders(db: AsyncSession) -> list[dict]:
        """
        🔥 СЕРДЦЕ УМНОГО АВТОЗАКА: Перебирает товары каталога, прогоняет их
        через конструктор тегов-правил и строго отсекает забаненные исключения.
        """
        prod_stmt = select(Product)
        prod_res = await db.execute(prod_stmt)
        products = prod_res.scalars().all()

        pre_orders = []

        for p in products:
            # 🛑 ПРАВИЛО ИСКЛЮЧЕНИЯ: Если на товар нажали галочку — полностью игнорируем его
            if p.id in MOCK_EXCEPTIONS:
                continue

            # Считаем текущий остаток физических юнитов на полках (IN_STORE)
            count_stmt = select(func.count(ProductUnit.id)).where(
                ProductUnit.product_id == p.id,
                ProductUnit.physical_status == PhysicalStatus.IN_STORE
            )
            count_res = await db.execute(count_stmt)
            current_stock = count_res.scalar() or 0

            price = float(p.recommended_retail_price or 0)
            name_lower = (p.name or "").lower()

            is_deficit = False
            matched_rule_id = 0
            stock_limit = 0
            recommended_qty = 5

            # Проверяем товар на соответствие составленным вами правилам-тегам
            for rule in MOCK_RULES:
                price_match = False
                if rule["price_operator"] == ">" and price > rule["price_value"]:
                    price_match = True
                elif rule["price_operator"] == "<" and price < rule["price_value"]:
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
                    "pre_order_id": 4000 + p.id,
                    "product_id": p.id,
                    "product_name": p.name,
                    "product_code": p.code,
                    "risk_level": f"🚨 Сработало Правило #{matched_rule_id} (Порог < {stock_limit} шт.) [В наличии: {current_stock} шт]",
                    "recommended_qty": recommended_qty,
                    "estimated_purchase_price": price * 0.6
                })

        return pre_orders
