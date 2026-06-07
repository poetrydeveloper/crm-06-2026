# services/core/src/models/product_unit.py
import enum
from datetime import datetime
from typing import List, Optional
from decimal import Decimal
from sqlalchemy import String, Integer, Decimal as Numeric, Boolean, DateTime, ForeignKey, Enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base

class LogisticsStatus(str, enum.Enum):
    CANDIDATE = "CANDIDATE"       # Черновик в ежедневной заявке (Армтек)
    IN_REQUEST = "IN_REQUEST"     # Заявлено поставщику
    IN_DELIVERY = "IN_DELIVERY"   # Поставщик отправил, товар в пути
    RECEIVED = "RECEIVED"         # Успешно принято на склад (Форсаж)

class PhysicalStatus(str, enum.Enum):
    IN_STORE = "IN_STORE"                 # Физически на полке, доступно к продаже
    SOLD = "SOLD"                         # Продано через кассу
    LOST = "LOST"                         # Утеряно / Недостача по ревизии
    WRITE_OFF = "WRITE_OFF"               # Списано / Возврат брака поставщику
    IN_DISASSEMBLED = "IN_DISASSEMBLED"   # Набор, который был расформирован на сателлиты
    ABSORBED = "ABSORBED"                 # Головка, поглощенная обратно в собранный набор

class ProductUnit(Base):
    """Физическая единица товара на магазине (Поштучный учет FIFO и Наборы)"""
    __tablename__ = "product_units"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"), nullable=False)
    supplier_id: Mapped[Optional[int]] = mapped_column(ForeignKey("suppliers.id"), nullable=True)
    
    # Уникальный номер, генерируемый системой для сквозного следа (Timeline)
    unique_serial_number: Mapped[str] = mapped_column(String(100), unique=True, nullable=False, index=True)
    
    # Динамическая цена закупки (прогноз при заявке, фиксация при приемке)
    purchase_price: Mapped[Optional[Decimal]] = mapped_column(Numeric(10, 2), nullable=True)
    
    # Статусы движения и физического состояния
    logistics_status: Mapped[LogisticsStatus] = mapped_column(Enum(LogisticsStatus), default=LogisticsStatus.CANDIDATE, nullable=False)
    physical_status: Mapped[PhysicalStatus] = mapped_column(Enum(PhysicalStatus), default=PhysicalStatus.IN_STORE, nullable=False)
    
    # Флаг жесткого резерва под клиента (чтобы кассир случайно не продал чужой заказ с полки)
    is_reserved: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    
    # --- ИЕРАРХИЯ НАБОРОВ (СВЯЗЬ НА СЕБЯ) ---
    # Если строка — это головка из набора, здесь будет лежать ID строки самого Набора
    parent_unit_id: Mapped[Optional[int]] = mapped_column(ForeignKey("product_units.id"), nullable=True)
    
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # SQLAlchemy отношения (Связи между таблицами)
    product: Mapped["Product"] = relationship("Product", back_populates="units")
    supplier: Mapped[Optional["Supplier"]] = relationship("Supplier", back_populates="supplied_units")
    
    # Связи для сборки/разборки наборов
    parent_set: Mapped[Optional["ProductUnit"]] = relationship("ProductUnit", remote_side=[id], back_populates="satellites")
    satellites: Mapped[List["ProductUnit"]] = relationship("ProductUnit", back_populates="parent_set")
    
    # Связь со строками кассовых чеков
    cash_event_items: Mapped[List["CashEventItem"]] = relationship("CashEventItem", back_populates="product_unit")
