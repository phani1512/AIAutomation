"""
Direct OCR test - bypass all the complex logic and just run OCR on a screenshot
"""
import cv2
import numpy as np
from PIL import Image
import pytesseract
import sys

# Configure Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load your Sircon screenshot
print("Please provide the path to your screenshot:")
print("Example: C:\\Users\\valaboph\\Downloads\\sircon.png")
img_path = input("Path: ").strip().strip('"')

try:
    # Load image
    img = cv2.imread(img_path)
    if img is None:
        print(f"ERROR: Could not load image from {img_path}")
        sys.exit(1)
    
    print(f"\n✓ Image loaded: {img.shape}")
    
    # Convert to grayscale
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    
    # Run OCR
    print("\n========== RUNNING PYTESSERACT ==========")
    data = pytesseract.image_to_data(gray, output_type=pytesseract.Output.DICT)
    
    # Show all detected text
    print(f"\nTotal words detected: {len(data['text'])}")
    print("\n========== EXTRACTED TEXT ==========")
    
    for i in range(len(data['text'])):
        text = data['text'][i].strip()
        conf = int(data['conf'][i]) if data['conf'][i] != '-1' else 0
        
        if text and conf > 30:  # Only show text with >30% confidence
            x = data['left'][i]
            y = data['top'][i]
            w = data['width'][i]
            h = data['height'][i]
            print(f"  '{text}' @ ({x},{y}) size={w}x{h} conf={conf}%")
    
    print("\n========== DONE ==========")
    print("\nIf you see 'First Name', 'Last Name', 'Email Address' above,")
    print("then OCR is working correctly and the problem is in the label matching.")
    print("\nIf you DON'T see those labels, then OCR preprocessing is the issue.")

except Exception as e:
    print(f"\nERROR: {e}")
    import traceback
    traceback.print_exc()
