# services/core/src/routers/warehouse_nodes/units.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import Product, ProductUnit

router = APIRouter(tags=["Склад: Юниты и остатки"])


@router.get("/units/by-category/{category_id}", status_code=200)
async def get_units_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """📦 Возвращает юниты в категории, сгруппированные по товарам"""
    products = (await db.execute(
        select(Product).where(Product.category_id == category_id)
    )).scalars().all()

    result = []
    for product in products:
        qty_stmt = select(func.count(ProductUnit.id)).where(
            ProductUnit.product_id == product.id,
            ProductUnit.physical_status == 'IN_STORE',
            ProductUnit.is_reserved == False
        )
        qty_res = (await db.execute(qty_stmt)).scalar_one()

        units = (await db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == product.id,
                ProductUnit.physical_status == 'IN_STORE'
            ).order_by(ProductUnit.created_at.asc()).limit(20)
        )).scalars().all()

        result.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_code": product.code,
            "recommended_retail_price": float(product.recommended_retail_price or 0),
            "in_stock": qty_res,
            "units": [{
                "unit_id": u.id,
                "unique_serial_number": u.unique_serial_number,
                "purchase_price": float(u.purchase_price or 0),
                "physical_status": u.physical_status.value,
            } for u in units]
        })

    return result