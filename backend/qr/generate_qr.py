# qrcode library helps us create QR code images
import qrcode

# json helps us read and write our product database file
import json

# os helps us work with folders and file paths
import os

# uuid generates a unique ID for each product
# uuid = Universally Unique Identifier
# Example: "a1b2c3d4-e5f6-7890-abcd-ef1234567890"
import uuid

# Path where we'll save QR code images
QR_FOLDER = 'qr_codes'

# Path to our product database
DB_PATH = 'product_db.json'

# Create qr_codes folder if it doesn't exist
os.makedirs(QR_FOLDER, exist_ok=True)

# Create empty database if it doesn't exist
if not os.path.exists(DB_PATH):
    with open(DB_PATH, 'w') as f:
        json.dump({}, f)

def generate_qr(product_name):
    """
    Takes a product name
    Creates a unique ID for it
    Generates a QR code image
    Saves product to database
    """
    
    # Generate a unique product ID
    # str(uuid.uuid4()) gives something like "a1b2c3d4-e5f6..."
    # [:8] takes only first 8 characters to keep it short
    product_id = "PRD-" + str(uuid.uuid4())[:8].upper()
    
    # Load existing database
    with open(DB_PATH, 'r') as f:
        db = json.load(f)
    
    # Add new product to database
    db[product_id] = product_name
    
    # Save updated database
    with open(DB_PATH, 'w') as f:
        json.dump(db, f, indent=4)
    
    # Create QR code
    # The QR code will contain the product_id
    qr = qrcode.QRCode(
        # version controls size of QR code (1=smallest)
        version=1,
        # error_correction allows QR to be read even if slightly damaged
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        # box_size = size of each small square in QR code
        box_size=10,
        # border = white space around QR code
        border=4
    )
    
    # Add our product ID as the data inside QR code
    qr.add_data(product_id)
    qr.make(fit=True)
    
    # Create the QR code image
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Save QR code image
    img_path = os.path.join(QR_FOLDER, f"{product_id}.png")
    img.save(img_path)
    
    print(f"✅ QR Code generated for: {product_name}")
    print(f"   Product ID: {product_id}")
    print(f"   Saved at: {img_path}")
    
    return product_id

# Generate QR codes for some sample products
print("=== Generating QR Codes for Sample Products ===\n")

products = [
    "Apple iPhone 15",
    "Samsung Galaxy S24",
    "Sony Headphones WH-1000XM5",
    "Nike Air Max 270",
    "Adidas Ultraboost 22"
]

for product in products:
    generate_qr(product)

print("\n✅ All QR codes generated!")
print(f"✅ Product database saved to {DB_PATH}")