"""add refresh token fields

Revision ID: f782c7906032
Revises: 7aa52410d442
Create Date: 2026-04-28 17:10:32.341405
"""

from alembic import op
import sqlalchemy as sa


revision = 'f782c7906032'
down_revision = '7aa52410d442'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        'users',
        sa.Column('refresh_token', sa.String(), nullable=True)
    )

    op.add_column(
        'users',
        sa.Column('refresh_token_expiry', sa.DateTime(), nullable=True)
    )


def downgrade():
    op.drop_column('users', 'refresh_token')
    op.drop_column('users', 'refresh_token_expiry')