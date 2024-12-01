from fastapi import APIRouter, Depends, HTTPException, Query
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
# from models.course import CourseOut
from .auth import get_db
from models.course import CourseModel
from bson import ObjectId

router = APIRouter()

async def test_db_connection(db):
    courses = await db["courses"].find().to_list(length=10)
    print("Courses:", courses)  # Check if you can fetch any courses


async def get_db():
    client = AsyncIOMotorClient('mongodb://localhost:27017')
    db = client['local']  # Replace with your database name
    return db

@router.get("/courses", response_model=dict)
async def list_all_courses(
    page: int = Query(1, ge=1),  # Page number, defaults to 1
    limit: int = Query(8, ge=1),  # Limit of courses per page, set to 8
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    skip = (page - 1) * limit  # Calculate the number of courses to skip

    # Access the courses collection and perform the find operation
    total_courses = await db["courses"].count_documents({})  # Total number of courses
    courses_cursor = db["courses"].find().skip(skip).limit(limit)
    courses = await courses_cursor.to_list(length=limit)

    # If no courses were found, raise a 404
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    # Calculate the total number of pages
    total_pages = (total_courses + limit - 1) // limit

    # Return both the list of courses and the total number of pages
    return {
        "courses": [
            {
                "id": str(course["_id"]),  # Convert ObjectId to string
                "name": course["name"],
                "description": course["description"],
                "teachers": course.get("teachers", [])
            } for course in courses
        ],
        "totalPages": total_pages
    }


# @router.put("/api/courses/{course_id}", response_model=CourseOut)
# async def edit_course(course_id: str, course: CourseModel, db=Depends(get_db)):
#     update_result = await db["courses"].update_one(
#         {"_id": ObjectId(course_id)},
#         {"$set": course.dict()}
#     )

#     if update_result.modified_count == 0:
#         raise HTTPException(status_code=404, detail="Course not found")

#     updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
#     return CourseOut(
#         id=str(updated_course["_id"]),
#         name=updated_course["name"],
#         description=updated_course["description"],
#         teachers=updated_course.get("teachers", [])
#     )

# @router.post("/api/courses", response_model=CourseOut)
# async def create_course(course: CourseModel, db=Depends(get_db)):
#     # Convert the course model to a dictionary and insert it into the database
#     course_data = course.dict()
#     result = await db["courses"].insert_one(course_data)
    
#     # Fetch the newly created course from the database to return
#     new_course = await db["courses"].find_one({"_id": result.inserted_id})
    
#     return CourseOut(
#         id=str(new_course["_id"]),
#         name=new_course["name"],
#         description=new_course["description"],
#         teachers=new_course.get("teachers", [])
#     )