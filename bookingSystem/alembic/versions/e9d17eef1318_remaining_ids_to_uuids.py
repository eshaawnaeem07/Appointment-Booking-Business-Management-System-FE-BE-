"""remaining ids to UUIDs

Revision ID: e9d17eef1318
Revises: 4d2e55a10054
Create Date: 2026-05-15 12:47:33.533229

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "e9d17eef1318"
down_revision: Union[str, Sequence[str], None] = "4d2e55a10054"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


appointment_status_enum = postgresql.ENUM(
    "PENDING",
    "CONFIRMED",
    "COMPLETED",
    "CANCELLED",
    name="appointmentstatus",
)

payment_status_enum = postgresql.ENUM(
    "PENDING",
    "PAID",
    "FAILED",
    "REFUNDED",
    name="paymentstatus",
)


def upgrade():

    # =====================================================
    # 0. Enable UUID extension
    # =====================================================
    op.execute('CREATE EXTENSION IF NOT EXISTS "pgcrypto"')

    # =====================================================
    # 1. DROP FK DEPENDENCIES FIRST (CRITICAL FIX #2)
    # =====================================================
    # Use CASCADE approach to handle all dependencies at once
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS fk_appointments_walk_in_customer CASCADE
        """)
    
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS appointments_walk_in_customer_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS appointments_user_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS appointments_business_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS appointments_service_id_fkey CASCADE
        """)

    op.execute("""
        ALTER TABLE businesses
        DROP CONSTRAINT IF EXISTS businesses_owner_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE business_customers
        DROP CONSTRAINT IF EXISTS business_customers_user_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE business_customers
        DROP CONSTRAINT IF EXISTS business_customers_business_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE services
        DROP CONSTRAINT IF EXISTS services_business_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE business_hours
        DROP CONSTRAINT IF EXISTS business_hours_business_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE payments
        DROP CONSTRAINT IF EXISTS payments_appointment_id_fkey CASCADE
        """)

    # =====================================================
    # 2. USERS
    # =====================================================
    op.add_column("users", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE users SET uuid = gen_random_uuid()")

    # =====================================================
    # 3. BUSINESSES
    # =====================================================
    op.add_column("businesses", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE businesses SET uuid = gen_random_uuid()")

    op.add_column("businesses", sa.Column("owner_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE businesses b
        SET owner_id_uuid = u.uuid
        FROM users u
        WHERE b.owner_id = u.id
    """)

    # =====================================================
    # 4. SERVICES
    # =====================================================
    op.add_column("services", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE services SET uuid = gen_random_uuid()")

    op.add_column("services", sa.Column("business_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE services s
        SET business_id_uuid = b.uuid
        FROM businesses b
        WHERE s.business_id = b.id
    """)

    # =====================================================
    # 5. BUSINESS HOURS
    # =====================================================
    op.add_column("business_hours", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE business_hours SET uuid = gen_random_uuid()")

    op.add_column("business_hours", sa.Column("business_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE business_hours bh
        SET business_id_uuid = b.uuid
        FROM businesses b
        WHERE bh.business_id = b.id
    """)

    # =====================================================
    # 6. BUSINESS CUSTOMERS
    # =====================================================
    op.add_column("business_customers", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE business_customers SET uuid = gen_random_uuid()")

    op.add_column("business_customers", sa.Column("business_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE business_customers bc
        SET business_id_uuid = b.uuid
        FROM businesses b
        WHERE bc.business_id = b.id
    """)

    op.add_column("business_customers", sa.Column("user_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE business_customers bc
        SET user_id_uuid = u.uuid
        FROM users u
        WHERE bc.user_id = u.id
    """)

    # =====================================================
    # 7. APPOINTMENTS (FIXED: NEVER assign UUID to integer column)
    # =====================================================
    op.add_column("appointments", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE appointments SET uuid = gen_random_uuid()")

    op.add_column("appointments", sa.Column("user_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE appointments a
        SET user_id_uuid = u.uuid
        FROM users u
        WHERE a.user_id = u.id
    """)

    op.add_column("appointments", sa.Column("business_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE appointments a
        SET business_id_uuid = b.uuid
        FROM businesses b
        WHERE a.business_id = b.id
    """)

    op.add_column("appointments", sa.Column("service_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE appointments a
        SET service_id_uuid = s.uuid
        FROM services s
        WHERE a.service_id = s.id
    """)

    op.add_column("appointments", sa.Column("walk_in_customer_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE appointments a
        SET walk_in_customer_id_uuid = bc.uuid
        FROM business_customers bc
        WHERE a.walk_in_customer_id = bc.id
    """)

    # =====================================================
    # 8. PAYMENTS
    # =====================================================
    op.add_column("payments", sa.Column("uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("UPDATE payments SET uuid = gen_random_uuid()")

    op.add_column("payments", sa.Column("appointment_id_uuid", postgresql.UUID(as_uuid=True), nullable=True))
    op.execute("""
        UPDATE payments p
        SET appointment_id_uuid = a.uuid
        FROM appointments a
        WHERE p.appointment_id = a.id
    """)

    # =====================================================
    # 9. DROP OLD PRIMARY KEYS SAFELY
    # =====================================================
    op.drop_constraint("users_pkey", "users", type_="primary")
    op.drop_constraint("businesses_pkey", "businesses", type_="primary")
    op.drop_constraint("services_pkey", "services", type_="primary")
    op.drop_constraint("business_hours_pkey", "business_hours", type_="primary")
    op.drop_constraint("business_customers_pkey", "business_customers", type_="primary")
    op.drop_constraint("appointments_pkey", "appointments", type_="primary")
    op.drop_constraint("payments_pkey", "payments", type_="primary")

    # =====================================================
    # 10. REPLACE IDs WITH UUIDS
    # =====================================================
    op.drop_column("users", "id")
    op.alter_column("users", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("users_pkey", "users", ["id"])

    op.drop_column("businesses", "id")
    op.alter_column("businesses", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("businesses_pkey", "businesses", ["id"])

    op.drop_column("services", "id")
    op.alter_column("services", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("services_pkey", "services", ["id"])

    op.drop_column("business_hours", "id")
    op.alter_column("business_hours", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("business_hours_pkey", "business_hours", ["id"])

    op.drop_column("business_customers", "id")
    op.alter_column("business_customers", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("business_customers_pkey", "business_customers", ["id"])

    op.drop_column("appointments", "id")
    op.alter_column("appointments", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("appointments_pkey", "appointments", ["id"])

    op.drop_column("payments", "id")
    op.alter_column("payments", "uuid", new_column_name="id", nullable=False)
    op.create_primary_key("payments_pkey", "payments", ["id"])

    # =====================================================
    # 11. DROP OLD FOREIGN KEY COLUMNS AND RENAME UUID COLUMNS
    # =====================================================
    # Drop old integer FK columns from businesses
    op.drop_column("businesses", "owner_id")
    op.alter_column("businesses", "owner_id_uuid", new_column_name="owner_id", nullable=False)
    
    # Drop old integer FK columns from services
    op.drop_column("services", "business_id")
    op.alter_column("services", "business_id_uuid", new_column_name="business_id", nullable=False)
    
    # Drop old integer FK columns from business_hours
    op.drop_column("business_hours", "business_id")
    op.alter_column("business_hours", "business_id_uuid", new_column_name="business_id", nullable=False)
    
    # Drop old integer FK columns from business_customers
    op.drop_column("business_customers", "business_id")
    op.alter_column("business_customers", "business_id_uuid", new_column_name="business_id", nullable=False)
    
    op.drop_column("business_customers", "user_id")
    op.alter_column("business_customers", "user_id_uuid", new_column_name="user_id", nullable=True)
    
    # Drop old integer FK columns from appointments
    op.drop_column("appointments", "user_id")
    op.alter_column("appointments", "user_id_uuid", new_column_name="user_id", nullable=True)
    
    op.drop_column("appointments", "business_id")
    op.alter_column("appointments", "business_id_uuid", new_column_name="business_id", nullable=False)
    
    op.drop_column("appointments", "service_id")
    op.alter_column("appointments", "service_id_uuid", new_column_name="service_id", nullable=False)
    
    op.drop_column("appointments", "walk_in_customer_id")
    op.alter_column("appointments", "walk_in_customer_id_uuid", new_column_name="walk_in_customer_id", nullable=True)
    
    # Drop old integer FK columns from payments
    op.drop_column("payments", "appointment_id")
    op.alter_column("payments", "appointment_id_uuid", new_column_name="appointment_id", nullable=False)

    # =====================================================
    # 12. RECREATE FOREIGN KEYS (CLEAN UUID STATE)
    # =====================================================
    op.create_foreign_key("businesses_owner_id_fkey", "businesses", "users", ["owner_id"], ["id"])
    op.create_foreign_key("services_business_id_fkey", "services", "businesses", ["business_id"], ["id"])
    op.create_foreign_key("business_hours_business_id_fkey", "business_hours", "businesses", ["business_id"], ["id"])
    op.create_foreign_key("business_customers_business_id_fkey", "business_customers", "businesses", ["business_id"], ["id"])
    op.create_foreign_key("business_customers_user_id_fkey", "business_customers", "users", ["user_id"], ["id"])

    op.create_foreign_key("appointments_user_id_fkey", "appointments", "users", ["user_id"], ["id"])
    op.create_foreign_key("appointments_business_id_fkey", "appointments", "businesses", ["business_id"], ["id"])
    op.create_foreign_key("appointments_service_id_fkey", "appointments", "services", ["service_id"], ["id"])
    op.create_foreign_key("appointments_walk_in_customer_id_fkey", "appointments", "business_customers", ["walk_in_customer_id"], ["id"])

    op.create_foreign_key("payments_appointment_id_fkey", "payments", "appointments", ["appointment_id"], ["id"])


def downgrade():
    raise NotImplementedError("UUID migration downgrade not supported safely")