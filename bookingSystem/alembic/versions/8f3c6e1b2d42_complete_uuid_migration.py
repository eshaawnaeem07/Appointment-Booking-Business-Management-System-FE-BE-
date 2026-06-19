"""Complete UUID migration - fix incomplete columns

Revision ID: 8f3c6e1b2d42
Revises: e9d17eef1318
Create Date: 2026-05-15 13:00:00.000000

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = "8f3c6e1b2d42"
down_revision: Union[str, Sequence[str], None] = "e9d17eef1318"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade():
    """Complete the UUID migration by renaming _uuid columns and dropping old integer columns"""
    
    # =====================================================
    # 1. DROP OLD FOREIGN KEYS THAT REFERENCE OLD COLUMNS
    # =====================================================
    op.execute("""
        ALTER TABLE businesses
        DROP CONSTRAINT IF EXISTS businesses_owner_id_fkey CASCADE
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
        ALTER TABLE business_customers
        DROP CONSTRAINT IF EXISTS business_customers_business_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE business_customers
        DROP CONSTRAINT IF EXISTS business_customers_user_id_fkey CASCADE
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
        ALTER TABLE appointments
        DROP CONSTRAINT IF EXISTS appointments_walk_in_customer_id_fkey CASCADE
        """)
    
    op.execute("""
        ALTER TABLE payments
        DROP CONSTRAINT IF EXISTS payments_appointment_id_fkey CASCADE
        """)

    # =====================================================
    # 2. RENAME _UUID COLUMNS AND DROP OLD INTEGER COLUMNS
    # =====================================================
    # Businesses - owner_id
    op.execute("ALTER TABLE businesses DROP COLUMN IF EXISTS owner_id")
    op.execute("ALTER TABLE businesses RENAME COLUMN owner_id_uuid TO owner_id")
    
    # Services - business_id
    op.execute("ALTER TABLE services DROP COLUMN IF EXISTS business_id")
    op.execute("ALTER TABLE services RENAME COLUMN business_id_uuid TO business_id")
    
    # Business Hours - business_id
    op.execute("ALTER TABLE business_hours DROP COLUMN IF EXISTS business_id")
    op.execute("ALTER TABLE business_hours RENAME COLUMN business_id_uuid TO business_id")
    
    # Business Customers - business_id and user_id
    op.execute("ALTER TABLE business_customers DROP COLUMN IF EXISTS business_id")
    op.execute("ALTER TABLE business_customers RENAME COLUMN business_id_uuid TO business_id")
    
    op.execute("ALTER TABLE business_customers DROP COLUMN IF EXISTS user_id")
    op.execute("ALTER TABLE business_customers RENAME COLUMN user_id_uuid TO user_id")
    
    # Appointments - user_id, business_id, service_id, walk_in_customer_id
    op.execute("ALTER TABLE appointments DROP COLUMN IF EXISTS user_id")
    op.execute("ALTER TABLE appointments RENAME COLUMN user_id_uuid TO user_id")
    
    op.execute("ALTER TABLE appointments DROP COLUMN IF EXISTS business_id")
    op.execute("ALTER TABLE appointments RENAME COLUMN business_id_uuid TO business_id")
    
    op.execute("ALTER TABLE appointments DROP COLUMN IF EXISTS service_id")
    op.execute("ALTER TABLE appointments RENAME COLUMN service_id_uuid TO service_id")
    
    op.execute("ALTER TABLE appointments DROP COLUMN IF EXISTS walk_in_customer_id")
    op.execute("ALTER TABLE appointments RENAME COLUMN walk_in_customer_id_uuid TO walk_in_customer_id")
    
    # Payments - appointment_id
    op.execute("ALTER TABLE payments DROP COLUMN IF EXISTS appointment_id")
    op.execute("ALTER TABLE payments RENAME COLUMN appointment_id_uuid TO appointment_id")

    # =====================================================
    # 3. RECREATE FOREIGN KEYS
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
