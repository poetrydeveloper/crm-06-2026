# services/core/src/components/rule_engine.py
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import PurchaseRule

class RuleEngine:
    @staticmethod
    async def add_rule(payload, db: AsyncSession) -> dict:
        """🛠️ Добавление нового правила из тегов напрямую в таблицы PostgreSQL"""
        new_rule = PurchaseRule(
            price_operator=payload.price_operator,
            price_value=payload.price_value,
            name_contains=payload.name_contains.lower() if payload.name_contains else None,
            stock_threshold=payload.stock_threshold
        )
        db.add(new_rule)
        await db.commit()
        return {"status": "success", "rule_id": new_rule.id, "message": "Аналитическое правило успешно записано в СУБД PostgreSQL"}

    @staticmethod
    async def get_rules(db: AsyncSession) -> list[dict]:
        """📋 Получение всех активных тегов-правил из базы данных ядра"""
        stmt = select(PurchaseRule)
        result = await db.execute(stmt)
        rules = result.scalars().all()
        
        # Если директор только развернул систему и СУБД стерильна, отдаем базовую матрицу-фоллбэк
        if not rules:
            return [
                {"id": 1, "price_operator": ">", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
                {"id": 2, "price_operator": "<", "price_value": 10.0, "name_contains": "бита", "stock_threshold": 5}
            ]
            
        return [
            {
                "id": r.id,
                "price_operator": r.price_operator,
                "price_value": r.price_value,
                "name_contains": r.name_contains,
                "stock_threshold": r.stock_threshold
            } for r in rules
        ]
