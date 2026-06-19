"""convert ids to uuid

Revision ID: 4d2e55a10054
Revises: 018d1dd42b59
Create Date: 2026-05-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers
revision: str = '4d2e55a10054'
down_revision: Union[str, Sequence[str], None] = '018d1dd42b59'
branch_labels = None
depends_on = None


def upgrade() -> None:
    # 1. Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # ========================================================
    # PHASE 1: BUSINESSES (Changing PK from String to UUID)
    # ========================================================
    # Drop FKs that point to businesses
    op.drop_constraint('services_business_id_fkey', 'services', type_='foreignkey')
    op.drop_constraint('appointments_business_id_fkey', 'appointments', type_='foreignkey')
    op.drop_constraint('business_hours_business_id_fkey', 'business_hours', type_='foreignkey')
    op.drop_constraint('business_customers_business_id_fkey', 'business_customers', type_='foreignkey')

    # Convert PK and FKs to UUID
    for table, col in [('businesses', 'id'), ('services', 'business_id'), 
                       ('appointments', 'business_id'), ('business_hours', 'business_id'), 
                       ('business_customers', 'business_id')]:
        op.execute(f'ALTER TABLE {table} ALTER COLUMN {col} TYPE UUID USING {col}::uuid')

    # Recreate FKs for Businesses
    op.create_foreign_key('services_business_id_fkey', 'services', 'businesses', ['business_id'], ['id'])
    op.create_foreign_key('appointments_business_id_fkey', 'appointments', 'businesses', ['business_id'], ['id'])
    op.create_foreign_key('business_hours_business_id_fkey', 'business_hours', 'businesses', ['business_id'], ['id'])
    op.create_foreign_key('business_customers_business_id_fkey', 'business_customers', 'businesses', ['business_id'], ['id'])


    # ========================================================
    # PHASE 2: APPOINTMENTS & PAYMENTS (The tricky part)
    # ========================================================
    # 1. Drop the FK from payments to appointments
    op.drop_constraint('payments_appointment_id_fkey', 'payments', type_='foreignkey')

    # 2. Prepare new UUID columns
    op.add_column('appointments', sa.Column('new_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()')))
    op.add_column('payments', sa.Column('new_appointment_id', postgresql.UUID(as_uuid=True)))

    # 3. CRITICAL: Map the new UUIDs from appointments to payments
    # This prevents the "Key not present in table appointments" error
    op.execute("""
        UPDATE payments 
        SET new_appointment_id = appointments.new_id 
        FROM appointments 
        WHERE payments.appointment_id = appointments.id
    """)

    # 4. Finalize Appointments PK
    op.drop_column('appointments', 'id')
    op.alter_column('appointments', 'new_id', new_column_name='id', nullable=False)
    op.execute("ALTER TABLE appointments ADD PRIMARY KEY (id)")

    # 5. Finalize Payments FK
    op.drop_column('payments', 'appointment_id')
    op.alter_column('payments', 'new_appointment_id', new_column_name='appointment_id', nullable=False)

    # 6. Recreate the Foreign Key constraint
    op.create_foreign_key(
        'payments_appointment_id_fkey',
        'payments',
        'appointments',
        ['appointment_id'],
        ['id']
    )

    # ========================================================
    # PHASE 3: PAYMENTS PK (Changing PK from Int to UUID)
    # ========================================================
    op.add_column('payments', sa.Column('new_id', postgresql.UUID(as_uuid=True), server_default=sa.text('uuid_generate_v4()')))
    op.drop_column('payments', 'id')
    op.alter_column('payments', 'new_id', new_column_name='id', nullable=False)
    op.execute("ALTER TABLE payments ADD PRIMARY KEY (id)")
def downgrade() -> None:
    pass