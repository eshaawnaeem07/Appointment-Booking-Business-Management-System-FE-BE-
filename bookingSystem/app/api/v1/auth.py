from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import timedelta
from app.db.session import get_db
from app.schemas import auth as auth_schema
from app.services.auth_service import AuthService
from app.core import security
from app.services.email_service import EmailService
from app.utils.constants import FROM_EMAIL

router = APIRouter(prefix="/auth", tags=["auth"])

#Register
@router.post("/register", response_model=auth_schema.UserResponse)
def register(user_in: auth_schema.UserCreate, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        return auth_service.register_user(
            email=user_in.email,
            password=user_in.password,
            role=user_in.role
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Login (Returns JWT + Refresh Token)
@router.post("/login")
def login(user_in: auth_schema.UserLogin, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        return auth_service.login_user(
            email=user_in.email,
            password=user_in.password
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Refresh Token
@router.post("/refresh-token")
def refresh_token(
    token_in: auth_schema.RefreshTokenRequest,
    db: Session = Depends(get_db)
):
    try:
        user = security.verify_refresh_token(db, token_in.refresh_token)

        new_access_token = security.create_access_token({
            "sub": user.email,
            "role": user.role
        })

        return {
            "access_token": new_access_token,
            "token_type": "bearer"
        }

    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

# Forgot Password (Generates OTP & Sends via SendGrid)
@router.post("/forgot-password")
def forgot_password(request: auth_schema.ForgotPasswordRequest, db: Session = Depends(get_db)):
    try:
        auth_service = AuthService(db)
        user = auth_service.get_user_by_email(request.email)
        if not user:
            raise HTTPException(status_code=404, detail="Email not found")

        otp = "5678"  #OTP

        auth_service.save_otp(user.id, otp)
        EmailService.send_otp_email(user.email, otp)

        return {"message": "OTP sent to your email"}

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Reset Password (OTP Verification + Password Match)
@router.post("/reset-password")
def reset_password(req: auth_schema.ResetPasswordRequest, db: Session = Depends(get_db)):
    try:
        # Check if passwords match
        if req.new_password != req.confirm_password:
            raise HTTPException(status_code=400, detail="Passwords do not match")
        
        auth_service = AuthService(db)
        # Validate OTP
        user = auth_service.verify_otp_and_get_user(req.email, req.otp)
        if not user:
            raise HTTPException(status_code=400, detail="Invalid or expired OTP")
        
        # Update Password
        auth_service.update_password(user, req.new_password)
        return {"message": "Password updated successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
    
# Logout (Handled on client by deleting tokens; server can blacklist)
@router.post("/logout")
def logout():
    try:
        return {"message": "Successfully logged out"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
