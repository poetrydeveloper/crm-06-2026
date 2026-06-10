# services/core/src/schemas/cash.py
from pydantic import BaseModel, Field
from typing import Optional
from decimal import Decimal
from datetime import datetime

class CashDayOpen(BaseModel):
    date: datetime = Field(default_factory=datetime.utcnow, description="Дата и время открытия смены")

class CashSaleCreate(BaseModel):
    product_id: int = Field(..., description="ID продаваемого товара")
    customer_id: Optional[int] = Field(None, description="ID постоянного клиента (Optional)")
    sale_price: Decimal = Field(..., ge=0, max_digits=10, decimal_places=2, description="Цена продажи")
    amount_cash: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2, description="Наличные")
    amount_card: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2, description="Карта")
    amount_credit: Decimal = Field(default=Decimal("0.00"), ge=0, max_digits=10, decimal_places=2, description="В долг")
