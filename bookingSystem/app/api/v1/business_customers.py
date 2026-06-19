from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.services.business_customer_services import CustomerService
from app.schemas.business_customer import (
    CustomerCreate, CustomerUpdate, CustomerOut
)
from app.core.dependencies import get_current_user
from uuid import UUID

router = APIRouter(tags=["Business Customers"])
#get all customers for a business
@router.get("/businesses/{id}/customers", response_model=list[CustomerOut])
def get_customers(id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return CustomerService.get_all(db, id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customers: {str(e)}")
#get one customer for a business
@router.get("/businesses/{id}/customers/{customer_id}", response_model=CustomerOut)
def get_customer(id: UUID, customer_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return CustomerService.get_one(db, id, customer_id, user)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to fetch customer: {str(e)}")
#create a customer for a business
@router.post("/businesses/{id}/customers", response_model=CustomerOut)
def create_customer(id: UUID, payload: CustomerCreate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return CustomerService.create(db, id, user, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create customer: {str(e)}")
#update a customer for a business
@router.put("/businesses/{id}/customers/{customer_id}", response_model=CustomerOut)
def update_customer(id: UUID, customer_id: UUID, payload: CustomerUpdate, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        return CustomerService.update(db, id, customer_id, user, payload)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update customer: {str(e)}")
    
#delete a customer for a business
@router.delete("/businesses/{id}/customers/{customer_id}")
def delete_customer(id: UUID, customer_id: UUID, db: Session = Depends(get_db), user=Depends(get_current_user)):
    try:
        CustomerService.delete(db, id, customer_id, user)
        return {"message": "Deleted"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to delete customer: {str(e)}")