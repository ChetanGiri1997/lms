from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from bson import ObjectId
from .common import PyObjectId  # Assuming you already have the custom PyObjectId class

# Material Schema for Study Materials (PDF, PPTX, DOCs, Videos)
class MaterialModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str  # Title of the material
    description: Optional[str] = None  # Optional description
    file_url: str  # URL where the file is stored (can be S3, local server, etc.)
    file_type: str  # File type (e.g., pdf, pptx, docx, mp4)
    file_size: int  # Size of the file in bytes
    course_id: PyObjectId  # Reference to the course the material is associated with
    uploaded_at: datetime = Field(default_factory=datetime.utcnow)  # Upload timestamp

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
