import os
from PIL import Image
import pytesseract

common_paths = [
    r"C:\Program Files\Tesseract-OCR\tesseract.exe",
    r"C:\Program Files (x86)\Tesseract-OCR\tesseract.exe",
    r"C:\Users\deepa\AppData\Local\Programs\Tesseract-OCR\tesseract.exe"
]
for p in common_paths:
    if os.path.exists(p):
        pytesseract.pytesseract.tesseract_cmd = p
        break


def extract_text(image_path):
    if not os.path.exists(image_path):
        return ""
    try:
        image = Image.open(image_path)
        return pytesseract.image_to_string(image).strip()
    except Exception as e:
        print("OCR error:", e)
        return ""
