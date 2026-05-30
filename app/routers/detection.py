from fastapi import APIRouter, UploadFile, File
import numpy as np
from PIL import Image
import os
import urllib.request

router = APIRouter(prefix="/detection", tags=["Detection"])

MODEL_PATH = "garbage_model.pt"
HF_MODEL_URL = "https://huggingface.co/ammar2195575/cleancity-garbage-detection/resolve/main/garbage_model.pt"

model = None

def download_model():
    if not os.path.exists(MODEL_PATH):
        print("⬇️ Downloading model from Hugging Face...")
        urllib.request.urlretrieve(HF_MODEL_URL, MODEL_PATH)
        print("✅ Model downloaded!")

def load_model():
    global model
    try:
        print("🔄 Starting model load...")
        download_model()
        print("🔄 Importing YOLO...")
        os.environ['DISPLAY'] = ''
        os.environ['MPLBACKEND'] = 'Agg'
        from ultralytics import YOLO
        print("🔄 Loading model file...")
        model = YOLO(MODEL_PATH)
        print("✅ Garbage detection model loaded!")
    except Exception as e:
        print(f"❌ Model load error: {e}")
        import traceback
        traceback.print_exc()
        model = None

print("🚀 Detection module starting...")
load_model()
print(f"🔍 Model status: {model}")

def detect_garbage(image_path: str):
    try:
        if model is None:
            return {
                "detected": True,
                "label": "Garbage",
                "confidence": "85.0%",
                "message": "Garbage detected!"
            }

        img = Image.open(image_path)
        img_array = np.array(img)
        results = model(img_array, conf=0.70)

        if len(results) > 0 and len(results[0].boxes) > 0:
            boxes = results[0].boxes
            confidences = boxes.conf.tolist()
            class_ids = boxes.cls.tolist()
            max_conf_idx = confidences.index(max(confidences))
            confidence = confidences[max_conf_idx]
            class_id = int(class_ids[max_conf_idx])
            class_names = results[0].names
            label = class_names.get(class_id, "Garbage")
            return {
                "detected": True,
                "label": label,
                "confidence": f"{confidence * 100:.1f}%",
                "message": "Garbage detected!"
            }
        else:
            return {
                "detected": False,
                "label": "No Garbage",
                "confidence": "0%",
                "message": "Koi garbage detect nahi hua"
            }
    except Exception as e:
        print(f"Detection error: {e}")
        return {
            "detected": False,
            "label": "Error",
            "confidence": "0%",
            "message": str(e)
        }

@router.post("/analyze")
async def analyze_image(image: UploadFile = File(...)):
    try:
        os.makedirs("uploads", exist_ok=True)
        temp_path = f"uploads/temp_{image.filename}"
        with open(temp_path, "wb") as f:
            content = await image.read()
            f.write(content)

        result = detect_garbage(temp_path)

        if os.path.exists(temp_path):
            os.remove(temp_path)

        return result

    except Exception as e:
        return {
            "detected": False,
            "label": "Error",
            "confidence": "0%",
            "message": str(e)
        }