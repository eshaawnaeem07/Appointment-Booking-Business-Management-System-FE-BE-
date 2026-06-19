"""add business customers table

Revision ID: 018d1dd42b59
Revises: f782c7906032
Create Date: 2026-05-05
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

revision: str = '018d1dd42b59'
down_revision: Union[str, Sequence[str], None] = 'f782c7906032'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'business_customers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column(
            'business_id',
            postgresql.UUID(as_uuid=True), 
            sa.ForeignKey('businesses.id'),
            nullable=False
        ),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id'), nullable=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('phone', sa.String(length=15), nullable=False),
        sa.Column('email', sa.String(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
    )

    op.add_column(
        'appointments',
        sa.Column('walk_in_customer_id', sa.Integer(), nullable=True)
    )

    op.create_foreign_key(
        'fk_appointments_walk_in_customer',
        'appointments',
        'business_customers',
        ['walk_in_customer_id'],
        ['id']
    )


def downgrade() -> None:
    op.drop_constraint('fk_appointments_walk_in_customer', 'appointments', type_='foreignkey')
    op.drop_column('appointments', 'walk_in_customer_id')
    op.drop_table('business_customers')