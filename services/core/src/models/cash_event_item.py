# services/core/src/models/cash_event_item.py
from datetime import datetime
from decimal import Decimal
from sqlalchemy import Integer , Numeric, DateTime, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CashEventItem(Base):
    """Позиция (строка) внутри кассового чека продажи или возврата"""
    __tablename__ = "cash_event_items"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cash_event_id: Mapped[int] = mapped_column(ForeignKey("cash_events.id"), nullable=False)
    
    # Связь с конкретной поштучной единицей товара, ушедшей со склада
    product_unit_id: Mapped[int] = mapped_column(ForeignKey("product_units.id"), nullable=False)
    
    # Финальная цена за 1 единицу товара, которую заплатил клиент (с учетом всех скидок)
    price_per_unit: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # Зафиксированная скидка в рублях на эту позицию (для аналитики упущенной выгоды)
    discount_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # SQLAlchemy отношения (Связи)
    cash_event: Mapped["CashEvent"] = relationship("CashEvent", back_populates="items")
    product_unit: Mapped["ProductUnit"] = relationship("ProductUnit", back_populates="cash_event_items")
