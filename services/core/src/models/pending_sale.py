# services/core/src/models/pending_sale.py
import enum
from datetime import datetime
from typing import Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Decimal as Numeric, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class PendingStatus(str, enum.Enum):
    PENDING = "PENDING"     # Ожидает разбора админом (висит в неопознанных)
    RESOLVED = "RESOLVED"   # Успешно исправлен и привязан к реальному товару
    CANCELLED = "CANCELLED" # Ошибочная запись, аннулирована вручную

class PendingSale(Base):
    """Отложенные кассовые продажи для товаров, отсутствующих в справочнике"""
    __tablename__ = "pending_sales"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    cash_day_id: Mapped[int] = mapped_column(ForeignKey("cash_days.id"), nullable=False)
    
    # Временные текстовые данные, которые кассир вбил руками в спешке
    temp_name: Mapped[str] = mapped_column(String(255), nullable=False)
    temp_price: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    temp_quantity: Mapped[int] = mapped_column(Integer, default=1, nullable=False)
    
    # Опциональные текстовые подсказки для админа, чтобы он понял, что это было
    temp_category_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    temp_brand_name: Mapped[Optional[str]] = mapped_column(String(100), nullable=True)
    
    # --- КЛЮЧЕВОЙ БЛОК ИСПРАВЛЕНИЯ И СВЯЗЫВАНИЯ ---
    status: Mapped[PendingStatus] = mapped_column(Enum(PendingStatus), default=PendingStatus.PENDING, nullable=False)
    
    # Сюда запишется ID реального товара, когда админ проведёт разбор
    resolved_product_id: Mapped[Optional[int]] = mapped_column(ForeignKey("products.id"), nullable=True)
    resolved_at: Mapped[Optional[datetime]] = mapped_column(DateTime, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # SQLAlchemy отношения
    cash_day: Mapped["CashDay"] = relationship("CashDay", back_populates="pending_sales")
    resolved_product: Mapped[Optional["Product"]] = relationship("Product", back_populates="pending_sales")
