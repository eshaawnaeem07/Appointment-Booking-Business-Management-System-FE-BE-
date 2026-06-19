from enum import Enum


class UserRole(str, Enum):
    USER = "user"
    BUSINESS = "business"


class AppointmentStatus(str, Enum):
    PENDING = "pending"          # waiting for payment (if required)
    CONFIRMED = "confirmed"
    COMPLETED = "completed"
    NO_SHOW = "no_show"


class PaymentStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    FAILED = "failed"


class DayEnum(str, Enum):
    monday = "Monday"  
    tuesday = "Tuesday"
    wednesday = "Wednesday"
    thursday = "Thursday"
    friday = "Friday"
    saturday = "Saturday"
    sunday = "Sunday"