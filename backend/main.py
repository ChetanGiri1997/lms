from fastapi import FastAPI, APIRouter, Depends
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers import auth, users, courses
from config import settings
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

# Database connection handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    try:
        # Check MongoDB connection
        await app.mongodb.list_collection_names()
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e  # Ensure the app doesn't start if the connection fails
    yield  # Wait for shutdown
    # Shutdown logic
    app.mongodb_client.close()

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://potential-chainsaw-pjgwpr7qxgqx26657-5173.app.github.dev"],  # Replace with the React app URL for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files (e.g., profile pictures)
app.mount("/profile_pictures", StaticFiles(directory="profile_pictures"), name="profile_pictures")


# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(courses.router, prefix="/api", tags=["courses"])



if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
