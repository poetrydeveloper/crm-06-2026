# services/core/src/components/order_manager.py
import uuid
from decimal import Decimal
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from src.models import Product, Supplier, ProductUnit, LogisticsStatus, PhysicalStatus
from src.schemas.warehouse import CreateSupplierOrder, SupplierOrderResponse, OrderResponseItem

class OrderManager:
    @staticmethod
    async def create_order(payload: CreateSupplierOrder, db: AsyncSession) -> SupplierOrderResponse:
        supplier = await db.get(Supplier, payload.supplier_id)
        if not supplier:
            raise HTTPException(status_code=404, detail=f"Поставщик с ID {payload.supplier_id} не найден")

        total_financial_load = Decimal("0.00")
        response_items = []

        for item in payload.items:
            product = await db.get(Product, item.product_id)
            if not product:
                raise HTTPException(status_code=404, detail=f"Товар с ID {item.product_id} не найден")

            subtotal = item.estimated_purchase_price * item.quantity
            total_financial_load += subtotal

            # Поштучное FIFO-зарождение единиц товара
            for _ in range(item.quantity):
                unique_sn = f"SUP-{payload.supplier_id}-{uuid.uuid4().hex[:8].upper()}"
                new_unit = ProductUnit(
                    product_id=item.product_id,
                    supplier_id=payload.supplier_id,
                    unique_serial_number=unique_sn,
                    purchase_price=item.estimated_purchase_price,
                    logistics_status=LogisticsStatus.IN_REQUEST,
                    physical_status=PhysicalStatus.EXPECTED, 
                    is_reserved=False
                )
                db.add(new_unit)

            response_items.append(
                OrderResponseItem(
                    product_id=product.id, product_name=product.name, code=product.code,
                    quantity=item.quantity, estimated_price=item.estimated_purchase_price, subtotal=subtotal
                )
            )

        await db.commit()
        return SupplierOrderResponse(
            supplier_id=supplier.id, supplier_name=supplier.name,
            total_financial_load=total_financial_load, items=response_items
        )
