# services/core/src/models/purchase_exception.py
from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship
from src.models.base import Base

class PurchaseException(Base):
    """
    🚫 ФИЗИЧЕСКАЯ ТАБЛИЦА ЧЕРНОГО СПИСКА ИСКЛЮЧЕНИЙ 'БОЛЬШЕ НЕ НАХОДИТЬ'
    🛡️ СУБД-СТАНДАРТ: Хранит строгую ссылку на существующий ID номенклатуры.
    """
    __tablename__ = "purchase_exceptions"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    product_id = Column(Integer, ForeignKey("products.id", ondelete="CASCADE"), unique=True, nullable=False)
    
    product = relationship("Product")
