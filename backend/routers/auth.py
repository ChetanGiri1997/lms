from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from models.user import UserRegister, UserInDB, Token, TokenData, UserLogin, UserUpdate, UserOut
from typing import Optional
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from bson import ObjectId
from dotenv import load_dotenv
import os
from config import settings

# Load environment variables from .env
load_dotenv()

router = APIRouter()

# Password hashing configuration
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


# Dependency: Get DB connection
async def get_db() -> AsyncIOMotorDatabase:
    client = AsyncIOMotorClient(os.getenv("MONGODB_URL"))
    return client[os.getenv("DB_NAME")]


# Utility functions
def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def hash_password(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta if expires_delta else timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)



async def get_user(db: AsyncIOMotorDatabase, identifier: str) -> Optional[UserInDB]:
    user = await db["users"].find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    if user:
        user["id"] = str(user.pop("_id"))  # Convert MongoDB _id to id
        user["password"] = user.pop("hashed_password", user.get("password"))  # Use 'hashed_password' if it exists
        user["first_name"] = user.get("first_name")  # Ensure to include first_name
        user["last_name"] = user.get("last_name")    # Ensure to include last_name
        return UserInDB(**user)  # Convert dict to UserInDB model
    return None



async def authenticate_user(db: AsyncIOMotorDatabase, identifier: str, password: str) -> Optional[UserInDB]:
    # Query the database to find the user by username or email
    user = await db["users"].find_one({"$or": [{"username": identifier}, {"email": identifier}]})
    
    # If user is found, verify the password
    if user and verify_password(password, user.get("password")):
        # Check if the user is active
        if not user.get("is_active", False):
            return None  # User is inactive, return None
        
        # Convert MongoDB _id to a string id
        user["id"] = str(user.pop("_id"))
        
        # Return the user as a UserInDB object (assuming you have this model)
        return UserInDB(**user)
    
    return None  # Return None if authentication fails


# Check if user has a specific role
async def has_role(user: UserInDB, required_role: str) -> bool:
    return user.role == required_role


# Token validation and extraction of user from token
async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncIOMotorDatabase = Depends(get_db),
) -> UserInDB:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={
            "error_code": "AUTH_401_UNAUTHORIZED",
            "message": settings.AUTH_ERRORS["AUTH_401_UNAUTHORIZED"],
        },
    )
    
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        identifier: str = payload.get("sub")
        role: str = payload.get("role")
        if identifier is None or role is None:
            raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={
                "error_code": "AUTH_401_TOKEN_EXPIRED",
                "message": settings.AUTH_ERRORS["AUTH_401_TOKEN_EXPIRED"],
            },
        )
    except JWTError:
        raise credentials_exception

    user = await get_user(db, identifier)
    if not user:
        raise credentials_exception

    return user



@router.post("/login", response_model=Token)
async def login_for_access_token(login_request: UserLogin, db=Depends(get_db)):
    user = await authenticate_user(db, login_request.identifier, login_request.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username, email, or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Generate access and refresh tokens
    access_token_expires = timedelta(minutes=int(os.getenv("ACCESS_TOKEN_EXPIRY")))
    refresh_token_expires = timedelta(days=int(os.getenv("REFRESH_TOKEN_EXPIRY")))
    access_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=access_token_expires
    )
    refresh_token = create_access_token(
        data={"sub": user.username, "role": user.role}, expires_delta=refresh_token_expires
    )

    # Optionally store the refresh token in the database
    await db["refresh_tokens"].insert_one({
        "user_id": user.id,
        "token": refresh_token,
        "expires_at": datetime.utcnow() + refresh_token_expires,
    })

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer",
        "role": user.role,
        "id": str(user.id),
    }


@router.post("/refresh", response_model=Token)
async def refresh_access_token(refresh_token: str, db=Depends(get_db)):
    try:
        payload = jwt.decode(refresh_token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        identifier: str = payload.get("sub")
        role: str = payload.get("role")
        if identifier is None or role is None:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail={"error_code":"AUTH_401_INVALID_TOKEN", "message": settings.AUTH_ERRORS["AUTH_401_INVALID_TOKEN"]},
            )
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_401_REFRESH_EXPIRED", "message": settings.AUTH_ERRORS["AUTH_401_REFRESH_EXPIRED"]},
        )
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code": "AUTH_401_INVALID_TOKEN", "message":settings.AUTH_ERRORS["AUTH_401_INVALID_TOKEN"] },
        )

    # Check the refresh token against the database
    token_record = await db["refresh_tokens"].find_one({"token": refresh_token})
    if not token_record or token_record["expires_at"] < datetime.utcnow():
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail={"error_code" : "AUTH_401_INVALID_TOKEN", "message":settings.AUTH_ERRORS["AUTH_401_INVALID_TOKEN"] },
        )

    # Generate new access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    new_access_token = create_access_token(
        data={"sub": identifier, "role": role}, expires_delta=access_token_expires
    )

    return {
        "access_token": new_access_token,
        "token_type": "bearer",
        "role": role,
    }



