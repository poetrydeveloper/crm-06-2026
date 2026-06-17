# services/core/src/schemas/warehouse.py
from pydantic import BaseModel, Field
from typing import List, Optional
from decimal import Decimal

# --- ТВОИ ОРИГИНАЛЬНЫЕ СХЕМЫ СТРОГОГО ФИНАНСОВОГО УЧЕТА ---
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
    code: str
    quantity: int
    estimated_price: Decimal
    subtotal: Decimal

class SupplierOrderResponse(BaseModel):
    supplier_id: int
    supplier_name: str
    total_financial_load: Decimal
    items: List[OrderResponseItem]

# --- ПОДКЛЮЧЕННЫЕ КОНТРАКТЫ СКЛАДСКИХ ОПЕРАЦИЙ ---
class ReceiptItem(BaseModel):
    product_id: int
    quantity: int
    actual_purchase_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2)

class SupplierInvoiceReceipt(BaseModel):
    supplier_id: int
    items: List[ReceiptItem]

class DisassemblyTemplatedPayload(BaseModel):
    unique_serial_number: str

class DisassemblyPartialPayload(BaseModel):
    unique_serial_number: str
    child_product_id: int

class SetAbsorptionPayload(BaseModel):
    parent_product_id: int
    satellite_unit_ids: List[int]

class RuleCreatePayload(BaseModel):
    rule_name: str
    tags: List[str]
