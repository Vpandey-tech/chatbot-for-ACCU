"""
Advanced Open Source Engineering Model for Mechanical Engineering Chatbot.
This module integrates enhanced multimodal capabilities, deep search functionality,
and specialized engineering knowledge to provide high-quality responses without
requiring external API services.
"""

import re
import logging
import base64
import json
import os
from typing import List, Dict, Any, Optional, Union
import copy
import math
from io import BytesIO
from PIL import Image
import random

# Import our specialized components
from engineering_data import (
    MANUFACTURING_PROCESSES, 
    MATERIALS_DATABASE, 
    CNC_PARAMETERS, 
    CNC_CODES,
    INDIAN_STANDARDS,
    CUTTING_PARAMETERS,
    PUNE_MANUFACTURING,
    get_tooling_recommendation,
    generate_simple_gcode
)

from deep_search import DeepSearchEngine

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class AdvancedEngineeringAssistant:
    """
    Advanced open-source model for mechanical engineering queries with multimodal support.
    This class integrates enhanced document processing, deep search, and engineering expertise
    without relying on external APIs.
    """
    
    def __init__(self, model_name: str = "MechExpert-Advanced-v1"):
        """
        Initialize the advanced engineering model.
        
        Args:
            model_name: The name of the model (identifier only)
        """
        self.model_name = model_name
        
        # Initialize deep search component
        self.search_engine = DeepSearchEngine()
        
        # Define keyword-to-domain mapping
        self.domain_keywords = {
            "manufacturing": ["cnc", "machining", "turning", "milling", "drilling", "fabrication", 
                            "production", "manufacture", "3d print", "additive", "lathe", "factory",
                            "process", "forming", "cutting", "tooling", "machine", "tool"],
            
            "materials": ["steel", "aluminum", "metal", "alloy", "material", "composite", "plastic",
                        "selection", "property", "strength", "hardness", "grade", "specification",
                        "stainless", "carbon steel", "titanium", "copper", "brass", "iron"],
            
            "design": ["design", "cad", "model", "assembly", "drawing", "specification", "tolerance",
                      "constraint", "dimension", "feature", "parameter", "engineering drawing"],
            
            "standards": ["standard", "code", "regulation", "iso", "astm", "din", "is ", "indian standard",
                         "ansi", "asme", "certification", "compliance"],
            
            "calculations": ["calculate", "equation", "formula", "stress", "strain", "force", "torque",
                           "pressure", "temperature", "thermal", "load", "factor", "safety", "efficiency"]
        }
        
        # Define response templates
        self.response_templates = {
            "manufacturing": [
                "Based on manufacturing considerations, {content}",
                "From a manufacturing perspective, {content}",
                "When considering the manufacturing process, {content}",
                "The manufacturing approach for this would involve {content}",
                "Looking at this from a manufacturing standpoint, {content}"
            ],
            "materials": [
                "Regarding material selection, {content}",
                "From a materials science perspective, {content}",
                "When considering the material properties, {content}",
                "The material considerations for this application suggest {content}",
                "Based on material engineering principles, {content}"
            ],
            "general": [
                "Based on mechanical engineering principles, {content}",
                "From an engineering perspective, {content}",
                "The analysis indicates that {content}",
                "According to engineering standards and practices, {content}",
                "In the context of mechanical engineering, {content}"
            ]
        }
        
        logger.info(f"Initialized advanced engineering model: {model_name}")
    
    def detect_domain(self, query: str) -> str:
        """
        Detect the engineering domain from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            Detected domain string
        """
        query = query.lower()
        domain_scores = {}
        
        # Calculate scores for each domain
        for domain, keywords in self.domain_keywords.items():
            score = 0
            for keyword in keywords:
                if keyword in query:
                    score += 1
            domain_scores[domain] = score
        
        # Get the domain with the highest score
        if domain_scores:
            max_score = max(domain_scores.values())
            if max_score > 0:
                max_domains = [d for d, s in domain_scores.items() if s == max_score]
                return max_domains[0]
        
        return "general"
    
    def extract_materials(self, query: str) -> List[str]:
        """
        Extract mentioned materials from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            List of detected materials
        """
        query = query.lower()
        detected_materials = []
        
        # Common material keywords
        material_keywords = [
            "steel", "stainless steel", "carbon steel", "alloy steel", "mild steel",
            "aluminum", "aluminium", "copper", "brass", "bronze",
            "titanium", "nickel", "iron", "cast iron", "plastic",
            "abs", "pla", "nylon", "polyethylene", "polycarbonate",
            "composite", "carbon fiber", "wood", "ceramic"
        ]
        
        # Check for each material keyword
        for material in material_keywords:
            if material in query:
                detected_materials.append(material)
        
        return detected_materials
    
    def extract_manufacturing_processes(self, query: str) -> List[str]:
        """
        Extract mentioned manufacturing processes from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            List of detected processes
        """
        query = query.lower()
        detected_processes = []
        
        # Common manufacturing process keywords
        process_keywords = [
            "cnc", "machining", "turning", "milling", "drilling", "boring", "reaming",
            "tapping", "grinding", "edm", "welding", "casting", "forging",
            "stamping", "forming", "bending", "rolling", "extrusion", "injection molding",
            "3d printing", "additive manufacturing", "fdm", "sla", "sls", "dmls"
        ]
        
        # Check for each process keyword
        for process in process_keywords:
            if process in query:
                detected_processes.append(process)
        
        return detected_processes
    
    def extract_dimensions(self, query: str) -> Dict[str, float]:
        """
        Extract dimensions from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary of dimension types and values
        """
        dimensions = {}
        
        # Regular expressions for common dimension patterns
        diameter_patterns = [
            r'diameter (?:of )?(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)',
            r'(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)(?:\s*)(?:diameter|dia|ø)',
            r'(?:ø|Ø)(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)'
        ]
        
        length_patterns = [
            r'length (?:of )?(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)',
            r'(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)(?:\s*)(?:length|long)'
        ]
        
        width_patterns = [
            r'width (?:of )?(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)',
            r'(\d+\.?\d*)(?:\s*)(mm|cm|m|inch|in)(?:\s*)(?:width|wide)'
        ]
        
        # Extract dimensions
        for pattern in diameter_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                value, unit = matches[0]
                dimensions['diameter'] = {'value': float(value), 'unit': unit}
                break
        
        for pattern in length_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                value, unit = matches[0]
                dimensions['length'] = {'value': float(value), 'unit': unit}
                break
        
        for pattern in width_patterns:
            matches = re.findall(pattern, query, re.IGNORECASE)
            if matches:
                value, unit = matches[0]
                dimensions['width'] = {'value': float(value), 'unit': unit}
                break
        
        return dimensions
    
    def extract_location_info(self, query: str) -> Dict[str, str]:
        """
        Extract location information from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary with location information
        """
        location_info = {}
        
        # Look for cities
        indian_cities = ["mumbai", "delhi", "bangalore", "pune", "hyderabad", "chennai", 
                        "kolkata", "ahmedabad", "surat", "jaipur"]
        
        for city in indian_cities:
            if city in query.lower():
                location_info['city'] = city.capitalize()
                break
        
        # Look for pincodes
        pincode_match = re.search(r'pincode\s*[=:]\s*(\d{6})', query)
        if pincode_match:
            location_info['pincode'] = pincode_match.group(1)
        else:
            # Alternative pincode pattern
            pincode_match = re.search(r'pin\s*code\s*[=:]\s*(\d{6})', query)
            if pincode_match:
                location_info['pincode'] = pincode_match.group(1)
            else:
                # Just try to find any 6-digit number that might be a pincode
                pincode_match = re.search(r'\b(\d{6})\b', query)
                if pincode_match:
                    location_info['pincode'] = pincode_match.group(1)
        
        return location_info
    
    def extract_machine_info(self, query: str) -> Dict[str, str]:
        """
        Extract machine information from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            Dictionary with machine information
        """
        machine_info = {}
        
        # Common machine brands
        machine_brands = ["fanuc", "siemens", "haas", "mazak", "dmg mori", "okuma", 
                         "doosan", "hurco", "makino", "lmw", "ace", "bfw"]
        
        for brand in machine_brands:
            if brand in query.lower():
                machine_info['brand'] = brand.upper()
                break
        
        # Look for specific machine models
        # LMW LX20T is mentioned in their requirements
        if "lmw lx20t" in query.lower():
            machine_info['model'] = "LMW LX20T"
            machine_info['type'] = "CNC Turning Center"
            machine_info['controller'] = "FANUC 0i-TF"
        
        # Try to identify the machine type
        machine_types = {
            "turning center": ["turning center", "turning machine", "lathe", "lx20t"],
            "machining center": ["machining center", "milling machine", "mill", "vmc", "hmc"],
            "drilling machine": ["drilling machine", "drill press", "radial drill"],
            "grinding machine": ["grinding machine", "grinder", "surface grinder"]
        }
        
        for type_name, keywords in machine_types.items():
            for keyword in keywords:
                if keyword in query.lower():
                    machine_info['type'] = type_name.capitalize()
                    break
        
        return machine_info
    
    def extract_indian_standards(self, query: str) -> List[str]:
        """
        Extract Indian Standard references from the query.
        
        Args:
            query: The user's query text
            
        Returns:
            List of detected IS codes
        """
        standards = []
        
        # Look for IS code patterns (e.g., IS 800, IS 2062)
        is_codes = re.findall(r'IS\s+(\d+)', query, re.IGNORECASE)
        
        for code in is_codes:
            standards.append(f"IS {code}")
        
        return standards
    
    def process_file_content(self, file_content: Dict) -> str:
        """
        Process file content with enhanced multimodal understanding.
        
        Args:
            file_content: Dictionary containing file content
            
        Returns:
            String with file analysis
        """
        if not file_content:
            return ""
        
        analysis_parts = []
        
        # Process text content if available
        if "text" in file_content and file_content["text"]:
            text = file_content["text"]
            
            # Check if text contains technical content
            technical_terms = self.search_engine.extract_technical_terms(text)
            if technical_terms:
                term_list = ", ".join(technical_terms[:10])
                analysis_parts.append(f"I detected technical terms in your document including: {term_list}.")
            
            # Look for engineering specifications
            dimension_pattern = r'(\d+(?:\.\d+)?)\s*(?:mm|cm|m|inch|in)\b'
            dimensions = re.findall(dimension_pattern, text)
            if dimensions:
                analysis_parts.append(f"I found specific measurements in your document which may relate to part dimensions or tolerances.")
        
        # Process metadata if available
        if "metadata" in file_content and file_content["metadata"]:
            metadata = file_content["metadata"]
            if "document_type" in metadata:
                analysis_parts.append(f"This appears to be a {metadata['document_type']}.")
        
        # Process analysis data if available
        if "analysis" in file_content and file_content["analysis"]:
            analysis = file_content["analysis"]
            if "image_type" in analysis:
                analysis_parts.append(f"{analysis['image_type']}.")
            
            if "detected_dimensions" in analysis and analysis["detected_dimensions"]:
                dims = ", ".join(analysis["detected_dimensions"][:5])
                analysis_parts.append(f"I detected potential dimensions: {dims}.")
        
        # Basic image analysis
        if "images" in file_content and file_content["images"]:
            num_images = len(file_content["images"])
            analysis_parts.append(f"Your upload contains {num_images} image{'s' if num_images > 1 else ''}.")
        
        if not analysis_parts:
            return "I can see you've uploaded a file. I'll incorporate any relevant information from it into my response."
        
        return " ".join(analysis_parts)
    
    def generate_material_response(self, query: str, materials: List[str]) -> str:
        """
        Generate a response about materials based on the query with enhanced details.
        
        Args:
            query: The user's query
            materials: List of detected materials
            
        Returns:
            Response string about materials
        """
        response_parts = []
        
        for material in materials:
            material_upper = material.upper()
            
            # Check if it's a steel
            if "steel" in material:
                if "stainless" in material:
                    response_parts.append(
                        f"For stainless steel, Indian standards typically follow IS 6911. "
                        f"Common grades include SS304 and SS316. SS304 (18% Cr, 8% Ni) is suitable for "
                        f"general applications, while SS316 (16% Cr, 10% Ni, 2% Mo) offers better "
                        f"corrosion resistance for marine or pharmaceutical applications."
                    )
                elif "carbon" in material or "mild" in material:
                    response_parts.append(
                        f"For carbon/mild steel, Indian standards typically follow IS 2062. "
                        f"Common grades include E250 (yield strength: 250 MPa) for structural components "
                        f"and E350 (yield strength: 350 MPa) for heavy-duty structures. "
                        f"These are readily available in standard stock forms like plates, sheets, bars, "
                        f"angles, and channels throughout India."
                    )
                else:
                    response_parts.append(
                        f"Steel is governed by various Indian standards including IS 2062 for structural steel. "
                        f"Stock forms are widely available in India including rounds, flats, plates, and sheets. "
                        f"For precise material selection, consider the specific application requirements including "
                        f"strength, corrosion resistance, and machinability."
                    )
            
            # Check if it's aluminum
            elif "aluminum" in material or "aluminium" in material:
                response_parts.append(
                    f"Aluminum in India typically follows IS 737 standards. Common grades include "
                    f"64430 (equivalent to 6063) for extrusions and architectural applications, and "
                    f"64430 WP (equivalent to 6061) for structural components. "
                    f"Aluminum offers excellent machinability, good corrosion resistance, and "
                    f"is available in various stock forms like sheets, plates, rods, and extrusions."
                )
            
            # Other materials
            elif "copper" in material or "brass" in material or "bronze" in material:
                response_parts.append(
                    f"Copper alloys in India follow standards like IS 410 for brass and IS 1635 for bronze. "
                    f"Brass (Cu-Zn alloy) is excellent for machining and is used for valves and fittings. "
                    f"Bronze (Cu-Sn alloy) offers good wear resistance for applications like bushings and bearings. "
                    f"Both offer excellent machinability but are relatively high-cost materials."
                )
            else:
                response_parts.append(
                    f"Material selection is critical for engineering applications. Consider factors "
                    f"like mechanical properties, corrosion resistance, machinability, cost, and "
                    f"availability. For Indian standards compliance, refer to the Bureau of Indian "
                    f"Standards (BIS) specifications for your material type."
                )
        
        # If no specific materials were detected
        if not response_parts:
            response_parts.append(
                "When selecting materials for engineering applications in India, consider following "
                "appropriate Indian Standards (IS codes) such as IS 2062 for structural steel, "
                "IS 737 for aluminum, or IS 410 for copper alloys. The selection should be based on "
                "mechanical properties, environmental conditions, manufacturing processes, and cost constraints."
            )
        
        return " ".join(response_parts)
    
    def generate_manufacturing_response(self, query: str, processes: List[str], dimensions: Dict[str, float], machine_info: Dict[str, str]) -> str:
        """
        Generate a response about manufacturing processes based on the query with enhanced details.
        
        Args:
            query: The user's query
            processes: List of detected manufacturing processes
            dimensions: Dictionary of extracted dimensions
            machine_info: Dictionary of machine information
            
        Returns:
            Response string about manufacturing
        """
        response_parts = []
        
        # If specific processes were mentioned
        if processes:
            for process in processes:
                process = process.lower()
                
                if "cnc" in process or "machining" in process or "turning" in process:
                    if machine_info and 'model' in machine_info and machine_info['model'] == "LMW LX20T":
                        response_parts.append(
                            f"For CNC turning on an LMW LX20T machine, you should consider the following parameters: "
                            f"The machine uses a FANUC 0i-TF controller with a maximum spindle speed of 4500 RPM. "
                            f"For steel workpieces, use carbide inserts with CNMG/TNMG geometry. "
                            f"Recommended cutting parameters for mild steel are 60-120 m/min cutting speed, "
                            f"0.2-0.4 mm/rev feed rate, and 1-4 mm depth of cut."
                        )
                        
                        # Add G-code if we have dimensions
                        if dimensions and 'diameter' in dimensions and 'length' in dimensions:
                            diameter = dimensions['diameter']['value']
                            length = dimensions['length']['value']
                            materials = self.extract_materials(query)
                            material = "MILD_STEEL"  # Default
                            if materials and "stainless" in " ".join(materials).lower():
                                material = "STAINLESS_STEEL"
                            elif materials and ("aluminum" in " ".join(materials).lower() or "aluminium" in " ".join(materials).lower()):
                                material = "ALUMINUM"
                            
                            g_code = generate_simple_gcode("TURNING", material, diameter, length)
                            response_parts.append(f"Here's a basic G-code program for your turning operation:\n\n```\n{g_code}\n```")
                    else:
                        response_parts.append(
                            f"For CNC machining processes, select appropriate cutting tools and parameters based on the material. "
                            f"For turning operations on steel, use carbide inserts (CNMG/TNMG geometry), with cutting speeds "
                            f"of 60-120 m/min, feed rates of 0.2-0.4 mm/rev, and depths of cut of 1-4 mm. "
                            f"For aluminum, increase cutting speeds to 150-300 m/min and use specific geometries like CCMT/DCMT."
                        )
                
                elif "mill" in process:
                    response_parts.append(
                        f"For milling operations, use carbide end mills appropriate for your material. "
                        f"For steel, 4-flute end mills work well with cutting speeds of 80-150 m/min and "
                        f"feed rates of 0.1-0.3 mm/tooth. For aluminum, use 2-3 flute end mills with cutting "
                        f"speeds of 200-500 m/min. Calculate spindle speed as (Cutting Speed × 1000) ÷ (π × Tool Diameter)."
                    )
                
                elif "drill" in process:
                    response_parts.append(
                        f"For drilling operations, choose between HSS and carbide drills based on "
                        f"production volume and material. For steel, HSS drills operate at 15-25 m/min with "
                        f"feeds of 0.1-0.3 mm/rev, while carbide drills can operate at 50-80 m/min. "
                        f"For stainless steel, reduce speeds by about 30% and use rigid setups with plenty of coolant."
                    )
                
                elif "3d print" in process or "additive" in process:
                    response_parts.append(
                        f"For 3D printing/additive manufacturing, the choice of technology affects material options. "
                        f"FDM is cost-effective for thermoplastics like ABS and PLA, while SLS can work with nylon "
                        f"and DMLS can print metal parts. Consider layer height (0.1-0.3mm), infill density (20-100%), "
                        f"and orientation to balance strength, surface finish, and production time."
                    )
        
        # If no specific processes were detected
        if not response_parts:
            response_parts.append(
                "For manufacturing processes, consider factors like material, geometry, precision requirements, "
                "and production volume. CNC machining offers high precision for complex parts in metals, "
                "while 3D printing excels for prototypes and complex geometries. For production quantities, "
                "processes like injection molding (plastics) or die casting (metals) may be more cost-effective."
            )
        
        return " ".join(response_parts)
    
    def generate_tooling_response(self, query: str, processes: List[str], materials: List[str]) -> str:
        """
        Generate a response about tooling based on the query with enhanced details.
        
        Args:
            query: The user's query
            processes: List of detected manufacturing processes
            materials: List of detected materials
            
        Returns:
            Response string about tooling
        """
        if not processes or not materials:
            return ""
        
        response_parts = []
        
        # Map detected processes to standard process names
        process_mapping = {
            "turning": "TURNING",
            "lathe": "TURNING",
            "mill": "MILLING",
            "milling": "MILLING",
            "drill": "DRILLING",
            "drilling": "DRILLING"
        }
        
        # Map detected materials to standard material names
        material_mapping = {
            "mild steel": "MILD_STEEL",
            "carbon steel": "MILD_STEEL",
            "stainless steel": "STAINLESS_STEEL",
            "stainless": "STAINLESS_STEEL",
            "aluminum": "ALUMINUM",
            "aluminium": "ALUMINUM"
        }
        
        detected_process = None
        for process in processes:
            for key, value in process_mapping.items():
                if key in process:
                    detected_process = value
                    break
            if detected_process:
                break
        
        detected_material = None
        for material in materials:
            for key, value in material_mapping.items():
                if key in material:
                    detected_material = value
                    break
            if detected_material:
                break
        
        # Default values if not found
        if not detected_process:
            detected_process = "TURNING"
        if not detected_material:
            detected_material = "MILD_STEEL"
        
        # Get tooling recommendation
        if "lmw lx20t" in query.lower():
            recommendation = get_tooling_recommendation(detected_material, detected_process, "LMW_LX20T")
        else:
            recommendation = get_tooling_recommendation(detected_material, detected_process)
        
        # Format response
        if recommendation:
            response_parts.append(f"For {detected_process.lower()} {detected_material.lower().replace('_', ' ')}, I recommend using {recommendation['tool_type']}.")
            
            if recommendation['cutting_parameters']:
                params = recommendation['cutting_parameters']
                response_parts.append(f"Recommended cutting parameters: Cutting speed {params['cutting_speed']}, feed rate {params['feed']}")
                
            if 'specific_notes' in recommendation:
                response_parts.append("Important considerations:")
                for note in recommendation['specific_notes']:
                    response_parts.append(f"- {note}")
            
            response_parts.append(f"You can source these tools from manufacturers like {', '.join(recommendation['supplier_options'][:3])} or Indian suppliers such as {', '.join(recommendation['indian_suppliers'][:3])}.")
        
        return " ".join(response_parts)
    
    def generate_location_specific_response(self, location_info: Dict[str, str]) -> str:
        """
        Generate location-specific manufacturing information with enhanced details.
        
        Args:
            location_info: Dictionary with location information
            
        Returns:
            Response string with location-specific information
        """
        if not location_info:
            return ""
        
        response_parts = []
        
        # If we have a pincode for Pune
        if 'pincode' in location_info and location_info['pincode'] in PUNE_MANUFACTURING:
            pincode = location_info['pincode']
            pune_data = PUNE_MANUFACTURING[pincode]
            
            response_parts.append(f"For manufacturing in {pune_data['industrial_area']} (Pincode: {pincode}), you should know:")
            
            if 'specialization' in pune_data:
                response_parts.append(f"This area specializes in {', '.join(pune_data['specialization'])}.")
            
            if 'major_companies' in pune_data:
                response_parts.append(f"Major companies in the area include {', '.join(pune_data['major_companies'])}.")
            
            if 'service_providers' in pune_data:
                response_parts.append("Available service providers:")
                for service_type, providers in pune_data['service_providers'].items():
                    response_parts.append(f"- {service_type.replace('_', ' ')}: {', '.join(providers)}")
        
        # If we just have a city
        elif 'city' in location_info and location_info['city'].lower() == 'pune':
            response_parts.append(
                "Pune is a major manufacturing hub in India with several industrial areas including "
                "Pimpri-Chinchwad, Bhosari, and Chakan. The city has strong capabilities in automotive "
                "manufacturing, heavy engineering, and machine tools. Major companies include Tata Motors, "
                "Bharat Forge, Force Motors, and numerous tier-1 and tier-2 suppliers. For specific "
                "service providers, please provide a pincode or industrial area."
            )
        
        return " ".join(response_parts)
    
    def generate_standards_response(self, standards: List[str]) -> str:
        """
        Generate a response about engineering standards with enhanced details.
        
        Args:
            standards: List of detected standards
            
        Returns:
            Response string about standards
        """
        if not standards:
            return ""
        
        response_parts = []
        
        for standard in standards:
            if standard in INDIAN_STANDARDS["IS_CODES"]:
                response_parts.append(f"{standard}: {INDIAN_STANDARDS['IS_CODES'][standard]}")
            else:
                # Extract just the number
                std_number = standard.replace("IS ", "")
                if "800" in std_number:
                    response_parts.append(f"{standard}: This standard likely refers to IS 800, which is the Code of practice for general construction in steel.")
                elif "2062" in std_number:
                    response_parts.append(f"{standard}: This standard likely refers to IS 2062, which covers Hot rolled medium and high tensile structural steel.")
                else:
                    response_parts.append(f"{standard}: This appears to be an Indian Standard. For detailed information, refer to the Bureau of Indian Standards (BIS) documentation.")
        
        return "Regarding the Indian Standards mentioned: " + " ".join(response_parts)
    
    def analyze_image(self, file_content: Dict) -> str:
        """
        Enhanced analysis of uploaded images with improved capabilities.
        
        Args:
            file_content: Dictionary containing file data
            
        Returns:
            String with image analysis
        """
        if not file_content or "images" not in file_content or not file_content["images"]:
            return ""
        
        analysis = []
        
        # Check if we have image analysis
        if "analysis" in file_content and file_content["analysis"]:
            # Add image type information if available
            if "image_type" in file_content["analysis"]:
                analysis.append(file_content["analysis"]["image_type"])
                
            # Add dimension information if available
            if "dimensions" in file_content["analysis"]:
                analysis.append(f"Image dimensions: {file_content['analysis']['dimensions']}")
        
        # Add text extraction results if available
        if "text" in file_content and file_content["text"]:
            text = file_content["text"]
            # Truncate if too long
            if len(text) > 100:
                text = text[:100] + "..."
            analysis.append(f"Text extracted from image: \"{text}\"")
        
        if not analysis:
            analysis = [
                "I notice you've uploaded an engineering diagram or image.",
                "I can see its basic properties and will incorporate any visible technical information into my response."
            ]
        
        return " ".join(analysis)
    
    def generate_fanuc_gcode_sample(self) -> str:
        """
        Generate a sample G-code program for FANUC controller with enhanced details.
        
        Returns:
            String with G-code sample
        """
        return """
Sample G-code program for FANUC controller (LMW LX20T):

```
%
O1000 (SAMPLE TURNING PROGRAM)
G21 G40 G95 (MM, TOOL COMP CANCEL, FEED PER REV)
G28 U0 W0 (HOME POSITION RETURN)
T0101 (TOOL SELECTION AND OFFSET)
G50 S3000 (MAX SPINDLE SPEED LIMIT)
G96 S180 M03 (CONSTANT SURFACE SPEED, SPINDLE ON CW)
G00 X100.0 Z5.0 (RAPID TO POSITION)
G01 Z0 F0.2 (LINEAR FEED TO Z0)
G01 X80.0 F0.15 (LINEAR FEED TO X80.0)
G01 Z-50.0 (LINEAR FEED TO Z-50.0)
G01 X100.0 F0.2 (LINEAR FEED TO X100.0)
G00 Z5.0 (RAPID TO Z5.0)
G28 U0 W0 (HOME POSITION RETURN)
M30 (END OF PROGRAM)
%
```

Common G-codes:
- G00: Rapid positioning
- G01: Linear interpolation
- G96: Constant surface speed
- G28: Return to home position

Common M-codes:
- M03: Spindle on CW
- M08: Coolant on
- M30: End of program and rewind
"""
    
    def generate_response(self, 
                         user_message: str, 
                         context: Optional[List[Dict[str, str]]] = None,
                         specialized_prompt: Optional[str] = None,
                         file_content: Optional[Dict] = None) -> str:
        """
        Generate a response to the user's message with enhanced capabilities.
        
        Args:
            user_message: The user's message
            context: Optional list of previous messages
            specialized_prompt: Optional specialized domain prompt
            file_content: Optional dictionary with file content
            
        Returns:
            The model's response
        """
        try:
            # Detect domain and extract entities
            domain = self.detect_domain(user_message)
            materials = self.extract_materials(user_message)
            processes = self.extract_manufacturing_processes(user_message)
            dimensions = self.extract_dimensions(user_message)
            location_info = self.extract_location_info(user_message)
            machine_info = self.extract_machine_info(user_message)
            standards = self.extract_indian_standards(user_message)
            
            # Generate domain-specific responses
            material_response = self.generate_material_response(user_message, materials)
            manufacturing_response = self.generate_manufacturing_response(user_message, processes, dimensions, machine_info)
            tooling_response = self.generate_tooling_response(user_message, processes, materials)
            location_response = self.generate_location_specific_response(location_info)
            standards_response = self.generate_standards_response(standards)
            
            # Check for file content
            file_analysis = ""
            if file_content:
                file_analysis = self.process_file_content(file_content)
            
            # Check for G-code request
            g_code_sample = ""
            if "g code" in user_message.lower() or "g-code" in user_message.lower() or "fanuc" in user_message.lower():
                g_code_sample = self.generate_fanuc_gcode_sample()
            
            # Compose the initial response
            response_parts = []
            
            # Start with file analysis if available
            if file_analysis:
                response_parts.append(file_analysis)
            
            # Add domain-specific responses
            if material_response:
                response_parts.append(material_response)
            
            if manufacturing_response:
                response_parts.append(manufacturing_response)
            
            if tooling_response:
                response_parts.append(tooling_response)
            
            if location_response:
                response_parts.append(location_response)
            
            if standards_response:
                response_parts.append(standards_response)
            
            if g_code_sample:
                response_parts.append(g_code_sample)
            
            # If we couldn't generate any specific responses
            if not response_parts:
                response_parts.append(
                    "To provide a detailed engineering analysis for your question, I would need more specific information about: "
                    "1) The material you're working with, 2) The manufacturing process you plan to use, "
                    "3) Key dimensions or specifications, and 4) Any specific standards or requirements you need to meet. "
                    "For complex engineering tasks, consider consulting local engineering services in your area "
                    "who can provide hands-on expertise."
                )
            
            # Format the basic response
            basic_response = "\n\n".join(response_parts)
            
            # Enhance with deep search
            enhanced_response = self.search_engine.get_enhanced_response(user_message, basic_response)
            
            return enhanced_response
            
        except Exception as e:
            logger.error(f"Error generating response: {str(e)}")
            return "I apologize, but I encountered an error processing your engineering query. Please try rephrasing your question with more specific details about the materials, manufacturing processes, or design parameters you're working with."