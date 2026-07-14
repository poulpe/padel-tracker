"""simplified logs id

Revision ID: f9eef5663708
Revises: 535aaf00283a
Create Date: 2025-02-01 00:14:13.765004

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

# revision identifiers, used by Alembic.
revision: str = "f9eef5663708"
down_revision: Union[str, None] = "535aaf00283a"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
