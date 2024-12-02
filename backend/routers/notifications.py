from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from models.notifications import NotificationSchema, NotificationHistoryModel
from utils.notifications import create_notification
from .auth import get_current_user, get_db  # Ensure user is authenticated
from utils.notifications import mark_notification_as_read

router = APIRouter()

# Endpoint to create a notification
@router.post("/create-notification")
async def create_notification_endpoint(
    notification: NotificationSchema,  # The notification schema to define the data
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Dependency to get DB connection
):
    try:
        # Create the notification using the utility function
        response = create_notification(db, notification)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Endpoint to get a list of notifications for the current user
@router.get("/notifications", response_model=list[NotificationHistoryModel])
async def get_notifications(
    current_user: dict = Depends(get_current_user),  # Ensure user is authenticated
    db = Depends(get_db),  # Database connection
    limit: int = 10,  # Number of records to fetch per request
    page: int = 1,  # Pagination support
):
    skip = (page - 1) * limit
    try:
        # Fetch notifications for the current user from the database
        notifications = await db["notification_history"].find({"recipient_email": current_user["email"]}) \
            .skip(skip).limit(limit).to_list(length=limit)
        
        if not notifications:
            raise HTTPException(status_code=404, detail="No notifications found")
        
        return notifications
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error fetching notifications")

@router.patch("/mark-as-read/{notification_id}")
async def mark_notification_as_read(
    notification_id: str,
    current_user: dict = Depends(get_current_user),  # Notification ID to mark as read
    db = Depends(get_db)  # Database connection
):
    try:
        # Mark the notification as read using the utility function
        response = mark_notification_as_read(db, notification_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

