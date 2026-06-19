"""make email required in business customer models

Revision ID: b2e7ed612f1d
Revises: 8f3c6e1b2d42
Create Date: 2026-06-01 13:12:35.439435

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'b2e7ed612f1d'
down_revision: Union[str, Sequence[str], None] = '8f3c6e1b2d42'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Make email required in business_customers table."""
    # First, set any NULL emails to a placeholder (optional but safe)
    op.execute("UPDATE business_customers SET email = 'noemail@example.com' WHERE email IS NULL")
    
    # Alter the email column to be NOT NULL
    op.alter_column('business_customers', 'email',
               existing_type=sa.String(),
               nullable=False)


def downgrade() -> None:
    """Downgrade schema - Revert email column to nullable."""
    op.alter_column('business_customers', 'email',
               existing_type=sa.String(),
               nullable=True)
