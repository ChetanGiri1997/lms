from fastapi import APIRouter, Depends, HTTPException, Query, Body, status
from motor.motor_asyncio import AsyncIOMotorClient
from typing import List
from .auth import get_db, get_current_user
from models.assignment import  Assignment, AssignmentCreate, StudentCompletion
from bson import ObjectId
from datetime import datetime
from models.common import PyObjectId

router = APIRouter()



# 1. Create an Assignment
@router.post("/assignments", response_model=Assignment)
async def create_assignment(
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Verify if the course exists
    course = await db["courses"].find_one({"_id": ObjectId(assignment_data.course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Verify if the user is a teacher or admin
    if current_user["role"] not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Only teachers and admins can create assignments")

    # Create the assignment document
    assignment = {
        "title": assignment_data.title,
        "description": assignment_data.description,
        "deadline": assignment_data.deadline,
        "teacher": {"_id": current_user["_id"], "name": current_user["name"], "role": current_user["role"]},
        "students_completed": [],
        "course_id": assignment_data.course_id
    }

    # Insert the assignment into the database
    result = await db["assignments"].insert_one(assignment)
    assignment["_id"] = result.inserted_id

    return Assignment(**assignment)

# 2. List Assignments for a Course
@router.get("/courses/{course_id}/assignments", response_model=List[Assignment])
async def list_assignments(
    course_id: str,
    current_user = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Verify if the course exists
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Retrieve assignments for the course
    assignments = await db["assignments"].find({"course_id": ObjectId(course_id)}).to_list(length=100)
    
    return [Assignment(**assignment) for assignment in assignments]

# 3. Get Assignment Details by ID
@router.get("/assignments/{assignment_id}", response_model=Assignment)
async def get_assignment(
    assignment_id: str,
    current_user = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Retrieve assignment by ID
    assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    return Assignment(**assignment)

# 4. Mark Assignment as Completed by Student
@router.patch("/assignments/{assignment_id}/complete", response_model=Assignment)
async def mark_assignment_completed(
    assignment_id: str,
    student_id: PyObjectId,
    db = Depends(get_db),
    current_user: dict = Depends(get_current_user)  # Ensure the user is authenticated
):
    # Retrieve the assignment by ID
    assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")
    
    # Check if the student is enrolled in the course
    course = await db["courses"].find_one({"_id": ObjectId(assignment["course_id"])})
    if student_id not in [student["_id"] for student in course["students"]]:
        raise HTTPException(status_code=403, detail="Student is not enrolled in the course")

    # Check if the assignment is already completed
    for student in assignment["students_completed"]:
        if student["student_id"] == student_id:
            raise HTTPException(status_code=400, detail="Assignment already completed by this student")

    # Mark the assignment as completed
    student_name = next(student["name"] for student in course["students"] if student["_id"] == student_id)
    completed_data = StudentCompletion(
        student_id=student_id,
        student_name=student_name,
        completed_at=datetime.utcnow()
    )
    
    # Add the student completion data to the assignment
    await db["assignments"].update_one(
        {"_id": ObjectId(assignment_id)},
        {"$push": {"students_completed": completed_data.dict()}}
    )

    # Return the updated assignment
    updated_assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    return Assignment(**updated_assignment)

# 5. Update Assignment
@router.put("/assignments/{assignment_id}", response_model=Assignment)
async def update_assignment(
    assignment_id: str,
    assignment_data: AssignmentCreate,
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Retrieve the assignment by ID
    assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check if the user is the teacher who created the assignment or an admin
    if assignment["teacher"]["_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only the teacher or admin can update this assignment")

    # Prepare update data
    update_data = {k: v for k, v in assignment_data.dict().items() if v is not None}
    
    # Update the assignment in the database
    await db["assignments"].update_one({"_id": ObjectId(assignment_id)}, {"$set": update_data})

    # Return the updated assignment
    updated_assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    return Assignment(**updated_assignment)

# 6. Delete Assignment
@router.delete("/assignments/{assignment_id}", response_model=dict)
async def delete_assignment(
    assignment_id: str,
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)
):
    # Retrieve the assignment by ID
    assignment = await db["assignments"].find_one({"_id": ObjectId(assignment_id)})
    if not assignment:
        raise HTTPException(status_code=404, detail="Assignment not found")

    # Check if the user is the teacher who created the assignment or an admin
    if assignment["teacher"]["_id"] != current_user["_id"] and current_user["role"] != "admin":
        raise HTTPException(status_code=403, detail="Only the teacher or admin can delete this assignment")

    # Delete the assignment
    await db["assignments"].delete_one({"_id": ObjectId(assignment_id)})

    return {"status": "success", "message": "Assignment deleted"}
