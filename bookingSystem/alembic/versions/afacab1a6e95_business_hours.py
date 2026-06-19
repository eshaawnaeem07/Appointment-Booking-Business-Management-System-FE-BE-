from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers
revision: str = 'afacab1a6e95'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:

    # USERS
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('password', sa.String(), nullable=False),
        sa.Column('role', sa.String()),
        sa.Column('reset_token', sa.String()),
        sa.Column('token_expiry', sa.DateTime()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)


    # BUSINESSES
    op.create_table(
        'businesses',
        sa.Column('id', sa.String(), primary_key=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('is_deleted', sa.Boolean(), default=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),

        sa.ForeignKeyConstraint(['owner_id'], ['users.id']),
    )


    # SERVICES
    op.create_table(
        'services',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.String()),
        sa.Column('duration', sa.Integer(), nullable=False),
        sa.Column('price', sa.Float(), nullable=False),
        sa.Column('requires_deposit', sa.Boolean(), default=False),
        sa.Column('is_active', sa.Boolean(), default=True),

        sa.ForeignKeyConstraint(['business_id'], ['businesses.id']),
    )


    # APPOINTMENTS
    op.create_table(
        'appointments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), nullable=True),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('service_id', sa.Integer(), nullable=False),
        sa.Column('start_time', sa.DateTime()),
        sa.Column('end_time', sa.DateTime()),
        sa.Column('status', sa.String()),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),

        sa.ForeignKeyConstraint(['user_id'], ['users.id']),
        sa.ForeignKeyConstraint(['business_id'], ['businesses.id']),
        sa.ForeignKeyConstraint(['service_id'], ['services.id']),
    )


    # PAYMENTS
    op.create_table(
        'payments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('appointment_id', sa.Integer(), nullable=False),
        sa.Column('stripe_session_id', sa.String()),
        sa.Column('stripe_payment_intent', sa.String()),
        sa.Column('status', sa.String()),  # safer than enum for first migration
        sa.Column('amount', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime()),
        sa.Column('updated_at', sa.DateTime()),

        sa.ForeignKeyConstraint(['appointment_id'], ['appointments.id']),
    )


    # BUSINESS HOURS
    op.create_table(
        'business_hours',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('business_id', sa.String(), nullable=False),
        sa.Column('day_of_week', sa.Integer(), nullable=False),
        sa.Column('open_time', sa.Time(), nullable=False),
        sa.Column('close_time', sa.Time(), nullable=False),
        sa.Column('is_open', sa.Boolean(), default=False),

        sa.ForeignKeyConstraint(['business_id'], ['businesses.id']),
    )


def downgrade() -> None:

    op.drop_table('business_hours')
    op.drop_table('payments')
    op.drop_table('appointments')
    op.drop_table('services')
    op.drop_table('businesses')
    op.drop_index('ix_users_email', table_name='users')
    op.drop_table('users')