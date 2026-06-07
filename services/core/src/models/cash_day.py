# services/core/src/models/cash_day.py
from datetime import datetime
from typing import List
from decimal import Decimal
from sqlalchemy import Integer, Decimal as Numeric, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class CashDay(Base):
    """Операционный кассовый день (Смена)"""
    __tablename__ = "cash_days"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    
    # Дата операционного дня (уникальна, один день — одна смена)
    date: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, unique=True, index=True)
    
    # Флаг состояния смены (false = открыта, идет торговля; true = закрыта, сдан бэкап)
    is_closed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # Финансовый итог дня по выручке (заполняется автоматически при закрытии смены)
    total_revenue: Mapped[Decimal] = mapped_column(Numeric(10, 2), default=Decimal("0.00"), nullable=False)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Прямая связь: один кассовый день содержит множество чеков и оплат
    events: Mapped[List["CashEvent"]] = relationship("CashEvent", back_populates="cash_day")
    
    # Связь с отложенными продажами "на коленке" за этот день
    pending_sales: Mapped[List["PendingSale"]] = relationship("PendingSale", back_populates="cash_day")
