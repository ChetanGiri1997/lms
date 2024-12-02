from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from routers import auth, users, courses, assignment, materials, email_router, notifications
from config import settings

# Database connection handling
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    try:
        await app.mongodb.list_collection_names()
        print("Connected to MongoDB successfully")
    except Exception as e:
        print(f"Failed to connect to MongoDB: {e}")
        raise e
    yield
    app.mongodb_client.close()

# Initialize FastAPI app
app = FastAPI(lifespan=lifespan)

# CORS middleware setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Exact frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware to log requests for debugging
@app.middleware("http")
async def log_request(request: Request, call_next):
    print(f"Request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# Static files
app.mount("/profile_pictures", StaticFiles(directory="profile_pictures"), name="profile_pictures")
app.mount("/materials", StaticFiles(directory="materials"), name="study_materials")


# Include routers
app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(courses.router, prefix="/api", tags=["courses"])
app.include_router(assignment.router, prefix="/api", tags=["assignments"])
app.include_router(materials.router, prefix="/api", tags=["materials"])
app.include_router(email_router.router, prefix="/api", tags=["email"])
app.include_router(notifications.router, prefix="/api", tags=["notifications"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
