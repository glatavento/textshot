import pytesseract
from PIL import Image


def getOcrVersion():
    return pytesseract.get_tesseract_version()


def processImage(image: Image, lang):
    result = pytesseract.image_to_string(image, timeout=5, lang=lang).strip()
    return result
