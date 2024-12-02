from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from .common import PyObjectId  # Importing the custom PyObjectId class

# Teacher Schema
class Teacher(BaseModel):
    id: PyObjectId = Field(..., alias="_id")
    name: str
    role: str  # Should be "teacher" or "admin"

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# Student Schema for completed assignments
class StudentCompletion(BaseModel):
    student_id: PyObjectId = Field(..., alias="_id")
    student_name: str
    completed_at: datetime  # Timestamp when the student marks the assignment as completed

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# Assignment Model
class Assignment(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None  # Deadline for assignment submission
    teacher: Teacher  # The teacher who assigns the assignment
    students_completed: List[StudentCompletion] = Field(default_factory=list)  # List of students who have completed it
    course_id: PyObjectId = Field(..., alias="course_id")  # The course this assignment belongs to

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

# Schema for Creating a New Assignment (only necessary fields for creation)
class AssignmentCreate(BaseModel):
    title: str
    description: Optional[str] = None
    deadline: Optional[datetime] = None
    teacher_id: PyObjectId  # ID of the teacher assigning the assignment
    course_id: PyObjectId  # The ID of the course to which the assignment belongs

    class Config:
        arbitrary_types_allowed = True
        json_encoders = {PyObjectId: str}

