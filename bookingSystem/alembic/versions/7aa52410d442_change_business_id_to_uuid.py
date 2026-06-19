"""change business id to uuid safely

Revision ID: 7aa52410d442
Revises: bc0ffbee5c02
Create Date: 2026-04-27
"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers
revision = '7aa52410d442'
down_revision = 'bc0ffbee5c02'
branch_labels = None
depends_on = None


def upgrade():
    # Enable UUID extension
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp";')

    # 1. Add new UUID column in businesses
    op.add_column(
        'businesses',
        sa.Column('id_uuid', postgresql.UUID(as_uuid=True), nullable=True)
    )

    # 2. Populate UUIDs
    op.execute("UPDATE businesses SET id_uuid = uuid_generate_v4();")

    # 3. Add new UUID columns to dependent tables
    op.add_column('services', sa.Column('business_id_uuid', postgresql.UUID(as_uuid=True)))
    op.add_column('appointments', sa.Column('business_id_uuid', postgresql.UUID(as_uuid=True)))
    op.add_column('business_hours', sa.Column('business_id_uuid', postgresql.UUID(as_uuid=True)))

    # 4. Copy data using JOIN
    op.execute("""
        UPDATE services s
        SET business_id_uuid = b.id_uuid
        FROM businesses b
        WHERE s.business_id = b.id;
    """)

    op.execute("""
        UPDATE appointments a
        SET business_id_uuid = b.id_uuid
        FROM businesses b
        WHERE a.business_id = b.id;
    """)

    op.execute("""
        UPDATE business_hours bh
        SET business_id_uuid = b.id_uuid
        FROM businesses b
        WHERE bh.business_id = b.id;
    """)

    # 5. Drop old foreign keys
    op.drop_constraint('services_business_id_fkey', 'services', type_='foreignkey')
    op.drop_constraint('appointments_business_id_fkey', 'appointments', type_='foreignkey')
    op.drop_constraint('business_hours_business_id_fkey', 'business_hours', type_='foreignkey')

    # 6. Drop old columns
    op.drop_column('services', 'business_id')
    op.drop_column('appointments', 'business_id')
    op.drop_column('business_hours', 'business_id')
    op.drop_column('businesses', 'id')

    # 7. Rename new columns
    op.alter_column('businesses', 'id_uuid', new_column_name='id')
    op.alter_column('services', 'business_id_uuid', new_column_name='business_id')
    op.alter_column('appointments', 'business_id_uuid', new_column_name='business_id')
    op.alter_column('business_hours', 'business_id_uuid', new_column_name='business_id')

    # 8. Set primary key
    op.create_primary_key('businesses_pkey', 'businesses', ['id'])

    # 9. Recreate foreign keys
    op.create_foreign_key(
        'services_business_id_fkey',
        'services', 'businesses',
        ['business_id'], ['id']
    )

    op.create_foreign_key(
        'appointments_business_id_fkey',
        'appointments', 'businesses',
        ['business_id'], ['id']
    )

    op.create_foreign_key(
        'business_hours_business_id_fkey',
        'business_hours', 'businesses',
        ['business_id'], ['id']
    )


def downgrade():
    raise Exception("Downgrade not supported for UUID migration")