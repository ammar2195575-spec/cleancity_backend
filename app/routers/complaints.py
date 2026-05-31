from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
import shutil
import os
import uuid
from datetime import datetime
from app.database import get_db
from app.models import Complaint
import cloudinary
import cloudinary.uploader

router = APIRouter(prefix="/complaints", tags=["Complaints"])

# Cloudinary config
cloudinary.config(
    cloud_name="dqdf46ldg",
    api_key="318491485831716",
    api_secret="NhHzpH-tcd1oxeTPRfMiolg6EX4"
)

UPLOAD_DIR = "uploads"

@router.post("/submit")
async def submit_complaint(
    user_id: int = Form(...),
    user_name: str = Form(...),
    description: str = Form(...),
    latitude: float = Form(...),
    longitude: float = Form(...),
    address: str = Form(...),
    image: UploadFile = File(...),
    ai_label: str = Form(default="Unknown"),
    ai_confidence: str = Form(default="0%"),
    db: Session = Depends(get_db)
):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = f"{UPLOAD_DIR}/temp_{uuid.uuid4()}.jpg"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Cloudinary pe upload karo
    upload_result = cloudinary.uploader.upload(
        temp_path,
        folder="cleancity/before"
    )
    image_url = upload_result['secure_url']

    # Temp file delete karo
    os.remove(temp_path)

    complaint_id = f"CC-{str(uuid.uuid4())[:6].upper()}"

    new_complaint = Complaint(
        complaint_id=complaint_id,
        user_id=user_id,
        user_name=user_name,
        description=description,
        image_path=image_url,
        latitude=latitude,
        longitude=longitude,
        address=address,
        status="pending",
        ai_label=ai_label,
        ai_confidence=ai_confidence,
    )
    db.add(new_complaint)
    db.commit()
    db.refresh(new_complaint)

    return {
        "message": "Complaint submitted successfully",
        "complaint_id": complaint_id,
        "status": "pending"
    }

@router.get("/all")
def get_all_complaints(db: Session = Depends(get_db)):
    complaints = db.query(Complaint).order_by(
        Complaint.created_at.desc()
    ).all()
    return complaints

@router.get("/user/{user_id}")
def get_user_complaints(user_id: int, db: Session = Depends(get_db)):
    complaints = db.query(Complaint).filter(
        Complaint.user_id == user_id
    ).order_by(Complaint.created_at.desc()).all()
    return complaints

@router.put("/status/{complaint_id}")
def update_status(
    complaint_id: str,
    status: str,
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    complaint.status = status
    complaint.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "Status updated",
        "complaint_id": complaint_id,
        "status": status
    }

@router.get("/{complaint_id}")
def get_complaint(complaint_id: str, db: Session = Depends(get_db)):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    return complaint

@router.post("/after-image/{complaint_id}")
async def upload_after_image(
    complaint_id: str,
    image: UploadFile = File(...),
    db: Session = Depends(get_db)
):
    complaint = db.query(Complaint).filter(
        Complaint.complaint_id == complaint_id
    ).first()

    if not complaint:
        raise HTTPException(status_code=404, detail="Complaint not found")

    os.makedirs(UPLOAD_DIR, exist_ok=True)
    temp_path = f"{UPLOAD_DIR}/temp_after_{uuid.uuid4()}.jpg"

    with open(temp_path, "wb") as buffer:
        shutil.copyfileobj(image.file, buffer)

    # Cloudinary pe upload karo
    upload_result = cloudinary.uploader.upload(
        temp_path,
        folder="cleancity/after"
    )
    after_image_url = upload_result['secure_url']

    # Temp file delete karo
    os.remove(temp_path)

    complaint.after_image_path = after_image_url
    complaint.status = "resolved"
    complaint.updated_at = datetime.utcnow()
    db.commit()

    return {
        "message": "After image uploaded successfully",
        "complaint_id": complaint_id,
        "after_image_path": after_image_url
    }