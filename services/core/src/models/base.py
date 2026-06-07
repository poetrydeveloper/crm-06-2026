# services/core/src/models/base.py
from sqlalchemy.orm import DeclarativeBase

class Base(DeclarativeBase):
    """Единый декларативный класс для всех таблиц PostgreSQL 16"""
    pass
