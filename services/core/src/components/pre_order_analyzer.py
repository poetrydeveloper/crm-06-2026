# services/core/src/components/pre_order_analyzer.py
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product

class PreOrderAnalyzer:
    @staticmethod
    async def get_mock_pre_orders(db: AsyncSession) -> list[dict]:
        """
        Атомарная функция: Имитирует сигналы дефицита от аналитики.
        Сканирует карточки товаров и генерирует рекомендации для закупки.
        """
        stmt = select(Product).limit(3)
        result = await db.execute(stmt)
        products = result.scalars().all()

        pre_orders = []
        for idx, p in enumerate(products):
            pre_orders.append({
                "pre_order_id": 200 + idx,
                "product_id": p.id,
                "product_name": p.name,
                "product_code": p.code,
                "risk_level": "ВЫСОКИЙ ДЕФИЦИТ" if idx == 0 else "СРЕДНИЙ РИСК",
                "recommended_qty": 10 if idx == 0 else 5,
                "estimated_purchase_price": float(p.recommended_retail_price) * 0.6
            })
            
        if not pre_orders:
            pre_orders.append({
                "pre_order_id": 201, 
                "product_id": 1, 
                "product_name": "Ключ рожковый 10мм Toptul",
                "product_code": "КЛ-10-ТП", 
                "risk_level": "КРИТИЧЕСКИЙ ОСТАТОК", 
                "recommended_qty": 15, 
                "estimated_purchase_price": 250.00
            })
        return pre_orders
