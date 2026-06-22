# services/core/src/routers/warehouse_nodes/warehouse_orders.py
from datetime import datetime, timedelta, date
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from src.database import get_db
from src.models import Product, Supplier, ProductUnit

router = APIRouter(tags=["Склад: Активные заявки"])


@router.get("/orders/active", status_code=200)
async def list_active_orders(days: int = Query(10, ge=1, le=365), db: AsyncSession = Depends(get_db)):
    """📋 Активные заявки за последние N дней (только те, где есть EXPECTED юниты)"""
    since_date = datetime.utcnow() - timedelta(days=days)

    # Находим заявки с EXPECTED юнитами за период
    active_result = (await db.execute(
        select(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at).label("order_date"),
            func.count(ProductUnit.id).label("expected_count")
        )
        .where(
            ProductUnit.physical_status == 'EXPECTED',
            ProductUnit.created_at >= since_date
        )
        .group_by(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at)
        )
        .order_by(func.date(ProductUnit.created_at).desc(), ProductUnit.supplier_id)
    )).all()

    if not active_result:
        return {"orders": []}

    order_keys = [(row[0], row[1]) for row in active_result]  # (supplier_id, order_date как date)
    supplier_ids = set(row[0] for row in active_result)

    suppliers_map = {}
    if supplier_ids:
        supp_res = (await db.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))).scalars().all()
        for s in supp_res:
            suppliers_map[s.id] = s.name

    orders = []
    for supplier_id, order_date_val in order_keys:
        # Получаем все юниты этой заявки (EXPECTED + IN_STORE)
        units = (await db.execute(
            select(ProductUnit).where(
                ProductUnit.supplier_id == supplier_id,
                func.date(ProductUnit.created_at) == order_date_val
            ).order_by(ProductUnit.created_at.asc())
        )).scalars().all()

        # Группируем по товарам
        products_map = {}
        for u in units:
            if u.product_id not in products_map:
                product = await db.get(Product, u.product_id)
                products_map[u.product_id] = {
                    "product_id": u.product_id,
                    "product_name": product.name.replace("_", " ") if product else f"Товар #{u.product_id}",
                    "product_code": product.code if product else "—",
                    "units": [],
                    "expected_count": 0,
                    "total_count": 0,
                }
            products_map[u.product_id]["units"].append({
                "unit_id": u.id,
                "unique_serial_number": u.unique_serial_number,
                "purchase_price": float(u.purchase_price or 0),
                "physical_status": u.physical_status.value if u.physical_status else "EXPECTED",
            })
            products_map[u.product_id]["total_count"] += 1
            if u.physical_status.value == "EXPECTED":
                products_map[u.product_id]["expected_count"] += 1

        total_financial_load = sum(
            sum(unit["purchase_price"] for unit in p["units"]) for p in products_map.values()
        )

        orders.append({
            "order_key": f"{order_date_val}_{supplier_id}",
            "order_date": str(order_date_val),
            "supplier_id": supplier_id,
            "supplier_name": suppliers_map.get(supplier_id, f"Поставщик #{supplier_id}"),
            "total_financial_load": total_financial_load,
            "products": list(products_map.values()),
        })

    return {"orders": orders}