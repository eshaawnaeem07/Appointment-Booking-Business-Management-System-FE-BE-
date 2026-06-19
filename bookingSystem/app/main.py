from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

from app.api.v1.business import router as business_router
from app.api.v1.auth import router as auth_router
from app.api.v1.business_hours import router as business_hours_router
from app.api.v1.services import router as services_router
from app.api.v1.appointments import router as appointment_router
from app.api.v1.business_customers import router as customers_router
from app.api.v1.payments import router as payments_router

from app.db.base import Base
from app.db.session import engine
from app.models import user, business, appointment, business_hours, payment, service, business_customer

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI()
# CORS
cors_origins = [
    origin.strip()
    for origin in os.getenv(
        "CORS_ORIGINS",
        "http://localhost:5173,http://localhost:3000,http://localhost:8080",
    ).split(",")
    if origin.strip()
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(auth_router)
app.include_router(business_router)
app.include_router(business_hours_router)
app.include_router(services_router)
app.include_router(appointment_router)
app.include_router(customers_router)
app.include_router(payments_router)

# @app.get("/")
# def health():
#     return {"status": "running"}

# @app.get("/test-task")
# def run_test_task():
#     task = test_task.delay()
#     return {
#         "message": "Task sent",
#         "task_id": task.id
#     }
@app.get("/test-task")
def test_task():
    """Test endpoint - verifies Celery is working. Real tasks are created when appointments are booked."""
    from app.workers.tasks import mark_no_show
    from app.workers.celery_app import celery_app
    
    try:
        # Queue a test task (won't find appointment, but verifies queuing works)
        task = mark_no_show.apply_async(
            args=["00000000-0000-0000-0000-000000000000"],
            countdown=5  # 5 seconds delay for quick testing
        )
        
        return {
            "status": "✓ CELERY WORKING",
            "message": "Test task queued successfully",
            "task_id": task.id,
            "note": "Real appointment tasks are created when appointments are booked"
        }
    except Exception as e:
        return {
            "status": "✗ CELERY ERROR",
            "error": str(e),
            "message": "Failed to queue task - check if Redis and Celery worker are running"
        }
