import os
import logging
import fitz  # PyMuPDF
import base64
from PIL import Image
from io import BytesIO
import pytesseract
from pdf2image import convert_from_path, convert_from_bytes
from typing import List, Dict, Tuple, Optional, Union

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

def process_pdf_file(filepath: str) -> Dict:
    """
    Extract text and images from a PDF file.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Dict containing text content and base64-encoded images
    """
    result = {
        "text": "",
        "images": []
    }
    
    try:
        # Open the PDF
        pdf_document = fitz.open(filepath)
        
        # Extract text from each page
        text_content = []
        for page_num in range(len(pdf_document)):
            page = pdf_document[page_num]
            text_content.append(page.get_text())
            
            # Extract images
            for img_index, img in enumerate(page.get_images(full=True)):
                xref = img[0]
                base_image = pdf_document.extract_image(xref)
                image_bytes = base_image["image"]
                
                # Convert image bytes to base64
                encoded_img = base64.b64encode(image_bytes).decode('utf-8')
                mime_type = base_image["ext"]
                img_data = f"data:image/{mime_type};base64,{encoded_img}"
                
                result["images"].append({
                    "data": img_data,
                    "page": page_num + 1,
                    "index": img_index + 1
                })
        
        # Join text from all pages
        result["text"] = "\n\n".join(text_content)
        
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        result["error"] = str(e)
    
    return result

def process_image_file(filepath: str) -> Dict:
    """
    Process an image file and extract text using OCR.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dict containing OCR text and base64-encoded image
    """
    result = {
        "text": "",
        "images": []
    }
    
    try:
        # Open and process the image
        with Image.open(filepath) as img:
            # Perform OCR to extract text
            text = pytesseract.image_to_string(img)
            result["text"] = text
            
            # Convert image to base64
            buffered = BytesIO()
            img_format = img.format if img.format else 'JPEG'
            img.save(buffered, format=img_format)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            mime_type = 'jpeg' if img_format.lower() == 'jpg' else img_format.lower()
            img_data = f"data:image/{mime_type};base64,{img_str}"
            
            result["images"].append({
                "data": img_data,
                "page": 1,
                "index": 1
            })
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        result["error"] = str(e)
    
    return result

def process_file(filepath: str) -> Dict:
    """
    Process a file based on its extension.
    
    Args:
        filepath: Path to the file
        
    Returns:
        Dict with extracted content
    """
    file_ext = filepath.rsplit('.', 1)[1].lower()
    
    if file_ext == 'pdf':
        return process_pdf_file(filepath)
    elif file_ext in ['png', 'jpg', 'jpeg']:
        return process_image_file(filepath)
    else:
        return {"error": f"Unsupported file type: {file_ext}"}

def prepare_for_claude(extracted_content: Dict) -> List[Dict]:
    """
    Prepare extracted content for Claude API.
    
    Args:
        extracted_content: Dict with text and images extracted from a file
        
    Returns:
        List of content parts for Claude's API
    """
    content_parts = []
    
    # Add text content if available
    if extracted_content.get("text"):
        content_parts.append({
            "type": "text",
            "text": extracted_content["text"]
        })
    
    # Add images if available
    for img in extracted_content.get("images", []):
        if img.get("data"):
            # Extract the base64 data without the MIME prefix
            img_data = img["data"].split("base64,")[1] if "base64," in img["data"] else img["data"]
            
            content_parts.append({
                "type": "image",
                "source": {
                    "type": "base64",
                    "media_type": img["data"].split(";")[0].split(":")[1] if ":" in img["data"] else "image/jpeg",
                    "data": img_data
                }
            })
    
    return content_parts