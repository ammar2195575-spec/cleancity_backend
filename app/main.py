from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
from .database import engine, Base
from .routers import auth, complaints

# Database tables banao
Base.metadata.create_all(bind=engine)

# FastAPI app
app = FastAPI(
    title="CleanCity API",
    description="Garbage Detection and Complaint Management System",
    version="1.0.0"
)

# CORS middleware — Flutter se connect hone ke liye
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Uploads folder serve karo
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Routers include karo
app.include_router(auth.router)
app.include_router(complaints.router)

# Root endpoint
@app.get("/")
def root():
    return {
        "message": "CleanCity API is running!",
        "version": "1.0.0",
        "docs": "/docs"
    }

# Health check
@app.get("/health")
def health_check():
    return {"status": "healthy"}