# services/core/src/models/purchase_rule.py
from sqlalchemy import Column, Integer, String, Numeric, DateTime, func
from src.models.base import Base

class PurchaseRule(Base):
    """🧠 Модель динамических правил автозаказа для компонента RuleEngine"""
    __tablename__ = "purchase_rules"

    id = Column(Integer, primary_key=True, index=True)
    price_operator = Column(String(50), nullable=True, default="ge")
    price_value = Column(Numeric(10, 2), nullable=True, default=0.00)
    name_contains = Column(String(255), nullable=True)
    stock_threshold = Column(Integer, nullable=True, default=2)
    
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())
