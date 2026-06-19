from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from uuid import UUID

from app.db.session import get_db
from app.services.business_service import BusinessService
from app.schemas.business import BusinessCreate, BusinessUpdate, BusinessOut
from app.core.dependencies import require_roles
from app.utils.enums import UserRole

router = APIRouter(prefix="/businesses", tags=["Businesses"])

# GET ALL BUSINESSES
@router.get("/", response_model=list[BusinessOut])
def get_all_businesses(db: Session = Depends(get_db)):
    """
    Retrieve all businesses (public endpoint).
    Returns:
        List of all businesses stored in the system.
    """
    try:
        service = BusinessService(db)
        return service.get_all()

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch businesses: {str(e)}"
        )

# GET MY BUSINESSES
@router.get("/mine", response_model=list[BusinessOut])
def get_my_businesses(
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.BUSINESS))
):
    """
    Retrieve businesses owned by the current business user.
    """
    try:
        service = BusinessService(db)
        return service.get_mine(user)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch businesses: {str(e)}"
        )

# GET BUSINESS BY ID
@router.get("/{id}", response_model=BusinessOut)
def get_business(id: UUID, db: Session = Depends(get_db)):
    """
    Retrieve a single business by its ID.

    Args:
        id (UUID): Business ID

    Returns:
        BusinessOut: Business details
    """
    try:
        service = BusinessService(db)
        return service.get_by_id(id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch business: {str(e)}"
        )

# CREATE BUSINESS
@router.post("/", response_model=BusinessOut)
def create_business(
    data: BusinessCreate,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.BUSINESS))
):
    """
    Create a new business (BUSINESS role only).

    Args:
        data (BusinessCreate): Business creation payload
        user: Authenticated business user

    Returns:
        BusinessOut: Created business
    """
    try:
        service = BusinessService(db)
        return service.create(user, data)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business creation failed: {str(e)}"
        )

# UPDATE BUSINESS
# @router.put("/{id}", response_model=BusinessOut)
# def update_business(
#     id: UUID,
#     data: BusinessUpdate,
#     db: Session = Depends(get_db),
#     user=Depends(require_roles(UserRole.BUSINESS))
# ):
#     """
#     Update an existing business (OWNER only).

#     Args:
#         id (UUID): Business ID
#         data (BusinessUpdate): Fields to update
#         user: Authenticated owner

#     Returns:
#         BusinessOut: Updated business
#     """
#     try:
#         service = BusinessService(db)
#         return service.update(user, id, data)

#     except HTTPException:
#         raise

#     except Exception as e:
#         raise HTTPException(
#             status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
#             detail=f"Business update failed: {str(e)}"
#         )

# DELETE BUSINESS (SOFT DELETE)
@router.delete("/{id}")
def delete_business(
    id: UUID,
    db: Session = Depends(get_db),
    user=Depends(require_roles(UserRole.BUSINESS))
):
    """
    Soft delete a business (OWNER only).
    Args:
        id (UUID): Business ID
        user: Authenticated owner
    Returns:
        dict: Deletion confirmation message
    """
    try:
        service = BusinessService(db)
        return service.delete(user, id)

    except HTTPException:
        raise

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Business deletion failed: {str(e)}"
        )