@router.post("/register", response_model=Token)
async def register_user(
    user: UserRegister,
    db=Depends(get_db),
    current_user=Depends(get_current_user)
):
    # Check if current user is admin or teacher
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You do not have permission to create users."
        )

    user_data = user.dict()  # Initialize user_data from user
    # Set default role for teachers
    if current_user.role == "teacher":
        user_data["role"] = "student"  # Default to student role

    # Check for existing username or email
    existing_user = await get_user(db, user.username) or await get_user(db, user.email)
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already registered")

    # Hash the password and prepare user data for insertion
    hashed_password = hash_password(user.password)
    user_data["password"] = hashed_password  # Save hashed password
    user_data["created_at"] = datetime.utcnow()  # Set created timestamp
    user_data["is_active"] = True  # Default to active
    

    # Insert user into the database
    result = await db["users"].insert_one(user_data)

    # Create access token
    access_token = create_access_token(
        data={"sub": user.username, "role": user_data.get("role", "student")}
    )

    return {
        "access_token": access_token,
        "token_type": "bearer",
        "role": user_data["role"],
        "id": str(result.inserted_id)  # Use the inserted ID from the result
    }


async def toggle_user_status(user_id: str, db: AsyncIOMotorDatabase, current_user=Depends(get_current_user)):
    """Toggle the user's is_active status: enable if disabled, disable if enabled."""
    
    # Fetch the user from the database by their user_id
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    # If user does not exist, raise a 404 error
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Toggle the is_active status (if True, set to False, and vice versa)
    new_status = not user.get("is_active", False)

    # Update the user's is_active field in the database
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"is_active": new_status}}  # Toggle the is_active field
    )

    # If no document was modified, raise an error
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to update user status")

    # Return a success message with the updated status
    return {"detail": f"User successfully {'enabled' if new_status else 'disabled'}"}


#reset password
async def reset_pass(user_id: str, db: AsyncIOMotorDatabase, current_user=Depends(get_current_user)):
    """Reset a user's password."""
    user = await db["users"].find_one({"_id": ObjectId(user_id)})

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # Check if the current user is an admin or if they are a teacher trying to reset a student's password
    if current_user.role == 'admin':
        # Admins can reset passwords for any user
        pass
    elif current_user.role == 'teacher':
        # Teachers can only reset passwords for students
        if user.get("role") != "student":
            raise HTTPException(status_code=403, detail="Teachers can only reset passwords for students")
    else:
        raise HTTPException(status_code=403, detail="You do not have permission to reset passwords")

    # Generate a new random password    
    new_password = "admin"  # Consider generating a more secure random password
    hashed_password = hash_password(new_password)

    # Update the user's password in the database
    result = await db["users"].update_one(
        {"_id": ObjectId(user_id)},
        {"$set": {"password": hashed_password}}
    )

    # If no document was modified, raise an error
    if result.modified_count == 0:
        raise HTTPException(status_code=400, detail="Failed to reset password")

    # Return a success message
    return {"detail": "Password successfully reset"}


#Check user status
def check_user_status(user: UserInDB):
    if not user.is_active:
        raise HTTPException(status_code=400, detail="User is not active")



# @router.post("/register", response_model=Token)
# async def register_user(
#     user: UserRegister,
#     db=Depends(get_db)
# ):
#     # Check for existing username or email
#     existing_user = await get_user(db, user.username) or await get_user(db, user.email)
#     if existing_user:
#         raise HTTPException(status_code=400, detail="Username or email already registered")

#     # Hash the password and prepare user data for insertion
#     user_data = user.dict()  # Convert user input to dictionary
#     hashed_password = hash_password(user.password)
#     user_data["password"] = hashed_password  # Save hashed password
#     user_data["created_at"] = datetime.utcnow()  # Set created timestamp
#     user_data["is_active"] = True  # Default to active
#     user_data["role"] = "student"  # Default role for public registration

#     # Insert user into the database
#     result = await db["users"].insert_one(user_data)

#     # Create access token
#     access_token = create_access_token(
#         data={"sub": user.username, "role": user_data["role"]}
#     )

#     return {
#         "access_token": access_token,
#         "token_type": "bearer",
#         "role": user_data["role"],
#         "id": str(result.inserted_id)  # Use the inserted ID from the result
#     }


@router.put("/edit_users/{user_id}", response_model=UserOut)
async def update_user(
    user_id: str,
    user_update: UserUpdate,
    current_user: UserInDB = Depends(get_current_user),
    db = Depends(get_db)
):
    # Allow both admins and teachers
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to edit users")

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    update_data = user_update.dict(exclude_unset=True)

    # If current user is a teacher, remove the role from the update data
    if current_user.role == "teacher" and "role" in update_data:
        del update_data["role"]

    # Hash the password if it's being updated
    if "password" in update_data:
        update_data["password"] = hash_password(update_data["password"])

    await db["users"].update_one({"_id": ObjectId(user_id)}, {"$set": update_data})

    updated_user = await db["users"].find_one({"_id": ObjectId(user_id)})
    updated_user["id"] = str(updated_user.pop("_id"))  # Map MongoDB _id to id
    return UserOut(**updated_user)


@router.get("/edit_users/{user_id}", response_model=UserOut)
async def get_user_to_edit(
    user_id: str, 
    current_user: UserInDB = Depends(get_current_user), 
    db=Depends(get_db)
):
    # Allow only admins and teachers
    if current_user.role not in ["admin", "teacher"]:
        raise HTTPException(status_code=403, detail="Not authorized to view users")

    user = await db["users"].find_one({"_id": ObjectId(user_id)})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    # If current user is a teacher, only allow them to edit students
    if current_user.role == "teacher" and user.get("role") != "student":
        raise HTTPException(status_code=403, detail="Not authorized to edit this user")

    user["id"] = str(user.pop("_id"))  # Map MongoDB _id to id
    return UserOut(**user)

