# services/core/src/models/purchase_rule.py
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class PurchaseRule(Base):
    """🧠 Модель динамических правил автозаказа для компонента RuleEngine"""
    __tablename__ = "purchase_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    price_operator: Mapped[Optional[str]] = mapped_column(String(50), nullable=True, default="ge")
    price_value: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True, default=0.00)
    name_contains: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    stock_threshold: Mapped[Optional[int]] = mapped_column(Integer, nullable=True, default=2)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now(), onupdate=func.now())