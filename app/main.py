from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .database import engine, Base
from .routers import auth, complaints, detection

# Database tables banao
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="CleanCity API",
    description="Garbage Detection and Complaint Management System",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads folder
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers
app.include_router(auth.router)
app.include_router(complaints.router)
app.include_router(detection.router)

@app.on_event("startup")
async def startup_event():
    print("🚀 CleanCity API starting...")
    detection.load_model()
    print("✅ Startup complete!")

@app.get("/")
def root():
    return {
        "message": "CleanCity API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}