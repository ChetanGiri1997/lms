from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .common import PyObjectId  # Importing the custom PyObjectId class

# User Ownership Schema
class Owner(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    name: str
    role: str  # Can be "admin" or "teacher"

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}


# Assignment Schema
class Assignment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    completed_by: List[dict] = Field(default_factory=list)  # List of {"student_id": ..., "completion_timestamp": ...}

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}


# Main Course Model
class CourseModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    owner: Owner  # Owner (teacher or admin who created the course)
    teachers: List[Owner] = Field(default_factory=list)  # Additional teachers
    students: List[dict] = Field(default_factory=list)  # List of {"id": student_id, "name": student_name}
    assignments: List[Assignment] = Field(default_factory=list)  # Assignments within the course
    archived: bool = Field(default=False)  # Whether the course is archived
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}
        populate_by_name = True


# Schema for Creating a New Course
class CourseCreate(BaseModel):
    name: str
    description: str
    teacher_ids: Optional[List[PyObjectId]] = None  # Initial teachers to add

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

############################################################################################################
# Schema for Creating a New Assignment
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None

    class Config:
        arbitrary_types_allowed = True


# Schema for Archiving or Unarchiving a Course
class CourseArchiveAction(BaseModel):
    archived: bool  # True for archiving, False for unarchiving

    class Config:
        arbitrary_types_allowed = True
