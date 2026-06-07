# services/core/src/models/customer.py
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer , Numeric, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Customer(Base):
    """Модель клиента (контрагента) с единым виртуальным балансом для учета долгов и предоплат"""
    __tablename__ = "customers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), nullable=False, index=True) # ФИО, Имя или Название компании
    phone: Mapped[Optional[str]] = mapped_column(String(20), unique=True, nullable=True, index=True)
    email: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # Главное финансовое поле (+ это аванс/предоплата, - это долг клиента)
    balance: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Обратная связь: один клиент может совершить много кассовых событий (покупок, возвратов, предоплат)
    cash_events: Mapped[List["CashEvent"]] = relationship("CashEvent", back_populates="customer")
