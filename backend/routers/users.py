from fastapi import APIRouter, Depends, HTTPException
from models.user import UserOut, UserProfileOut, UserInDB
from .auth import get_current_user, get_db, toggle_user_status, reset_pass
from typing import Optional
from fastapi import UploadFile, File
from pathlib import Path
from bson import ObjectId
import os

router = APIRouter()

async def save_file(upload_file: UploadFile, user_id: str) -> str:
    """Helper function to save uploaded profile picture to a directory."""
    upload_dir = Path(f"profile_pictures/{user_id}")
    upload_dir.mkdir(parents=True, exist_ok=True)  # Create directory if it doesn't exist

    file_location = upload_dir / upload_file.filename
    with open(file_location, "wb") as f:
        f.write(await upload_file.read())

    return str(file_location)

@router.get("/users/{user_id}/profile", response_model=UserProfileOut)
async def get_user_profile(user_id: str, current_user: UserInDB = Depends(get_current_user), db = Depends(get_db)):
    """Endpoint to retrieve a user's profile data."""

    # Convert user_id to ObjectId for MongoDB querying
    target_user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not target_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is authorized to view this profile
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to access this profile")

    # Create the response model
    if target_user.get("profile_picture"):
        profile_picture_path = os.getenv("BASE_URL") + target_user.get("profile_picture")
    else:
        profile_picture_path = "None"
    return UserProfileOut(
        id=str(target_user["_id"]),
        username=target_user["username"],
        email=target_user.get("email"),
        first_name=target_user.get("first_name"),
        last_name=target_user.get("last_name"),
        role=target_user.get("role", "student"),
        is_active=target_user.get("is_active"),
        profile_picture=profile_picture_path
    )


@router.put("/users/{user_id}/profile", response_model=UserProfileOut)
async def update_user_profile(
    user_id: str,
    profile_picture: Optional[UploadFile] = File(None),
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_db)
):
    """Endpoint to update a user's profile data, including profile picture."""
    
    # Check if the current user is authorized to update this profile
    if str(current_user.id) != user_id:
        raise HTTPException(status_code=403, detail="Not authorized to update this profile")
    
    # Find the user in the database
    user_data = await db["users"].find_one({"_id": ObjectId(user_id)})
    
    if not user_data:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Process and save the profile picture if provided
    updated_fields = {}
    if profile_picture:
        file_location = await save_file(profile_picture, user_id)
        updated_fields["profile_picture"] = file_location  # Save the file location
    
    # Example of updating other fields (like first_name and last_name)
    if 'first_name' in user_data:
        updated_fields['first_name'] = user_data['first_name']
    if 'last_name' in user_data:
        updated_fields['last_name'] = user_data['last_name']
    
    # Update user information in the database
    if updated_fields:
        await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": updated_fields})
    
    # Return updated user information
    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    
    return UserProfileOut(
        id=str(updated_user["_id"]),
        username=updated_user["username"],
        email=updated_user.get("email"),
        first_name=updated_user.get("first_name"),
        last_name=updated_user.get("last_name"),
        role=updated_user.get("role", "role"),
        is_active=updated_user.get("is_active"),
        profile_picture=updated_user.get("profile_picture")
    )


    

@router.get("/users", response_model=list[UserOut])
async def get_users(
    search: Optional[str] = None,  # Accept search query
    current_user: dict = Depends(get_current_user),
    db = Depends(get_db)
):
    # Ensure the current user is an admin or teacher
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Build the query for search
    query = {}

    # Apply search filter if it's not empty
    if search and search.strip():
        query["username"] = {"$regex": search, "$options": "i"}  # Case-insensitive search using regex

    # If the current user is a teacher, restrict query to only fetch students
    if current_user.role == "teacher":
        query["role"] = "student"

    # Fetch users from the database (limit 1000 for now)
    users = await db["users"].find(query).to_list(1000)

    # Return a list of users, mapped to the UserOut schema
    return [
        UserOut(
            id=str(user["_id"]),  # Ensure ObjectId is converted to string
            username=user.get("username", "Unknown"),  # Use fallback in case username is missing
            email=user.get("email"),
            first_name=user.get("first_name"),
            last_name=user.get("last_name"),
            role=user.get("role", "student"),  # Default role to "student" if missing
            is_active=user.get("is_active", True)  # Default is_active to True if missing
        )
        for user in users
    ]



@router.get("/users/me", response_model=UserOut)
async def read_users_me(current_user: UserOut = Depends(get_current_user)):
    return current_user

@router.post("/logout")
async def logout():
    # Simply return a message that logout was successful
    return {"detail": "Logout successful"}

@router.post("/users/{user_id}/disable", status_code=200)
async def disable_user(user_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Endpoint to disable a user (accessible to admins and teachers for students)."""
    
    # Fetch the user from the database
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is an admin
    if current_user.role == "admin":
        # Admins can disable any user
        pass
    elif current_user.role == "teacher":
        # Teachers can only disable students
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Teachers can only disable students")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Call the helper function to toggle the user's status
    return await toggle_user_status(user_id, db)


    
    
@router.post("/users/{user_id}/reset-password", status_code=200)
async def reset_password(user_id: str, current_user: dict = Depends(get_current_user), db=Depends(get_db)):
    """Endpoint to reset a user's password (only accessible to admins or teachers for students)."""
    
    # Fetch the user from the database
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is an admin
    if current_user.role == "admin":
        # Admins can reset passwords for any user
        pass
    elif current_user.role == "teacher":
        # Teachers can only reset passwords for students
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Teachers can only reset passwords for students")
    else:
        raise HTTPException(status_code=403, detail="Not authorized")

    # Call the helper function to reset the user's password
    return await reset_pass(user_id, db, current_user)




