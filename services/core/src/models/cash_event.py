# services/core/src/models/cash_event.py
import enum
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer , Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CashEventType(str, enum.Enum):
    SALE = "SALE"       # Прямая кассовая продажа товара
    RETURN = "RETURN"   # Полный или частичный возврат товара клиентом
    INCOME = "INCOME"   # Внесение денег (например, предоплата за будущую заявку)
    EXPENSE = "EXPENSE" # Изъятие денег из кассы (расход на точку)

class CashEvent(Base):
    """Кассовое событие (Чек продажи, акт возврата или финансовый ордер)"""
    __tablename__ = "cash_events"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cash_day_id: Mapped[int] = mapped_column(ForeignKey("cash_days.id"), nullable=False)
    
    # Ссылка на клиента (если null — это анонимный "Гость", долг для него заблокирован)
    customer_id: Mapped[Optional[int]] = mapped_column(ForeignKey("customers.id"), nullable=True)
    
    type: Mapped[CashEventType] = mapped_column(Enum(CashEventType), default=CashEventType.SALE, nullable=False)
    
    # Общая финальная сумма по данному чеку/ордеру
    total_amount: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    
    # --- БЛОК КОМБИНИРОВАННОЙ ОПЛАТЫ И ДОЛГОВ ---
    amount_cash: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    amount_card: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    amount_credit: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False) # Уходит в минус баланса клиента
    
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True) # Примечание/ошибка кассира
    created_by: Mapped[str] = mapped_column(String(100), default="admin", nullable=False) # Кто оформил
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    # SQLAlchemy отношения (Связи)
    cash_day: Mapped["CashDay"] = relationship("CashDay", back_populates="events")
    customer: Mapped[Optional["Customer"]] = relationship("Customer", back_populates="cash_events")
    items: Mapped[List["CashEventItem"]] = relationship("CashEventItem", back_populates="cash_event")
