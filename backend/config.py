from pydantic_settings import BaseSettings
import secrets
from dotenv import load_dotenv
from typing import ClassVar, Dict


# Load environment variables from .env
load_dotenv()

class Settings(BaseSettings):

    SECRET_KEY: str = secrets.token_urlsafe(32)
    MONGODB_URL: str = f"mongodb+srv://chiranjung321:Chetan2053@cluster0.2zyaflh.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    DB_NAME: str = "lms"
    ALGORITHM: str = "HS256"
    

    # Token Expiry Settings
    ACCESS_TOKEN_EXPIRY: int = 3600  # Default to 1 hour (in seconds)
    REFRESH_TOKEN_EXPIRY: int = 86400  # Default to 24 hours (in seconds)
    
    # Authentication and Authorization Error Codes
    AUTH_ERRORS: ClassVar[Dict[str, str]] = {
        "AUTH_401_UNAUTHORIZED": "Invalid credentials.",
        "AUTH_401_TOKEN_EXPIRED": "Access token has expired. Please refresh or re-login.",
        "AUTH_401_INVALID_TOKEN": "Invalid refresh token.",
        "AUTH_401_REFRESH_EXPIRED": "Refresh token expired. Re-login required.",
        "AUTH_403_FORBIDDEN": "You do not have permission to perform this action.",
        "AUTH_403_ROLE_INVALID": "Action restricted to specific roles.",
        "AUTH_403_INACTIVE_ACCOUNT": "Your account is inactive or suspended.",
        "AUTH_403_ACCOUNT_LOCKED": "Account locked due to repeated login failures.",
    }

    # Resource Access Error Codes
    ACCESS_ERRORS: ClassVar[Dict[str, str]] = {
        "ACCESS_404_NOT_FOUND": "The requested resource was not found.",
        "ACCESS_403_INVALID_PRIVILEGE": "Insufficient privileges to access this resource.",
        "ACCESS_401_INVALID_TOKEN": "The provided token is invalid or malformed.",
        "ACCESS_409_RESOURCE_CONFLICT": "Resource conflict. Possibly duplicate data.",
    }

    # User Management Error Codes
    USER_ERRORS: ClassVar[Dict[str, str]] = {
        "USER_400_INVALID_DATA": "Invalid data provided for user operations.",
        "USER_404_NOT_FOUND": "User not found.",
        "USER_409_DUPLICATE": "User already exists with this identifier.",
        "USER_403_SELF_MODIFICATION": "Self-modification of permissions is not allowed.",
        "USER_401_SESSION_INVALID": "Session is invalid or has expired.",
    }

    # Course Management Error Codes (LMS-Specific)
    COURSE_ERRORS: ClassVar[Dict[str, str]] = {
        "COURSE_404_NOT_FOUND": "Course not found.",
        "COURSE_403_ACCESS_DENIED": "You are not enrolled in this course.",
        "COURSE_409_DUPLICATE": "A course with similar details already exists.",
        "COURSE_400_INVALID_INPUT": "Invalid course data provided.",
    }

    # API Error Codes
    API_ERRORS: ClassVar[Dict[str, str]] = {
        "API_400_BAD_REQUEST": "Invalid API request.",
        "API_401_UNAUTHORIZED": "Authentication is required for this API call.",
        "API_403_FORBIDDEN": "You are not authorized to access this API.",
        "API_404_NOT_FOUND": "API endpoint not found.",
        "API_429_TOO_MANY_REQUESTS": "Rate limit exceeded. Try again later.",
        "API_500_INTERNAL_SERVER_ERROR": "Unexpected server error.",
    }

    # File Upload and Management Error Codes
    FILE_ERRORS: ClassVar[Dict[str, str]] = {
        "FILE_400_INVALID_FORMAT": "Unsupported file format.",
        "FILE_413_PAYLOAD_TOO_LARGE": "File size exceeds the allowed limit.",
        "FILE_404_NOT_FOUND": "File not found.",
        "FILE_403_ACCESS_DENIED": "You do not have permission to access this file.",
    }

    # General Error Codes
    GENERAL_ERRORS: ClassVar[Dict[str, str]] = {
        "GEN_400_BAD_INPUT": "Invalid or malformed input provided.",
        "GEN_500_UNKNOWN_ERROR": "An unexpected error occurred.",
        "GEN_504_GATEWAY_TIMEOUT": "Request timed out.",
        "GEN_503_SERVICE_UNAVAILABLE": "The service is temporarily unavailable.",
    }

    # RBAC Debugging Error Codes
    RBAC_ERRORS: ClassVar[Dict[str, str]] = {
        "RBAC_403_ROLE_MISMATCH": "Your role does not match the required permissions.",
        "RBAC_403_INVALID_ACTION": "This action is not allowed for your role.",
        "RBAC_403_PERMISSION_MISSING": "You are missing the required permission.",
    }

    class Config:
        env_file = ".env"

# Access settings via the `Settings` class
settings = Settings()
