from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from .auth import get_db, get_current_user
from models.course import CourseModel, CourseCreate, CourseArchiveAction
from bson import ObjectId
import time

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
    current_user = Depends(get_current_user),  # Ensure the user is authenticated
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

@router.post("/courses", response_model=CourseModel)
async def add_course(
    course_data: CourseCreate,
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Check if the user is a teacher or admin
    if current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can add courses")

    # Prepare the course document
    course = {
        "name": course_data.name,
        "description": course_data.description,
        "owner": {"_id": current_user["_id"], "name": current_user["name"], "role": current_user["role"]},
        "teachers": [{"_id": current_user["_id"], "name": current_user["name"]}],
        "students": [],
        "assignments": [],
        "archived": False,
        "created_at": time.datetime.utcnow()
    }

    # Insert into the database
    result = await db["courses"].insert_one(course)
    course["_id"] = result.inserted_id

    return CourseModel(**course)

@router.put("/courses/{course_id}", response_model=CourseModel)
async def edit_course(
    course_id: str,
    course_data: dict = Body(...),  # Accept partial updates
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    # Fetch the course
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is the owner or an admin
    if course["owner"]["_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only the course owner or admin can edit this course")

    # Update the course
    update_data = {k: v for k, v in course_data.items() if v is not None}  # Only update provided fields
    await db["courses"].update_one({"_id": ObjectId(course_id)}, {"$set": update_data})

    # Return the updated course
    updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    return CourseModel(**updated_course)

@router.patch("/courses/{course_id}/archive", response_model=dict)
async def archive_course(
    course_id: str,
    action: CourseArchiveAction,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    # Fetch the course
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is the owner or an admin
    if course["owner"]["_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only the course owner or admin can archive this course")

    # Update the archived status
    await db["courses"].update_one({"_id": ObjectId(course_id)}, {"$set": {"archived": action.archived}})

    return {"status": "success", "archived": action.archived}


# New endpoint for enrolling in a course
@router.post("/courses/{course_id}/enroll", response_model=CourseModel)
async def enroll_in_course(
    course_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    # Fetch the course
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is already enrolled
    if any(student["_id"] == current_user["_id"] for student in course["students"]):
        raise HTTPException(status_code=400, detail="User is already enrolled in this course")

    # Enroll the user by adding their ID to the students list
    await db["courses"].update_one(
        {"_id": ObjectId(course_id)},
        {"$push": {"students": {"_id": current_user["_id"], "name": current_user["name"]}}}
    )

    # Return the updated course
    updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    return CourseModel(**updated_course)


# New endpoint for opting out of a course
@router.post("/courses/{course_id}/optout", response_model=CourseModel)
async def opt_out_of_course(
    course_id: str,
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    # Fetch the course
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is enrolled in the course
    student = next((s for s in course["students"] if str(s["_id"]) == str(current_user["_id"])), None)
    if not student:
        raise HTTPException(status_code=400, detail="User is not enrolled in this course")

    # Opt-out the user by removing their ID from the students list
    await db["courses"].update_one(
        {"_id": ObjectId(course_id)},
        {"$pull": {"students": {"_id": current_user["_id"]}}}
    )

    # Return the updated course
    updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    return CourseModel(**updated_course)
