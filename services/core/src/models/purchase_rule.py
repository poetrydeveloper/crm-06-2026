# services/core/src/models/purchase_rule.py
from sqlalchemy import Column, Integer, String, Float
from src.models.base import Base

class PurchaseRule(Base):
    """Физическая таблица конструктора тегов-условий автозаказа"""
    __tablename__ = "purchase_rules"

    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    price_operator = Column(String(5), nullable=False)  # '>', '<'
    price_value = Column(Float, nullable=False)
    name_contains = Column(String(255), nullable=True)  # Подстрока (тег)
    stock_threshold = Column(Integer, nullable=False)   # Порог дефицита
