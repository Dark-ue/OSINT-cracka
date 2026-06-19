import os
import json
import subprocess
from PIL import Image
from pyzbar.pyzbar import decode
import cv2

def extract_exif(image_path):
    """Extracts EXIF data using pyexiftool."""
    try:
        result = subprocess.run(['exiftool', '-json', image_path], capture_output=True, text=True)
        if result.returncode == 0:
            return json.loads(result.stdout)[0]
    except Exception as e:
        return {"error": f"Failed to extract EXIF: {e}"}
    return {}

def extract_gps(exif_data):
    """Extracts GPS coordinates from EXIF data."""
    gps = {}
    if exif_data and isinstance(exif_data, dict):
        lat = exif_data.get('GPSLatitude')
        lon = exif_data.get('GPSLongitude')
        if lat and lon:
            gps['latitude'] = lat
            gps['longitude'] = lon
    return gps

def extract_barcodes(image_path):
    """Extracts barcodes and QR codes from an image."""
    try:
        # Try cv2 first for better handling
        img = cv2.imread(image_path)
        if img is not None:
             decoded_objects = decode(img)
        else:
             # Fallback to PIL
             img = Image.open(image_path)
             decoded_objects = decode(img)
        
        results = []
        for obj in decoded_objects:
            results.append({
                "type": obj.type,
                "data": obj.data.decode("utf-8")
            })
        return results
    except Exception as e:
        return [{"error": f"Barcode extraction failed: {e}"}]

def run_all_extractions(image_path):
    """Runs all extraction methods on the image."""
    exif = extract_exif(image_path)
    gps = extract_gps(exif)
    barcodes = extract_barcodes(image_path)
    
    return {
        "exif": exif,
        "gps": gps,
        "barcodes": barcodes
    }
