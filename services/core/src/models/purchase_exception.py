# services/core/src/models/purchase_exception.py
from sqlalchemy import Integer, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship
from .base import Base
from .product import Product

class PurchaseException(Base):
    """
    🚫 ФИЗИЧЕСКАЯ ТАБЛИЦА ЧЕРНОГО СПИСКА ИСКЛЮЧЕНИЙ 'БОЛЬШЕ НЕ НАХОДИТЬ'
    🛡️ СУБД-СТАНДАРТ: Хранит строгую ссылку на существующий ID номенклатуры.
    """
    __tablename__ = "purchase_exceptions"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    product_id: Mapped[int] = mapped_column(ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    product: Mapped["Product"] = relationship("Product")