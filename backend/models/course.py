from pydantic import BaseModel, Field
from typing import List, Optional, Any
from bson import ObjectId

class PyObjectId(ObjectId):
    @classmethod
    def __get_validators__(cls):
        yield cls.validate

    @classmethod
    def validate(cls, v):
        if not ObjectId.is_valid(v):
            raise ValueError("Invalid objectid")
        return ObjectId(v)

    @classmethod
    def __get_pydantic_json_schema__(cls, field_schema: Any) -> None:
        field_schema.update(type="string")


class TeacherModel(BaseModel):
    id: PyObjectId = Field(default_factory=PyObjectId, alias="_id")
    name: str
    email: Optional[str] = None

    class Config:
        json_encoders = {ObjectId: str}
        arbitrary_types_allowed = True


class CourseModel(BaseModel):
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    name: str
    description: str
    teacher_ids: Optional[List[PyObjectId]] = None  # Support multiple teachers
    teachers: Optional[List[TeacherModel]] = None  # Teacher details can be included optionally

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}


class CourseCreate(BaseModel):
    name: str
    description: str
    teacher_ids: Optional[List[PyObjectId]] = None  # Optional teacher assignment


# class CourseOut(BaseModel):
#     id: str
#     name: str
#     description: str
#     teachers: Optional[List[TeacherModel]] = None  # Include teacher details in the output


class EnrolledCourse(BaseModel):
    id: str
    name: str
    description: str
    teachers: Optional[List[TeacherModel]] = None  # Include teacher details in the enrollment data
    progress: float


class StudentEnrollment(BaseModel):
    student_id: PyObjectId
    course_id: Optional[PyObjectId] = None  # Make course_id optional
    course_name: Optional[str] = None
    course_description: Optional[str] = None
    teachers: Optional[List[TeacherModel]] = None  # Include teachers
    progress: float = 0.0

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {ObjectId: str}
