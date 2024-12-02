import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi import HTTPException
from models.smtp import EmailSchema
from models.smtp import EmailHistoryModel
from typing import Dict
from datetime import datetime
from bson import ObjectId
from fastapi.responses import JSONResponse
from routers.auth import get_db


def send_email_via_smtp(db, email: EmailSchema):
    try:
        # SMTP server details (example: Gmail)
        smtp_host = "smtp.gmail.com"
        smtp_port = 587
        sender_email = "your-email@gmail.com"  # Your email address
        sender_password = "your-email-password"  # Your email password (use environment variables or secrets for security)

        # Create the MIME message
        msg = MIMEMultipart()
        msg["From"] = sender_email
        msg["To"] = email.recipient
        msg["Subject"] = email.subject
        msg.attach(MIMEText(email.body, "plain"))

        # Set up the SMTP connection and send the email
        with smtplib.SMTP(smtp_host, smtp_port) as server:
            server.starttls()  # Secure the connection
            server.login(sender_email, sender_password)
            server.sendmail(sender_email, email.recipient, msg.as_string())

        # Record the email history in the database
        email_history = EmailHistoryModel(
            recipient=email.recipient,
            subject=email.subject,
            body=email.body,
            sent_at=datetime.utcnow(),
            status="sent"
        )
        # Insert into the email history collection in MongoDB
        db["email_history"].insert_one(email_history.dict())

        return JSONResponse(status_code=200, content={"message": "Email sent successfully."})

    except Exception as e:
        # On failure, record the error message
        email_history = EmailHistoryModel(
            recipient=email.recipient,
            subject=email.subject,
            body=email.body,
            sent_at=datetime.utcnow(),
            status="failed",
            error_message=str(e)
        )
        # Insert into the email history collection
        db["email_history"].insert_one(email_history.dict())

        raise HTTPException(status_code=500, detail=f"Error sending email: {str(e)}")
