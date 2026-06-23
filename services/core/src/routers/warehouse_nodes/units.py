# services/core/src/routers/warehouse_nodes/units.py
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import Product, ProductUnit

router = APIRouter(tags=["Склад: Юниты и остатки"])


@router.get("/units/by-category/{category_id}", status_code=200)
async def get_units_by_category(category_id: int, db: AsyncSession = Depends(get_db)):
    """📦 Возвращает юниты в категории, сгруппированные по товарам (включая разобранные наборы)"""
    products = (await db.execute(
        select(Product).where(Product.category_id == category_id)
    )).scalars().all()

    result = []
    for product in products:
        # Количество IN_STORE (доступно для продажи)
        in_store_qty = (await db.execute(
            select(func.count(ProductUnit.id)).where(
                ProductUnit.product_id == product.id,
                ProductUnit.physical_status == 'IN_STORE',
                ProductUnit.is_reserved == False
            )
        )).scalar_one()

        # Количество IN_DISASSEMBLED (разобранные наборы)
        disassembled_qty = (await db.execute(
            select(func.count(ProductUnit.id)).where(
                ProductUnit.product_id == product.id,
                ProductUnit.physical_status == 'IN_DISASSEMBLED'
            )
        )).scalar_one()

        # Все юниты (IN_STORE + IN_DISASSEMBLED)
        units = (await db.execute(
            select(ProductUnit).where(
                ProductUnit.product_id == product.id,
                ProductUnit.physical_status.in_(['IN_STORE', 'IN_DISASSEMBLED'])
            ).order_by(ProductUnit.created_at.asc()).limit(20)
        )).scalars().all()

        total_in_stock = in_store_qty + disassembled_qty

        result.append({
            "product_id": product.id,
            "product_name": product.name,
            "product_code": product.code,
            "recommended_retail_price": float(product.recommended_retail_price or 0),
            "in_stock": total_in_stock,
            "in_store_qty": in_store_qty,
            "disassembled_qty": disassembled_qty,
            "units": [{
                "unit_id": u.id,
                "unique_serial_number": u.unique_serial_number,
                "purchase_price": float(u.purchase_price or 0),
                "physical_status": u.physical_status.value,
            } for u in units]
        })

    return result


@router.get("/units/{unit_id}/satellites", status_code=200)
async def get_unit_satellites(unit_id: int, db: AsyncSession = Depends(get_db)):
    """🛰️ Получить список сателлитов разобранного набора"""
    satellites = (await db.execute(
        select(ProductUnit).where(ProductUnit.parent_unit_id == unit_id)
    )).scalars().all()

    return {
        "unit_id": unit_id,
        "satellite_ids": [s.id for s in satellites],
        "satellites": [{
            "unit_id": s.id,
            "unique_serial_number": s.unique_serial_number,
            "product_id": s.product_id,
            "purchase_price": float(s.purchase_price or 0),
            "physical_status": s.physical_status.value,
        } for s in satellites]
    }