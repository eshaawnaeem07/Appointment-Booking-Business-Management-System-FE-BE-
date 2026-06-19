from fastapi import HTTPException
from app.models.business_customer import BusinessCustomer
from app.utils.business_utils import get_owned_business_or_403
from app.utils.customer_utils import get_customer_or_404
from app.utils.db_utils import commit_and_refresh

class CustomerService:
    @staticmethod
    def get_all(db, business_id, user):
        try:
            get_owned_business_or_403(db, business_id, user)

            return db.query(BusinessCustomer).filter(
                BusinessCustomer.business_id == business_id
            ).all()

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch customers: {str(e)}"
            )

    @staticmethod
    def get_one(db, business_id, customer_id, user):
        try:
            customer = get_customer_or_404(db, business_id, customer_id, user)
            return customer

        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(
                status_code=500,
                detail=f"Failed to fetch customer: {str(e)}")

    @staticmethod
    def create(db, business_id, user, payload):
        try:
            get_owned_business_or_403(db, business_id, user)

            customer = BusinessCustomer(
                business_id=business_id,
                name=payload.name,
                phone=payload.phone,
                email=payload.email)

            db.add(customer)
            return commit_and_refresh(db, customer)

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to create customer: {str(e)}"
            )

    @staticmethod
    def update(db, business_id, customer_id, user, payload):
        try:
            customer = get_customer_or_404(db, business_id, customer_id, user)

            # Build update data, excluding None values
            update_data = payload.dict(exclude_unset=True, exclude_none=True)
            
            # Ensure email is not empty if provided
            if 'email' in update_data and not update_data['email']:
                raise HTTPException(
                    status_code=400,
                    detail="Email cannot be empty"
                )

            for key, value in update_data.items():
                setattr(customer, key, value)

            return commit_and_refresh(db, customer)

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to update customer: {str(e)}")

    @staticmethod
    def delete(db, business_id, customer_id, user):
        try:
            customer = get_customer_or_404(db, business_id, customer_id, user)

            db.delete(customer)
            db.commit()

        except HTTPException:
            raise
        except Exception as e:
            db.rollback()
            raise HTTPException(
                status_code=500,
                detail=f"Failed to delete customer: {str(e)}"
            )