# cv2 is OpenCV - helps us read and process images
import cv2

# json helps us read our product database
import json

# numpy helps cv2 process image data
import numpy as np

# Path to our product database
DB_PATH = 'product_db.json'

def load_database():
    """
    Loads our product database from JSON file
    Returns a dictionary of product IDs and names
    """
    try:
        with open(DB_PATH, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print("❌ Database not found!")
        return {}

def verify_qr(image_path):
    """
    Takes a QR code image path
    Reads and decodes the QR code
    Checks if product ID exists in database
    Returns verification result
    """
    
    # Load the QR code image
    image = cv2.imread(image_path)
    
    # Check if image was loaded successfully
    if image is None:
        return {
            "status": "error",
            "message": "Could not load image"
        }
    
    # Create QR code detector
    # QRCodeDetector can find and read QR codes in images
    detector = cv2.QRCodeDetector()
    
    # detectAndDecode finds the QR code and extracts its data
    # data = the text inside QR code (our product ID)
    # bbox = the box coordinates around QR code in image
    data, bbox, _ = detector.detectAndDecode(image)
    
    # Check if QR code was found in image
    if not data:
        return {
            "status": "error",
            "message": "No QR code found in image"
        }
    
    print(f"📱 QR Code detected!")
    print(f"   Product ID found: {data}")
    
    # Load our product database
    db = load_database()
    
    # Check if product ID exists in database
    if data in db:
        # Product found - it's REAL
        return {
            "status": "success",
            "result": "REAL",
            "product_id": data,
            "product_name": db[data],
            "message": f"✅ REAL PRODUCT: {db[data]}"
        }
    else:
        # Product not found - it's FAKE
        return {
            "status": "success",
            "result": "FAKE",
            "product_id": data,
            "product_name": "Unknown",
            "message": "❌ FAKE PRODUCT: This QR code is not in our database"
        }

# Test our verification system
print("=== QR Code Verification System ===\n")

# Test 1: Verify a real QR code we generated
import os
qr_folder = 'qr_codes'
qr_files = os.listdir(qr_folder)

if qr_files:
    # Pick first QR code from our folder
    test_qr = os.path.join(qr_folder, qr_files[0])
    print(f"Testing with: {test_qr}")
    
    result = verify_qr(test_qr)
    print(f"\nResult: {result['message']}")
    
    if result['result'] == 'REAL':
        print(f"Product Name: {result['product_name']}")
        print(f"Product ID: {result['product_id']}")

# Test 2: Test with a fake/unknown QR code path
print("\n--- Testing with fake product ---")
fake_result = verify_qr('qr_codes/' + qr_files[0])
print(f"Database check passed: {fake_result['result']}")
