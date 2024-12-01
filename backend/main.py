from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from motor.motor_asyncio import AsyncIOMotorClient
from routers import auth, users, courses
from config import settings
from fastapi.staticfiles import StaticFiles
from contextlib import asynccontextmanager

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup logic
    app.mongodb_client = AsyncIOMotorClient(settings.MONGODB_URL)
    app.mongodb = app.mongodb_client[settings.DB_NAME]
    yield  # Wait for shutdown
    # Shutdown logic
    app.mongodb_client.close()

app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # React app's default port
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Assuming your images are stored in the "profile_pictures" folder
app.mount("/profile_pictures", StaticFiles(directory="profile_pictures"), name="profile_pictures")

app.include_router(auth.router, prefix="/api", tags=["auth"])
app.include_router(users.router, prefix="/api", tags=["users"])
app.include_router(courses.router, prefix="/api", tags=["courses"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
