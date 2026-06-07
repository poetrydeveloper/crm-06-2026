# services/core/src/models/product.py
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Numeric, DateTime, ForeignKey, JSON
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Product(Base):
    """Карточка товара (Глобальный справочник номенклатуры каталога)"""
    __tablename__ = "products"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"), nullable=False)
    brand_id: Mapped[Optional[int]] = mapped_column(ForeignKey("brands.id"), nullable=True)
    
    code: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True) # Артикул
    name: Mapped[str] = mapped_column(String(255), nullable=False)                         # Наименование
    description: Mapped[Optional[str]] = mapped_column(String(1000), nullable=True)
    recommended_retail_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # --- БЛОК УМНОГО И ОБУЧАЕМОГО ПОИСКА ---
    # Сюда авто-скрипт пишет ["ключ", "10мм", "toptul", "инструмент"]
    search_tags: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    
    # Сюда заносятся сленговые синонимы руками или при обучении: ["ск 911", "девятка", "разрезной"]
    search_aliases: Mapped[Optional[list]] = mapped_column(JSON, default=list, nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Прямые связи к справочникам
    category: Mapped["Category"] = relationship("Category", back_populates="products")
    brand: Mapped[Optional["Brand"]] = relationship("Brand", back_populates="products")
    
    # Связи с периферией
    units: Mapped[List["ProductUnit"]] = relationship("ProductUnit", back_populates="product")
    pending_sales: Mapped[List["PendingSale"]] = relationship("PendingSale", back_populates="resolved_product")
