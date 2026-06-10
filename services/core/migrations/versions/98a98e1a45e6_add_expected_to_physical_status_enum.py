"""add_expected_to_physical_status_enum

Revision ID: 98a98e1a45e6
Revises: c3b9afaa80f6
Create Date: 2026-06-10 11:19:38.101343

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '98a98e1a45e6'
down_revision: Union[str, Sequence[str], None] = 'c3b9afaa80f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Принудительно добавляем значение 'EXPECTED' в перечисление physicalstatus на уровне PostgreSQL 16
    op.execute("ALTER TYPE physicalstatus ADD VALUE 'EXPECTED'")

def downgrade() -> None:
    """Downgrade schema."""
    # В PostgreSQL удаление элементов из ENUM не поддерживается напрямую через ALTER TYPE,
    # поэтому при откате миграции мы просто пропускаем шаг, что абсолютно безопасно.
    pass
