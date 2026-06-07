# services/core/src/models/supplier.py
from datetime import datetime
from typing import List, Optional
from sqlalchemy import String, Integer, DateTime
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class Supplier(Base):
    """Справочник оптовых поставщиков (Армтек, Форсаж, Гамматест и др.)"""
    __tablename__ = "suppliers"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    name: Mapped[str] = mapped_column(String(150), unique=True, nullable=False, index=True) # Имя поставщика
    contact_info: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)        # Телефон / Заметки
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Связь: один поставщик может фигурировать во множестве штучных партий товаров
    supplied_units: Mapped[List["ProductUnit"]] = relationship("ProductUnit", back_populates="supplier")
