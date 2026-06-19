from sqlalchemy.orm import Session
from sqlalchemy import func
from app.models.user import User
from app.core.security import hash_password, verify_password, create_access_token
from datetime import datetime, timedelta
from app.utils.enums import UserRole
from app.core.security import generate_refresh_token


class AuthService:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_email(email: str) -> str:
        return email.strip().lower()

    def register_user(self, email: str, password: str, role):
        email = self._normalize_email(email)
        existing = self.db.query(User).filter(func.lower(func.trim(User.email)) == email).first()
        if existing:
            raise Exception("Email already exists")
        if role not in [UserRole.USER.value, UserRole.BUSINESS.value]:
            raise Exception("Input should be 'user' or 'business'")

        user = User(
            email=email,
            password=hash_password(password),
            role=role.lower()
        )

        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def login_user(self, email, password):
        email = self._normalize_email(email)
        user = self.db.query(User).filter(func.lower(func.trim(User.email)) == email).first()

        if not user or not verify_password(password, user.password):
            raise Exception("Invalid credentials")

        access_token = create_access_token({
            "sub": user.email,
            "role": user.role
        })
        refresh_token = generate_refresh_token()
        user.refresh_token = refresh_token
        user.refresh_token_expiry = datetime.utcnow() + timedelta(days=7)

        self.db.commit()

        return {
            "access_token": access_token,
            "refresh_token": refresh_token
        }

    def logout_user(self, email: str):
        email = self._normalize_email(email)
        user = self.db.query(User).filter(func.lower(func.trim(User.email)) == email).first()

        if not user:
            raise Exception("User not found")

        user.refresh_token = None
        user.refresh_token_expiry = None

        self.db.commit()

    def save_otp(self, user_id: int, otp: str):
        """Save OTP and expiry time in DB for the user"""
        user = self.db.query(User).filter(User.id == user_id).first()
        if not user:
            raise Exception("User not found")

        user.reset_token = otp
        user.token_expiry = datetime.utcnow() + timedelta(minutes=10)  # OTP valid for 10 mins
        self.db.commit()

    def get_user_by_email(self, email: str):
        """Fetch user by email"""
        email = self._normalize_email(email)
        return self.db.query(User).filter(func.lower(func.trim(User.email)) == email).first()

    def verify_otp_and_get_user(self, email: str, otp: str):
        """Verify OTP and return user if valid"""
        user = self.get_user_by_email(email)
        if not user:
            raise Exception("User not found")
        if (
            user.reset_token != otp
            or not user.token_expiry
            or user.token_expiry < datetime.utcnow()
        ):
            raise Exception("Invalid or expired OTP")
        return user

    def update_password(self, user: User, new_password: str):
        """Update user password and clear OTP"""
        user.password = hash_password(new_password)
        # clear OTP after use
        user.reset_token = None
        user.token_expiry = None

        self.db.commit()
