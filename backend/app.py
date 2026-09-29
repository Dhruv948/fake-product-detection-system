# FastAPI is our web framework
from fastapi import FastAPI, File, UploadFile, HTTPException

# BaseModel helps us define what data we expect from frontend
from pydantic import BaseModel

# CORSMiddleware allows our frontend to talk to our API
from fastapi.middleware.cors import CORSMiddleware

# StaticFiles lets us serve QR code images directly
from fastapi.staticfiles import StaticFiles

import pickle
import numpy as np
import os
import json
import cv2
import re
import qrcode
import uuid

# Initialize FastAPI app
app = FastAPI(
    title="Fake Product Detection API",
    description="Detects fake products using ML and QR verification",
    version="1.0.0"
)

# Enable CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"]
)

# ═══════════════════════════════════
# Load ML Model and TF-IDF
# ═══════════════════════════════════
model = pickle.load(open('model/model.pkl', 'rb'))
tfidf = pickle.load(open('model/tfidf.pkl', 'rb'))
print("✅ ML Model loaded successfully")

# ═══════════════════════════════════
# Load Product Database
# ═══════════════════════════════════
DB_PATH = 'qr/product_db.json'

def load_database():
    with open(DB_PATH, 'r') as f:
        return json.load(f)

def save_database(db):
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)

print("✅ Product database loaded successfully")

# ═══════════════════════════════════
# Text Cleaning Function
# ═══════════════════════════════════
def clean_text(text):
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = text.strip()
    return text

# ═══════════════════════════════════
# Define Request Models
# BaseModel = defines what data frontend must send
# ═══════════════════════════════════
class ReviewRequest(BaseModel):
    review: str

class ProductRequest(BaseModel):
    product_name: str

# ═══════════════════════════════════
# ROUTE 1: Home Route
# ═══════════════════════════════════
@app.get("/")
def home():
    return {
        "message": "Fake Product Detection API is running!",
        "docs": "Visit http://localhost:8000/docs to test all routes"
    }

# ═══════════════════════════════════
# ROUTE 2: Analyze Review
# ═══════════════════════════════════
@app.post("/analyze-review")
def analyze_review(request: ReviewRequest):
    try:
        review = request.review

        # Check if review is empty
        if not review:
            raise HTTPException(
                status_code=400,
                detail="No review text provided"
            )

        # Clean the review
        cleaned = clean_text(review)

        # Convert to numbers using TF-IDF
        review_tfidf = tfidf.transform([cleaned])

        # Predict fake or real
        prediction = model.predict(review_tfidf)[0]

        # Get confidence score
        proba = model.predict_proba(review_tfidf)[0]
        confidence = round(max(proba) * 100, 2)

        result = "FAKE" if prediction == 1 else "REAL"

        return {
            "status": "success",
            "result": result,
            "confidence": f"{confidence}%",
            "message": f"This review appears to be {result}",
            "review": review
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════
# ROUTE 3: Verify QR Code
# ═══════════════════════════════════
@app.post("/verify-qr")
async def verify_qr(qr_image: UploadFile = File(...)):
    try:
        # Read uploaded image
        # UploadFile = file sent from frontend
        contents = await qr_image.read()

        # Convert to numpy array so cv2 can process it
        img_array = np.frombuffer(contents, np.uint8)
        image = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

        if image is None:
            raise HTTPException(
                status_code=400,
                detail="Could not read image"
            )

        # Detect and decode QR code
        detector = cv2.QRCodeDetector()
        data, bbox, _ = detector.detectAndDecode(image)

        if not data:
            raise HTTPException(
                status_code=400,
                detail="No QR code found in image"
            )

        # Check database
        db = load_database()

        if data in db:
            return {
                "status": "success",
                "result": "REAL",
                "product_id": data,
                "product_name": db[data],
                "message": f"REAL PRODUCT: {db[data]}"
            }
        else:
            return {
                "status": "success",
                "result": "FAKE",
                "product_id": data,
                "product_name": "Unknown",
                "message": "FAKE PRODUCT: QR code not found in database"
            }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ═══════════════════════════════════
# ROUTE 4: Generate QR Code
# ═══════════════════════════════════
@app.post("/generate-qr")
def generate_qr_route(request: ProductRequest):
    try:
        product_name = request.product_name

        if not product_name:
            raise HTTPException(
                status_code=400,
                detail="No product name provided"
            )

        # Generate unique product ID
        product_id = "PRD-" + str(uuid.uuid4())[:8].upper()

        # Save to database
        db = load_database()
        db[product_id] = product_name
        save_database(db)

        # Generate QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4
        )
        qr.add_data(product_id)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")

        # Save QR image
        qr_path = f'qr/qr_codes/{product_id}.png'
        img.save(qr_path)

        return {
            "status": "success",
            "product_id": product_id,
            "product_name": product_name,
            "message": f"QR code generated for {product_name}",
            "qr_path": qr_path
        }

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))