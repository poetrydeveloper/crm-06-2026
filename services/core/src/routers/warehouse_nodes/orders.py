# services/core/src/routers/warehouse_nodes/orders.py
import uuid
from fastapi import APIRouter, Depends, status, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, text, func
from src.database import get_db
from src.models import Product, Supplier, ProductUnit
from src.models.product_unit import LogisticsStatus, PhysicalStatus
from src.schemas.warehouse import CreateSupplierOrder

router = APIRouter(tags=["Склад: Заказы поставщикам и FIFO"])


@router.get("/orders", status_code=200)
async def list_orders(db: AsyncSession = Depends(get_db)):
    """📋 Получить все заявки — активные (EXPECTED) и архив (только завершённые, без EXPECTED)"""
    active_rows = (await db.execute(
        select(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at).label("order_date"),
            ProductUnit.product_id,
            func.count(ProductUnit.id).label("qty"),
            func.avg(ProductUnit.purchase_price).label("avg_price")
        )
        .where(ProductUnit.physical_status == 'EXPECTED')
        .group_by(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at),
            ProductUnit.product_id
        )
        .order_by(func.date(ProductUnit.created_at).desc(), ProductUnit.supplier_id)
    )).all()

    archive_rows = (await db.execute(
        select(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at).label("order_date"),
            ProductUnit.product_id,
            func.count(ProductUnit.id).label("qty"),
            func.avg(ProductUnit.purchase_price).label("avg_price")
        )
        .where(ProductUnit.physical_status == 'IN_STORE')
        .group_by(
            ProductUnit.supplier_id,
            func.date(ProductUnit.created_at),
            ProductUnit.product_id
        )
        .order_by(func.date(ProductUnit.created_at).desc(), ProductUnit.supplier_id)
    )).all()

    stock_result = (await db.execute(
        select(
            ProductUnit.product_id,
            func.count(ProductUnit.id).label("total_stock")
        )
        .where(ProductUnit.physical_status == 'IN_STORE')
        .group_by(ProductUnit.product_id)
    )).all()
    stock_map = {row[0]: row[1] for row in stock_result}

    all_orders_result = (await db.execute(
        select(
            ProductUnit.product_id,
            func.count(ProductUnit.id).label("total_ordered")
        )
        .where(ProductUnit.physical_status.in_(['EXPECTED', 'IN_STORE']))
        .group_by(ProductUnit.product_id)
    )).all()
    all_orders_map = {row[0]: row[1] for row in all_orders_result}

    supplier_ids = set()
    product_ids = set()
    for row in active_rows:
        supplier_ids.add(row[0])
        product_ids.add(row[2])
    for row in archive_rows:
        supplier_ids.add(row[0])
        product_ids.add(row[2])

    suppliers_map = {}
    if supplier_ids:
        supp_res = (await db.execute(select(Supplier).where(Supplier.id.in_(supplier_ids)))).scalars().all()
        for s in supp_res:
            suppliers_map[s.id] = s.name

    products_map = {}
    if product_ids:
        prod_res = (await db.execute(select(Product).where(Product.id.in_(product_ids)))).scalars().all()
        for p in prod_res:
            products_map[p.id] = {"name": p.name, "code": p.code}

    def build_order_items(rows):
        orders = {}
        for row in rows:
            supplier_id = row[0]
            order_date = str(row[1])
            product_id = row[2]
            qty = row[3]
            avg_price = float(row[4]) if row[4] else 0.0

            key = f"{order_date}_{supplier_id}"
            if key not in orders:
                orders[key] = {
                    "order_key": key,
                    "order_date": order_date,
                    "supplier_id": supplier_id,
                    "supplier_name": suppliers_map.get(supplier_id, f"Поставщик #{supplier_id}"),
                    "items": [],
                }

            product_info = products_map.get(product_id, {"name": f"Товар #{product_id}", "code": "—"})
            orders[key]["items"].append({
                "product_id": product_id,
                "product_name": product_info["name"],
                "product_code": product_info["code"],
                "qty_in_order": qty,
                "avg_purchase_price": avg_price,
                "qty_in_all_orders": all_orders_map.get(product_id, 0),
                "qty_in_store": stock_map.get(product_id, 0),
            })

        return sorted(orders.values(), key=lambda o: o["order_date"], reverse=True)

    active_orders = build_order_items(active_rows)
    all_archive_orders = build_order_items(archive_rows)
    active_keys = set(o["order_key"] for o in active_orders)
    archived_orders = [o for o in all_archive_orders if o["order_key"] not in active_keys]

    return {"active": active_orders, "archived": archived_orders}


