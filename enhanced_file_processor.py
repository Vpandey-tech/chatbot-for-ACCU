"""
Enhanced file processor for handling uploaded files with improved multimodal capabilities.
This module provides advanced processing for PDFs and images using open-source libraries
without requiring API keys.
"""

import os
import logging
import base64
from io import BytesIO
from typing import Dict, Any, List, Optional, Tuple
import re
import json
from PIL import Image
import pytesseract
import fitz  # PyMuPDF
from pdf2image import convert_from_path
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
import nltk
from nltk.tokenize import word_tokenize
from nltk.corpus import stopwords

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Constants
ALLOWED_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}
UPLOAD_FOLDER = 'uploads'

# Download NLTK data
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

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

def extract_text_from_image(img) -> str:
    """
    Extract text from an image using OCR.
    
    Args:
        img: PIL Image object
        
    Returns:
        Extracted text string
    """
    try:
        text = pytesseract.image_to_string(img)
        return text.strip()
    except Exception as e:
        logger.error(f"OCR error: {str(e)}")
        return ""

def analyze_image_content(img) -> Dict[str, Any]:
    """
    Perform basic image analysis to identify engineering drawings or diagrams.
    
    Args:
        img: PIL Image object
        
    Returns:
        Dictionary with image analysis results
    """
    result = {}
    
    # Get image dimensions
    width, height = img.size
    result["dimensions"] = f"{width}x{height}"
    
    # Convert to grayscale and analyze
    if img.mode != 'L':  # If not already grayscale
        gray_img = img.convert('L')
    else:
        gray_img = img
    
    # Check if image might be a technical drawing (looking for characteristics like lines, minimal color variation)
    try:
        # Convert to numpy array for analysis
        img_array = np.array(gray_img)
        
        # Calculate basic image statistics
        std_dev = np.std(img_array)
        mean_value = np.mean(img_array)
        
        # Technical drawings often have high contrast with clear lines
        if std_dev > 40 and (mean_value > 180 or mean_value < 100):
            result["image_type"] = "Likely a technical drawing or engineering diagram"
        else:
            result["image_type"] = "General image, may not be a technical drawing"
    except Exception as e:
        logger.error(f"Image analysis error: {str(e)}")
        result["image_type"] = "Unable to determine image type"
    
    return result

def process_image_file(filepath: str) -> Dict[str, Any]:
    """
    Process an image file with enhanced analysis and OCR.
    
    Args:
        filepath: Path to the image file
        
    Returns:
        Dict containing extracted information and base64-encoded image
    """
    result = {
        "text": "",
        "images": [],
        "analysis": {}
    }
    
    try:
        # Open and process the image
        with Image.open(filepath) as img:
            # Extract text with OCR
            extracted_text = extract_text_from_image(img)
            if extracted_text:
                result["text"] = extracted_text
            
            # Analyze image content
            result["analysis"] = analyze_image_content(img)
            
            # Add basic image metadata
            format_type = img.format
            mode = img.mode
            result["analysis"]["format"] = format_type
            result["analysis"]["mode"] = mode
            
            # Convert image to base64 for display
            buffered = BytesIO()
            img_format = img.format if img.format else 'JPEG'
            img.save(buffered, format=img_format)
            img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
            
            mime_type = 'jpeg' if img_format.lower() == 'jpg' else img_format.lower()
            img_data = f"data:image/{mime_type};base64,{img_str}"
            
            result["images"].append({
                "data": img_data,
                "width": img.width,
                "height": img.height,
                "format": format_type
            })
            
    except Exception as e:
        logger.error(f"Error processing image: {str(e)}")
        result["error"] = str(e)
    
    return result

def extract_text_from_pdf(filepath: str) -> Tuple[str, List[Dict[str, Any]]]:
    """
    Extract text and images from a PDF file.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Tuple containing (extracted text, list of image data dictionaries)
    """
    extracted_text = ""
    images = []
    
    try:
        # Open the PDF
        pdf_document = fitz.open(filepath)
        
        # Extract text and images from each page
        for page_num, page in enumerate(pdf_document):
            # Extract text
            page_text = page.get_text()
            extracted_text += f"\n--- Page {page_num + 1} ---\n{page_text}"
            
            # Extract images
            image_list = page.get_images(full=True)
            
            for img_index, img_info in enumerate(image_list):
                try:
                    xref = img_info[0]
                    base_image = pdf_document.extract_image(xref)
                    image_bytes = base_image["image"]
                    image_ext = base_image["ext"]
                    
                    # Convert to PIL Image
                    image = Image.open(BytesIO(image_bytes))
                    
                    # Convert to base64
                    buffered = BytesIO()
                    image.save(buffered, format=image_ext.upper())
                    img_str = base64.b64encode(buffered.getvalue()).decode('utf-8')
                    img_data = f"data:image/{image_ext};base64,{img_str}"
                    
                    images.append({
                        "data": img_data,
                        "width": image.width,
                        "height": image.height,
                        "format": image_ext.upper(),
                        "page": page_num + 1
                    })
                except Exception as e:
                    logger.error(f"Error extracting image {img_index} from page {page_num + 1}: {str(e)}")
        
        pdf_document.close()
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
    
    return extracted_text.strip(), images

def extract_metadata_from_pdf(filepath: str) -> Dict[str, Any]:
    """
    Extract metadata from a PDF file.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Dictionary with PDF metadata
    """
    metadata = {}
    
    try:
        pdf_document = fitz.open(filepath)
        metadata = {
            "page_count": pdf_document.page_count,
            "title": pdf_document.metadata.get("title", ""),
            "author": pdf_document.metadata.get("author", ""),
            "subject": pdf_document.metadata.get("subject", ""),
            "keywords": pdf_document.metadata.get("keywords", ""),
            "creator": pdf_document.metadata.get("creator", ""),
            "producer": pdf_document.metadata.get("producer", ""),
            "format": "PDF " + pdf_document.metadata.get("format", ""),
        }
        pdf_document.close()
    except Exception as e:
        logger.error(f"Error extracting PDF metadata: {str(e)}")
    
    return metadata

