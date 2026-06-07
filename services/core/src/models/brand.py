# services/core/src/models/brand.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Brand(Base):
    """Справочник брендов (производителей инструментов и автотоваров)"""
    __tablename__ = "brands"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    description: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Обратная связь: один бренд может принадлежать множеству товаров в каталоге
    products: Mapped[List["Product"]] = relationship("Product", back_populates="brand")
