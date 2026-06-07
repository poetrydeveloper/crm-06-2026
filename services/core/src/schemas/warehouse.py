# services/core/src/schemas/warehouse.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

class OrderItem(BaseModel):
    product_id: int = Field(..., description="ID карточки товара из каталога")
    quantity: int = Field(..., ge=1, description="Количество заказываемых штук")
    estimated_purchase_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Ожидаемая цена закупки")

class CreateSupplierOrder(BaseModel):
    supplier_id: int = Field(..., description="ID поставщика (Армтек, Форсаж и др.)")
    items: List[OrderItem] = Field(..., description="Список позиций в заявке")

class OrderResponseItem(BaseModel):
    product_id: int
    product_name: str
    code: str  # Артикул
    quantity: int
    estimated_price: Decimal
    subtotal: Decimal

class SupplierOrderResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    total_financial_load: Decimal  # Общая финансовая нагрузка заявки
    items: List[OrderResponseItem]