def process_pdf_file(filepath: str) -> Dict[str, Any]:
    """
    Process a PDF file with enhanced metadata extraction.
    
    Args:
        filepath: Path to the PDF file
        
    Returns:
        Dict with extracted content
    """
    result = {
        "text": "",
        "images": [],
        "metadata": {},
        "analysis": {}
    }
    
    try:
        # Extract text and images
        extracted_text, images = extract_text_from_pdf(filepath)
        result["text"] = extracted_text
        result["images"] = images
        
        # Extract metadata
        result["metadata"] = extract_metadata_from_pdf(filepath)
        
        # Perform basic content analysis
        if extracted_text:
            # Calculate statistics
            word_count = len(extracted_text.split())
            result["analysis"]["word_count"] = word_count
            
            # Check for CAD terminology
            cad_terms = ["drawing", "diagram", "blueprint", "plan", "model", "design", 
                        "assembly", "component", "part", "view", "section", "dimension"]
            cad_count = sum(1 for term in cad_terms if term in extracted_text.lower())
            
            engineering_terms = ["material", "steel", "aluminum", "tolerance", "specification",
                                "standard", "manufacturing", "process", "cnc", "machining"]
            engineering_count = sum(1 for term in engineering_terms if term in extracted_text.lower())
            
            # Make basic classification
            if cad_count > 3:
                result["analysis"]["document_type"] = "Likely a CAD or technical drawing document"
            elif engineering_count > 3:
                result["analysis"]["document_type"] = "Likely an engineering specification document"
            else:
                result["analysis"]["document_type"] = "General document"
                
            # Extract dimensions if present (using regex patterns)
            dimension_pattern = r'(\d+(?:\.\d+)?)\s*(?:mm|cm|m|inch|in)\b'
            dimensions = re.findall(dimension_pattern, extracted_text)
            if dimensions:
                result["analysis"]["detected_dimensions"] = dimensions[:10]  # Limit to first 10
                
    except Exception as e:
        logger.error(f"Error processing PDF: {str(e)}")
        result["error"] = str(e)
    
    return result

def process_file(filepath: str) -> Dict[str, Any]:
    """
    Process a file based on its extension with enhanced capabilities.
    
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

def extract_engineering_keywords(text: str) -> List[str]:
    """
    Extract engineering-related keywords from text.
    
    Args:
        text: Input text
        
    Returns:
        List of engineering keywords
    """
    try:
        # Tokenize and process text
        tokens = word_tokenize(text.lower())
        stop_words = set(stopwords.words('english'))
        tokens = [word for word in tokens if word.isalpha() and word not in stop_words]
        
        # Engineering-specific keywords to emphasize
        engineering_terms = {
            "manufacturing": 2.0, "machining": 2.0, "cnc": 2.0, "tooling": 2.0,
            "material": 2.0, "steel": 1.5, "aluminum": 1.5, "plastic": 1.5,
            "design": 1.5, "mechanical": 1.5, "engineering": 1.5, "tolerance": 2.0,
            "dimension": 1.5, "assembly": 1.5, "drawing": 1.5, "specification": 2.0,
            "process": 1.5, "production": 1.5, "quality": 1.5, "testing": 1.5,
            "standard": 2.0, "code": 1.5, "regulation": 1.5, "compliance": 1.5,
            "simulation": 2.0, "analysis": 1.5, "calculation": 1.5, "prototype": 1.5,
            "measurement": 1.5, "instrument": 1.5, "sensor": 1.5, "control": 1.5,
            "3d printing": 2.0, "additive": 2.0, "subtractive": 2.0, "forming": 1.5,
            "heat treatment": 2.0, "casting": 1.5, "forging": 1.5, "welding": 1.5
        }
        
        # Create document frequency dictionary
        word_freq = {}
        for token in tokens:
            word_freq[token] = word_freq.get(token, 0) + 1
        
        # Apply engineering term weights
        weighted_words = []
        for word, freq in word_freq.items():
            weight = engineering_terms.get(word, 1.0)
            weighted_words.append((word, freq * weight))
        
        # Sort by weight and return top keywords
        weighted_words.sort(key=lambda x: x[1], reverse=True)
        return [word for word, _ in weighted_words[:20]]
        
    except Exception as e:
        logger.error(f"Error extracting keywords: {str(e)}")
        return []

def prepare_content_for_model(extracted_content: Dict[str, Any]) -> Dict[str, Any]:
    """
    Prepare extracted content for the model with enhanced feature extraction.
    
    Args:
        extracted_content: Dict with text and images extracted from a file
        
    Returns:
        Dict with prepared content for the model
    """
    prepared_content = {}
    
    # Add text if available
    if "text" in extracted_content and extracted_content["text"]:
        prepared_content["text"] = extracted_content["text"]
        
        # Extract keywords for better context understanding
        keywords = extract_engineering_keywords(extracted_content["text"])
        if keywords:
            prepared_content["keywords"] = keywords
    
    # Add images if available
    if "images" in extracted_content and extracted_content["images"]:
        prepared_content["images"] = extracted_content["images"]
    
    # Add metadata if available
    if "metadata" in extracted_content and extracted_content["metadata"]:
        prepared_content["metadata"] = extracted_content["metadata"]
    
    # Add analysis if available
    if "analysis" in extracted_content and extracted_content["analysis"]:
        prepared_content["analysis"] = extracted_content["analysis"]
    
    return prepared_content