from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from .auth import get_current_user, get_db
from models.course import CourseModel, CourseCreate, CourseArchiveAction
from models.user import UserInDB
from bson import ObjectId
from datetime import datetime


router = APIRouter()

@router.get("/courses", response_model=dict)
async def list_all_courses(
    page: int = Query(1, ge=1),  # Page number, defaults to 1
    limit: int = Query(8, ge=1),  # Limit of courses per page, set to 8
    current_user = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    skip = (page - 1) * limit  # Calculate the number of courses to skip

    # Filter for non-archived courses
    filter_condition = {"archived": False}

    # Fetch the total number of non-archived courses
    total_courses = await db["courses"].count_documents(filter_condition)
    
    # Fetch paginated non-archived courses
    courses_cursor = db["courses"].find(filter_condition).skip(skip).limit(limit)
    courses = await courses_cursor.to_list(length=limit)

    # If no courses are found, raise an HTTP exception
    if not courses:
        raise HTTPException(status_code=404, detail="No courses found")

    # Calculate total pages
    total_pages = (total_courses + limit - 1) // limit

    # Transform the course data into the required format
    formatted_courses = [
        {
            "id": str(course["_id"]),  # Convert ObjectId to string
            "name": course["name"],
            "description": course["description"],
            "owner": course["owner"],
            "teachers": course.get("teachers", []),
            "students": course.get("students", []),
            "assignments": course.get("assignments", []),
            "archived": course.get("archived", False),
            "created_at": course.get("created_at")
        } for course in courses
    ]

    # Return the paginated response
    return {
        "courses": formatted_courses,
        "totalPages": total_pages
    }



@router.post("/courses", response_model=CourseModel)
async def add_course(
    course_data: CourseCreate,
    current_user: UserInDB = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Check if the user is a teacher or admin
    if current_user.role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can add courses")

    # Prepare the course document
    course = {
        "name": course_data.name,
        "description": course_data.description,
        "owner": {"_id": current_user.id, "name": current_user.username, "role": current_user.role},
        "teachers": [
            {"_id": current_user.id, "name": current_user.username, "role": current_user.role}
        ],
        "students": [],
        "assignments": [],
        "archived": False,
        "created_at": datetime.utcnow()
    }

    # Insert into the database
    result = await db["courses"].insert_one(course)
    course["_id"] = result.inserted_id

    return CourseModel(**course)

@router.put("/courses/{course_id}", response_model=CourseModel)
async def edit_course(
    course_id: str,
    course_data: dict = Body(...),  # Accept partial updates
    current_user: UserInDB = Depends(get_current_user),  # Assuming current_user is an instance of UserInDB
    db = Depends(get_db)
):
    # Fetch the course from the database
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is the owner or an admin
    if course["owner"]["_id"] != str(current_user.id) and current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Only the course owner or admin can edit this course")

    # Update the course with the provided data
    update_data = {k: v for k, v in course_data.items() if v is not None}  # Only update provided fields
    await db["courses"].update_one({"_id": ObjectId(course_id)}, {"$set": update_data})

    # Return the updated course
    updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    return CourseModel(
        id=str(updated_course["_id"]),
        name=updated_course["name"],
        description=updated_course["description"],
        owner=updated_course["owner"],
        archived=updated_course["archived"]
        
    )

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
    if course["owner"]["_id"] != current_user.id and current_user.role != "admin":
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
    # Ensure the current user has the "student" role
    if current_user.role != "student":
        raise HTTPException(
            status_code=403, detail="Only students are allowed to enroll in courses"
        )

    # Fetch the course from the database
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is already enrolled in the course
    if any(student["_id"] == current_user.id for student in course.get("students", [])):
        raise HTTPException(status_code=400, detail="User is already enrolled in this course")

    # Enroll the user by adding their ID and name to the students array
    await db["courses"].update_one(
        {"_id": ObjectId(course_id)},
        {"$push": {"students": {"_id": current_user.id, "name": current_user.username}}}
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
    # Fetch the course from the database
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Check if the user is enrolled in the course
    student = next((s for s in course.get("students", []) if str(s["_id"]) == str(current_user.id)), None)
    if not student:
        raise HTTPException(status_code=400, detail="User is not enrolled in this course")

    # Opt-out the user by removing their ID from the students list
    await db["courses"].update_one(
        {"_id": ObjectId(course_id)},
        {"$pull": {"students": {"_id": current_user.id}}}
    )

    # Return the updated course
    updated_course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    return CourseModel(**updated_course)

async def get_course_edit_data(course_id: str, db = Depends(get_db)) -> dict:
    # Fetch the course data by ID
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Extract and return only limited data for editing (e.g., name, description, teachers)
    edit_data = {
        "name": course["name"],
        "description": course["description"],
        "teacher_ids": [teacher["_id"] for teacher in course.get("teachers", [])],  # List of teacher IDs
        "archived": course["archived"]
    }
    
    return edit_data

async def get_course_dashboard_data(course_id: str, db = Depends(get_db)) -> CourseModel:
    # Fetch the full course details by ID
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")
    
    # Return the full course data as a CourseModel
    return CourseModel(**course)

@router.get("/courses/{course_id}", response_model=CourseModel)
async def fetch_course_for_dashboard(course_id: str, db = Depends(get_db)):
    return await get_course_dashboard_data(course_id, db)

# Route to get limited course data for editing
@router.get("/courses/{course_id}/edit")
async def fetch_course_for_edit(course_id: str, db = Depends(get_db)):
    return await get_course_edit_data(course_id, db)