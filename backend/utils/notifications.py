from datetime import datetime
from fastapi import HTTPException
from models.notifications import NotificationSchema, NotificationHistoryModel
from routers.auth import get_db
from models.common import ObjectId


def create_notification(db, notification: NotificationSchema):
    try:
        # Save the notification in the database
        notification_dict = notification.dict()
        notification_dict["sent_at"] = datetime.utcnow()

        # Insert notification into the database
        db["notifications"].insert_one(notification_dict)

        # Record the notification in the notification history collection
        notification_history = NotificationHistoryModel(
            title=notification.title,
            message=notification.message,
            recipient_email=notification.recipient_email,
            sent_at=datetime.utcnow(),
            status="sent",
            is_read=False
        )

        # Insert into the notification history collection
        db["notification_history"].insert_one(notification_history.dict())

        return {"message": "Notification created successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error creating notification: {str(e)}")
    
def mark_notification_as_read(db, notification_id: str):
    try:
        # Find and update the notification as read
        result = db["notification_history"].update_one(
            {"_id": ObjectId(notification_id)},
            {"$set": {"is_read": True}}
        )

        if result.matched_count == 0:
            raise HTTPException(status_code=404, detail="Notification not found")

        return {"message": "Notification marked as read successfully."}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error updating notification: {str(e)}")

