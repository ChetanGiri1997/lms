from fastapi import APIRouter, Depends, HTTPException, Form, BackgroundTasks
from fastapi.responses import JSONResponse
from models.smtp import EmailSchema, EmailHistoryModel
from .auth import get_db
from utils.smtp import send_email_via_smtp
from typing import List
from .auth import get_current_user

router = APIRouter()

@router.post("/send-email")
async def send_email(
    email: EmailSchema,  # The email schema you define earlier
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Dependency to get DB connection
):
    try:
        # Send the email using the SMTP utility function
        response = send_email_via_smtp(db, email)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/mail", response_model=List[EmailHistoryModel])
async def get_mail_history(
    current_user: dict = Depends(get_current_user),  # Ensure user is authenticated
    db = Depends(get_db),  # Database connection
    limit: int = 10,  # Number of records to fetch per request
    page: int = 1,  # Pagination support
):
    skip = (page - 1) * limit
    try:
        # Fetch notifications (email history) for the current user from the database
        notifications = await db["email_history"].find({"recipient": current_user["email"]}) \
            .skip(skip).limit(limit).to_list(length=limit)
        
        if not notifications:
            raise HTTPException(status_code=404, detail="No notifications found")
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching notification history")