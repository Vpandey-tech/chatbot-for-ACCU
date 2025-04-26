"""
Free file processor for handling uploaded files without requiring API keys.
This module provides simple file processing capabilities for PDFs and images
using open-source libraries.
"""

import os
import logging
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional
from PIL import Image
import re

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'

def allowed_file(filename: str) -> bool:
    """Check if the file extension is allowed."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def ensure_upload_dir() -> None:
    """Ensure the upload directory exists."""
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)
        
def save_uploaded_file(file, filename: str) -> str:
    """Save an uploaded file to the upload directory."""
    ensure_upload_dir()
    filepath = os.path.join(UPLOAD_FOLDER, filename)
    file.save(filepath)
    return filepath

def process_image_file(filepath: str) -> Dict[str, Any]:
    """
    Process an image file and extract basic information.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dict containing image data
    """
    result = {
        "text": "",
        "images": []
    }
    
    try:
        # Open and process the image
        with Image.open(filepath) as img:
            # Get basic image information
            width, height = img.size
            format_type = img.format
            mode = img.mode
            
            # Add basic description
            result["text"] = f"Image: {os.path.basename(filepath)}\nFormat: {format_type}\nDimensions: {width}x{height} pixels\nColor mode: {mode}"
            
            # Convert image to base64
            buffered = BytesIO()
            img_format = img.format if img.format else 'JPEG'
            img.save(buffered, format=img_format)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            mime_type = 'jpeg' if img_format.lower() == 'jpg' else img_format.lower()
            img_data = f"data:image/{mime_type};base64,{img_str}"
            
            result["images"].append({
                "data": img_data,
                "width": width,
                "height": height,
                "format": format_type
            })
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        result["error"] = str(e)
    
    return result

def process_pdf_file(filepath: str) -> Dict[str, Any]:
    """
    Process a PDF file with minimal extraction.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Dict with basic PDF info
    """
    result = {
        "text": f"PDF file: {os.path.basename(filepath)}\n" +
                f"Note: Detailed PDF content extraction requires additional libraries. " +
                f"Basic analysis will be provided based on your query.",
        "images": []
    }
    
    # For a full implementation, you would use libraries like PyPDF2 or PDF.js
    # but we're keeping it minimal for simplicity
    
    return result

def process_file(filepath: str) -> Dict[str, Any]:
    """
    Process a file based on its extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dict with extracted content
    """
    file_ext = filepath.rsplit('.', 1)[1].lower() if '.' in filepath else ''
    
    if file_ext in ['jpg', 'jpeg', 'png']:
        return process_image_file(filepath)
    elif file_ext == 'pdf':
        return process_pdf_file(filepath)
    else:
        return {"error": f"Unsupported file type: {file_ext}"}

def prepare_for_model(extracted_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare extracted content for the model.
    
    Args:
        extracted_content: Dict with text and images extracted from a file
        
    Returns:
        Dict with prepared content for the model
    """
    prepared_content = {}
    
    # Add text if available
    if "text" in extracted_content and extracted_content["text"]:
        prepared_content["text"] = extracted_content["text"]
    
    # Add images if available
    if "images" in extracted_content and extracted_content["images"]:
        prepared_content["images"] = extracted_content["images"]
    
    return prepared_content