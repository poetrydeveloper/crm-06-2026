from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from src.models import PurchaseRule

class RuleEngine:
    @staticmethod
    async def add_rule(payload, db: AsyncSession) -> dict:
        """🛠️ Добавление нового правила с гарантированной фиксацией в PostgreSQL"""
        # Приводим к нижнему регистру оператор для строгого соответствия с движком аналитики
        op = getattr(payload, "price_operator", "ge").lower()
        # Конвертируем стандартные знаки в enterprise-формат, если нужно
        if op == ">=": op = "ge"
        if op == "<=": op = "le"

        new_rule = PurchaseRule(
            price_operator=op,
            price_value=getattr(payload, "price_value", 500.0),
            name_contains=payload.name_contains.lower() if getattr(payload, "name_contains", None) else None,
            stock_threshold=getattr(payload, "stock_threshold", 2)
        )
        
        try:
            db.add(new_rule)
            # 🔥 ИСПРАВЛЕНО: Явный коммит. Без него СУБД сделает ROLLBACK при закрытии сессии в get_db!
            await db.commit()
            # Обновляем объект, чтобы считать сгенерированный базой ID
            await db.refresh(new_rule)
            return {"status": "success", "rule_id": new_rule.id, "message": "Аналитическое правило успешно записано в СУБД PostgreSQL"}
        except Exception as e:
            await db.rollback()
            return {"status": "error", "message": f"Ошибка сохранения правила: {str(e)}"}

    @staticmethod
    async def get_rules(db: AsyncSession) -> list[dict]:
        """📋 Получение всех активных тегов-правил из базы данных ядра"""
        stmt = select(PurchaseRule).order_by(PurchaseRule.id.desc())
        result = await db.execute(stmt)
        rules = result.scalars().all()
        
        # Если директор ещё не создал ни одного правила, используем базовую матрицу-фоллбэк
        if not rules:
            return [
                {"id": 1, "price_operator": "ge", "price_value": 100.0, "name_contains": None, "stock_threshold": 2},
                {"id": 2, "price_operator": "le", "price_value": 50.0, "name_contains": "бита", "stock_threshold": 5}
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
