from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class NotificationSchema(BaseModel):
    title: str  # Title of the notification
    message: str  # Message content of the notification
    recipient_email: str  # Email of the user who will receive the notification
    sent_at: Optional[datetime] = None  # When the notification was sent
    status: Optional[str] = "pending"  # Status of the notification (e.g., pending, sent, failed)
    is_read: bool = False  # Whether the user has read the notification
    error_message: Optional[str] = None  # Error message if sending the notification fails

    class Config:
        orm_mode = True
        
class NotificationHistoryModel(BaseModel):
    title: str
    message: str
    recipient_email: str
    sent_at: datetime
    status: str  # "sent", "failed"
    is_read: bool
    error_message: Optional[str] = None

    class Config:
        orm_mode = True