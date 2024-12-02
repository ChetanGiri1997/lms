from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class EmailSchema(BaseModel):
    recipient: str  # Email address of the recipient
    subject: str  # Subject of the email
    body: str  # Body of the email
    sent_at: Optional[datetime] = None  # Timestamp of when the email was sent
    status: Optional[str] = "pending"  # Status of the email (e.g., pending, sent, failed)
    error_message: Optional[str] = None  # In case of failure, we can store the error message

    class Config:
        orm_mode = True


class EmailHistoryModel(BaseModel):
    recipient: str
    subject: str
    body: str
    sent_at: datetime
    status: str  # "sent", "failed"
    error_message: Optional[str] = None

    class Config:
        orm_mode = True