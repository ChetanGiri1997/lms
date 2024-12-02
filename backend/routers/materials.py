from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from fastapi.responses import JSONResponse
from bson import ObjectId
from typing import List
from .auth import get_db, get_current_user
from models.materials import MaterialModel  # Assuming the MaterialModel is in the models/material.py file
import os
import shutil
from models.common import PyObjectId

router = APIRouter()

# Define upload directory for study materials
UPLOAD_DIR = "materials"  # Adjust the directory as per your requirements

# Ensure the upload directory exists
os.makedirs(UPLOAD_DIR, exist_ok=True)

# API to upload study material
@router.post("/materials", response_model=MaterialModel)
async def upload_material(
    title: str = Form(...),  # Title of the material
    description: str = Form(None),  # Optional description
    course_id: PyObjectId = Form(...),  # Course ID the material belongs to
    file: UploadFile = File(...),  # The uploaded file
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    # Check if the course exists
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Save the uploaded file to the server
    file_location = os.path.join(UPLOAD_DIR, file.filename)
    with open(file_location, "wb") as f:
        shutil.copyfileobj(file.file, f)
    
    # Calculate file size (in bytes)
    file_size = os.path.getsize(file_location)
    
    # Create the material document in the database
    material = MaterialModel(
        title=title,
        description=description,
        file_url=file_location,  # Store the file path or URL
        file_type=file.content_type,
        file_size=file_size,
        course_id=course_id
    )
    
    # Insert the material into the database
    result = await db["materials"].insert_one(material.dict())
    
    # Return the material details
    material.id = str(result.inserted_id)  # Convert ObjectId to string
    return material

@router.get("/materials/{course_id}", response_model=List[MaterialModel])
async def list_materials_for_course(
    course_id: PyObjectId,  # Course ID to filter materials
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    # Check if the course exists
    course = await db["courses"].find_one({"_id": ObjectId(course_id)})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    # Get the materials for the course
    materials = await db["materials"].find({"course_id": course_id}).to_list(length=100)
    
    # If no materials are found, return an empty list
    if not materials:
        return []

    return [MaterialModel(**material) for material in materials]



@router.put("/materials/{material_id}", response_model=MaterialModel)
async def edit_material(
    material_id: PyObjectId,  # Material ID to edit
    title: str = Form(...),  # New title of the material
    description: str = Form(None),  # Optional new description
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    # Find the material by ID
    material = await db["materials"].find_one({"_id": ObjectId(material_id)})
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Check if the current user is an admin or course owner
    course = await db["courses"].find_one({"_id": ObjectId(material["course_id"])})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user["role"] not in ["admin", "owner"] and str(current_user["_id"]) != str(course["owner_id"]):
        raise HTTPException(status_code=403, detail="You do not have permission to edit this material")

    # Update the material's metadata
    update_data = {
        "title": title,
        "description": description
    }

    # Update the material in the database
    result = await db["materials"].update_one({"_id": ObjectId(material_id)}, {"$set": update_data})

    # If the material was not found or updated, raise an error
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Material not found")

    # Fetch the updated material
    updated_material = await db["materials"].find_one({"_id": ObjectId(material_id)})

    return MaterialModel(**updated_material)


@router.delete("/materials/{material_id}", response_model=MaterialModel)
async def archive_material(
    material_id: PyObjectId,  # Material ID to archive
    current_user: dict = Depends(get_current_user),  # Ensure the user is authenticated
    db = Depends(get_db)  # Ensure get_db returns a valid collection or database object
):
    # Find the material by ID
    material = await db["materials"].find_one({"_id": ObjectId(material_id)})
    if not material:
        raise HTTPException(status_code=404, detail="Material not found")

    # Check if the current user is an admin or course owner
    course = await db["courses"].find_one({"_id": ObjectId(material["course_id"])})
    if not course:
        raise HTTPException(status_code=404, detail="Course not found")

    if current_user["role"] not in ["admin", "owner"] and str(current_user["_id"]) != str(course["owner_id"]):
        raise HTTPException(status_code=403, detail="You do not have permission to archive this material")

    # Mark the material as archived by removing it or setting an archived flag
    result = await db["materials"].delete_one({"_id": ObjectId(material_id)})

    # If the material was not found or deleted, raise an error
    if result.deleted_count == 0:
        raise HTTPException(status_code=404, detail="Material not found")

    return {"detail": "Material archived successfully"}