@router.get("/orders/{supplier_id}/items", status_code=200)
async def get_order_items(supplier_id: int, db: AsyncSession = Depends(get_db)):
    """📋 Получить все юниты поставщика (EXPECTED и уже принятые)"""
    result = (await db.execute(
        select(ProductUnit)
        .where(ProductUnit.supplier_id == supplier_id)
        .order_by(ProductUnit.created_at.desc())
    )).scalars().all()

    items = []
    for unit in result:
        product = await db.get(Product, unit.product_id)
        items.append({
            "unit_id": unit.id,
            "product_id": unit.product_id,
            "product_name": product.name.replace("_", " ") if product else f"Товар #{unit.product_id}",
            "product_code": product.code if product else "—",
            "unique_serial_number": unit.unique_serial_number,
            "purchase_price": float(unit.purchase_price) if unit.purchase_price else 0.0,
            "physical_status": unit.physical_status.value if unit.physical_status else "EXPECTED",
        })

    return {"supplier_id": supplier_id, "items": items, "total": len(items)}


@router.post("/orders", status_code=status.HTTP_201_CREATED)
async def create_supplier_order(payload: CreateSupplierOrder, db: AsyncSession = Depends(get_db)):
    """🛠️ Команда 0001: Создание заявки с автогенерацией unique_serial_number"""
    supplier = await db.get(Supplier, payload.supplier_id)
    if not supplier:
        raise HTTPException(status_code=404, detail=f"Поставщик с ID {payload.supplier_id} не найден")

    total_financial_load = 0.0
    response_items = []

    for item in payload.items:
        product = await db.get(Product, item.product_id)
        if not product:
            raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")

        subtotal = float(item.quantity) * float(item.estimated_purchase_price)
        total_financial_load += subtotal

        for _ in range(item.quantity):
            generated_sn = f"SN-ORD-{uuid.uuid4().hex[:8].upper()}"
            unit = ProductUnit(
                product_id=item.product_id,
                supplier_id=payload.supplier_id,
                unique_serial_number=generated_sn,
                purchase_price=item.estimated_purchase_price,
                logistics_status=LogisticsStatus.IN_REQUEST,
                physical_status=PhysicalStatus.EXPECTED,
                is_reserved=False
            )
            db.add(unit)

        response_items.append({
            "product_id": item.product_id,
            "product_name": product.name,
            "code": product.code,
            "quantity": item.quantity,
            "estimated_price": float(item.estimated_purchase_price),
            "subtotal": subtotal
        })

    await db.commit()
    return {
        "supplier_id": payload.supplier_id,
        "supplier_name": supplier.name,
        "total_financial_load": total_financial_load,
        "items": response_items
    }


@router.delete("/units/debug-clear", status_code=200)
async def debug_clear_units(product_id: int, db: AsyncSession = Depends(get_db)):
    await db.execute(delete(ProductUnit).where(ProductUnit.product_id == product_id))
    await db.commit()
    return {"status": "cleared"}


@router.delete("/orders/debug-clear", status_code=200)
async def debug_clear_orders(product_id: int, db: AsyncSession = Depends(get_db)):
    return {"status": "cleared"}