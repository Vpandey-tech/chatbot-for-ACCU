"""
This module contains specialized mechanical engineering knowledge databases and reference data.
It provides expert information for common mechanical engineering topics, especially focused on:
- Manufacturing processes
- Material selection and properties
- Machine tooling and parameters
- CNC codes and machine programming
- Engineering standards (with emphasis on Indian standards)
- Design specifications
"""

# Manufacturing Processes Database
MANUFACTURING_PROCESSES = {
    "CNC_MACHINING": {
        "description": "Computer Numerical Control machining for precise metal cutting",
        "applications": ["Automotive parts", "Aerospace components", "Medical devices", "Precision tooling"],
        "material_compatibility": ["Metals", "Plastics", "Composites", "Wood"],
        "common_operations": ["Turning", "Milling", "Drilling", "Boring", "Tapping", "Reaming"],
        "advantages": ["High precision", "Good repeatability", "Complex shapes possible", "Automated production"],
        "limitations": ["High setup cost", "Limited workpiece size", "Tool wear", "Material waste"]
    },
    "3D_PRINTING": {
        "description": "Additive manufacturing process that builds objects layer by layer",
        "types": ["FDM (Fused Deposition Modeling)", "SLA (Stereolithography)", "SLS (Selective Laser Sintering)", "DMLS (Direct Metal Laser Sintering)"],
        "material_compatibility": ["Thermoplastics", "Photopolymers", "Metals", "Ceramics"],
        "advantages": ["Design freedom", "Rapid prototyping", "Low volume production", "Material efficiency"],
        "limitations": ["Size limitations", "Surface finish issues", "Material properties", "Production speed"]
    },
    "INJECTION_MOLDING": {
        "description": "Process of injecting molten material into a mold cavity to form parts",
        "applications": ["Consumer products", "Automotive components", "Medical devices", "Packaging"],
        "material_compatibility": ["Thermoplastics", "Thermosets", "Elastomers", "Metal powders (MIM)"],
        "advantages": ["High production rates", "Low labor costs", "Minimal waste", "Consistent quality"],
        "limitations": ["High tooling cost", "Design constraints", "Material limitations"]
    },
    "DIE_CASTING": {
        "description": "Process of forcing molten metal under high pressure into a mold cavity",
        "applications": ["Automotive parts", "Appliance components", "Industrial equipment"],
        "material_compatibility": ["Aluminum", "Zinc", "Magnesium", "Copper alloys"],
        "advantages": ["High precision", "Good surface finish", "High production rates", "Complex shapes"],
        "limitations": ["High tooling cost", "Limited material options", "Size limitations"]
    },
    "SHEET_METAL_FORMING": {
        "description": "Process of forming sheet metal into parts using various operations",
        "common_operations": ["Bending", "Stamping", "Drawing", "Punching", "Cutting"],
        "material_compatibility": ["Steel", "Aluminum", "Copper", "Brass", "Titanium"],
        "advantages": ["Low cost", "High production rates", "Material efficiency"],
        "limitations": ["Thickness limitations", "Design constraints", "Material properties"]
    }
}

# Materials Database (with focus on Indian context)
MATERIALS_DATABASE = {
    "STEELS": {
        "carbon_steel": {
            "IS_codes": ["IS 2062", "IS 1079", "IS 513", "IS 432"],
            "grades": {
                "IS 2062 E250": {"yield_strength": "250 MPa", "applications": ["Structural components", "Construction"]},
                "IS 2062 E350": {"yield_strength": "350 MPa", "applications": ["Heavy-duty structures", "Bridges"]},
                "IS 2062 E410": {"yield_strength": "410 MPa", "applications": ["High-strength structural components"]},
            },
            "properties": {"machinability": "Good", "weldability": "Excellent", "cost": "Low to Medium"},
            "stock_forms": ["Plates", "Sheets", "Bars", "Angles", "Channels", "I-beams"]
        },
        "alloy_steel": {
            "IS_codes": ["IS 4954", "IS 1570", "IS 5517"],
            "grades": {
                "IS 5517 26Cr4": {"composition": "0.22-0.29% C, 0.9-1.2% Cr", "applications": ["Gears", "Shafts"]},
                "IS 5517 40Cr4": {"composition": "0.36-0.44% C, 0.9-1.2% Cr", "applications": ["High stress components"]}
            },
            "properties": {"machinability": "Moderate", "weldability": "Moderate", "cost": "Medium to High"},
            "stock_forms": ["Rounds", "Flats", "Hexagons", "Plates"]
        },
        "stainless_steel": {
            "IS_codes": ["IS 6911", "IS 6528"],
            "grades": {
                "IS 6911 304": {"composition": "18% Cr, 8% Ni", "applications": ["Food processing", "Chemical equipment"]},
                "IS 6911 316": {"composition": "16% Cr, 10% Ni, 2% Mo", "applications": ["Marine applications", "Pharmaceutical equipment"]}
            },
            "properties": {"machinability": "Poor to Moderate", "weldability": "Good", "cost": "High"},
            "stock_forms": ["Sheets", "Plates", "Tubes", "Bars"]
        }
    },
    "ALUMINUM": {
        "IS_codes": ["IS 737", "IS 1285", "IS 733"],
        "grades": {
            "IS 737 64430": {"equivalent": "6063", "applications": ["Extrusions", "Architectural applications"]},
            "IS 737 64430 WP": {"equivalent": "6061", "applications": ["Structural components", "Machine parts"]}
        },
        "properties": {"machinability": "Excellent", "weldability": "Good", "cost": "Medium"},
        "stock_forms": ["Sheets", "Plates", "Rods", "Extrusions", "Tubes"]
    },
    "COPPER_ALLOYS": {
        "IS_codes": ["IS 1545", "IS 1635", "IS 410"],
        "grades": {
            "IS 410 Brass": {"composition": "Cu-Zn alloy", "applications": ["Valves", "Fittings", "Decorative hardware"]},
            "IS 1635 Bronze": {"composition": "Cu-Sn alloy", "applications": ["Bushings", "Bearings", "Gears"]}
        },
        "properties": {"machinability": "Excellent", "weldability": "Good to Excellent", "cost": "High"},
        "stock_forms": ["Sheets", "Plates", "Rods", "Tubes"]
    }
}

# CNC Machine Parameters and Tooling
CNC_PARAMETERS = {
    "TURNING": {
        "tool_bits": {
            "HSS": {"speeds": "15-30 m/min for steel", "feed_rates": "0.1-0.5 mm/rev", "cost": "Low"},
            "Carbide": {"speeds": "60-150 m/min for steel", "feed_rates": "0.2-0.8 mm/rev", "cost": "Medium"},
            "Ceramic": {"speeds": "300-500 m/min for steel", "feed_rates": "0.1-0.5 mm/rev", "cost": "High"}
        },
        "common_diameters": ["6mm", "8mm", "10mm", "12mm", "16mm", "20mm", "25mm"],
        "operations": {
            "Roughing": {"depth_of_cut": "2-5mm", "feed_rate": "High"},
            "Finishing": {"depth_of_cut": "0.5-1mm", "feed_rate": "Low"},
            "Threading": {"pitch_options": "Metric (0.5-6mm), Imperial (8-56 TPI)"}
        }
    },
    "MILLING": {
        "tool_bits": {
            "End Mills": {"types": ["2-flute", "4-flute", "ball end", "flat end"], "sizes": "1mm to 25mm"},
            "Face Mills": {"diameters": "50mm to 200mm", "application": "Surface finishing"},
            "Drill Mills": {"application": "Combined drilling and milling"}
        },
        "parameters": {
            "Spindle Speed": "Calculated as (Cutting Speed × 1000) ÷ (π × Tool Diameter)",
            "Feed Rate": "Calculated as (Spindle Speed × Number of Teeth × Chip Load)"
        }
    }
}

# CNC G-codes and M-codes (FANUC compatible)
CNC_CODES = {
    "G_CODES": {
        "G00": "Rapid positioning",
        "G01": "Linear interpolation",
        "G02": "Circular interpolation CW",
        "G03": "Circular interpolation CCW",
        "G04": "Dwell",
        "G17": "XY plane selection",
        "G18": "ZX plane selection",
        "G19": "YZ plane selection",
        "G20": "Programming in inches",
        "G21": "Programming in mm",
        "G28": "Return to home position",
        "G40": "Tool radius compensation cancel",
        "G41": "Tool radius compensation left",
        "G42": "Tool radius compensation right",
        "G43": "Tool height offset compensation positive",
        "G49": "Tool height offset cancel",
        "G54-G59": "Work coordinate systems",
        "G80": "Cancel canned cycle",
        "G81": "Drilling cycle",
        "G82": "Drilling cycle with dwell",
        "G83": "Peck drilling cycle",
        "G90": "Absolute programming",
        "G91": "Incremental programming",
        "G94": "Feed per minute",
        "G95": "Feed per revolution",
        "G96": "Constant surface speed",
        "G97": "Constant spindle speed"
    },
    "M_CODES": {
        "M00": "Program stop",
        "M01": "Optional stop",
        "M02": "End of program",
        "M03": "Spindle on CW",
        "M04": "Spindle on CCW",
        "M05": "Spindle stop",
        "M06": "Tool change",
        "M08": "Coolant on",
        "M09": "Coolant off",
        "M30": "End of program and rewind",
        "M98": "Subprogram call",
        "M99": "Subprogram end or return"
    },
    "LMW_LX20T": {
        "controller": "FANUC 0i-TF",
        "max_spindle_speed": "4500 RPM",
        "max_turning_diameter": "350mm",
        "max_turning_length": "500mm",
        "sample_program": """
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
        """
    }
}

# Indian Engineering Standards Database
INDIAN_STANDARDS = {
    "IS_CODES": {
        "IS 800": "Code of practice for general construction in steel",
        "IS 808": "Dimensions for hot rolled steel beam, column, channel and angle sections",
        "IS 814": "Covered electrodes for manual metal arc welding of carbon and carbon manganese steel",
        "IS 1024": "Code of practice for use of welding in bridges and structures subject to dynamic loading",
        "IS 1079": "Hot rolled carbon steel sheet and strip",
        "IS 1367": "Technical supply conditions for threaded steel fasteners",
        "IS 1875": "Carbon steel billets, blooms, slabs and bars for forgings",
        "IS 2062": "Hot rolled medium and high tensile structural steel",
        "IS 3757": "High strength structural bolts",
        "IS 4218": "ISO metric screw threads",
        "IS 9595": "Metal arc welding of carbon and carbon manganese steels"
    },
    "MANUFACTURING_STANDARDS": {
        "IS 1300": "Phenolic moulding materials",
        "IS 2067": "Metal cutting machine tools—Test codes for accuracy",
        "IS 3459": "Method for calculating machining times and rates",
        "IS 5462": "Sizes for measuring tools and tool elements",
        "IS 6073": "Specification for carbide cutting tools",
        "IS 10441": "Code of practice for care and maintenance of CNC machine tools",
        "IS 14489": "Code of practice for safe use of CNC machine tools"
    }
}

# Material cutting parameters
CUTTING_PARAMETERS = {
    "TURNING": {
        "MILD_STEEL": {
            "HSS": {"cutting_speed": "15-25 m/min", "feed": "0.1-0.3 mm/rev", "doc": "1-3 mm"},
            "CARBIDE": {"cutting_speed": "60-120 m/min", "feed": "0.2-0.4 mm/rev", "doc": "1-4 mm"}
        },
        "STAINLESS_STEEL": {
            "HSS": {"cutting_speed": "10-15 m/min", "feed": "0.1-0.2 mm/rev", "doc": "0.5-2 mm"},
            "CARBIDE": {"cutting_speed": "40-80 m/min", "feed": "0.1-0.3 mm/rev", "doc": "1-3 mm"}
        },
        "ALUMINUM": {
            "HSS": {"cutting_speed": "60-100 m/min", "feed": "0.1-0.4 mm/rev", "doc": "1-4 mm"},
            "CARBIDE": {"cutting_speed": "150-300 m/min", "feed": "0.2-0.5 mm/rev", "doc": "1-5 mm"}
        }
    },
    "MILLING": {
        "MILD_STEEL": {
            "HSS": {"cutting_speed": "20-30 m/min", "feed": "0.1-0.2 mm/tooth", "doc": "1-3 mm"},
            "CARBIDE": {"cutting_speed": "80-150 m/min", "feed": "0.1-0.3 mm/tooth", "doc": "1-5 mm"}
        },
        "STAINLESS_STEEL": {
            "HSS": {"cutting_speed": "15-20 m/min", "feed": "0.05-0.15 mm/tooth", "doc": "0.5-2 mm"},
            "CARBIDE": {"cutting_speed": "50-100 m/min", "feed": "0.1-0.2 mm/tooth", "doc": "1-3 mm"}
        },
        "ALUMINUM": {
            "HSS": {"cutting_speed": "70-110 m/min", "feed": "0.1-0.3 mm/tooth", "doc": "1-4 mm"},
            "CARBIDE": {"cutting_speed": "200-500 m/min", "feed": "0.1-0.4 mm/tooth", "doc": "1-6 mm"}
        }
    },
    "DRILLING": {
        "MILD_STEEL": {
            "HSS": {"cutting_speed": "15-25 m/min", "feed": "0.1-0.3 mm/rev"},
            "CARBIDE": {"cutting_speed": "50-80 m/min", "feed": "0.1-0.4 mm/rev"}
        },
        "STAINLESS_STEEL": {
            "HSS": {"cutting_speed": "10-15 m/min", "feed": "0.05-0.15 mm/rev"},
            "CARBIDE": {"cutting_speed": "30-60 m/min", "feed": "0.05-0.2 mm/rev"}
        },
        "ALUMINUM": {
            "HSS": {"cutting_speed": "60-100 m/min", "feed": "0.1-0.4 mm/rev"},
            "CARBIDE": {"cutting_speed": "100-200 m/min", "feed": "0.1-0.5 mm/rev"}
        }
    }
}

# Manufacturing services in Pune by pincode
PUNE_MANUFACTURING = {
    "411041": {
        "industrial_area": "Pimpri-Chinchwad Industrial Area",
        "specialization": ["Automotive manufacturing", "Heavy engineering", "Machine tools"],
        "major_companies": ["Tata Motors", "Bharat Forge", "Force Motors"],
        "service_providers": {
            "CNC_Machining": ["Precision Engineering Works", "Kalyani CNC", "Techno Tools"],
            "Heat_Treatment": ["Heat Treat Solutions", "Thermo Process"],
            "Surface_Finishing": ["Galvanizing India", "Premier Plating Works"]
        }
    },
    "411026": {
        "industrial_area": "Bhosari Industrial Area",
        "specialization": ["Auto components", "Sheet metal work", "Plastic molding"],
        "service_providers": {
            "Tool_Manufacturing": ["Pioneer Tools", "Accurate Tools & Dies"],
            "Inspection_Services": ["Quality Metrology", "CMM Services"]
        }
    },
    "411057": {
        "industrial_area": "Chakan Industrial Area",
        "specialization": ["Automotive", "Electronics manufacturing"],
        "major_companies": ["Volkswagen", "Mercedes-Benz", "Mahindra & Mahindra"],
        "service_providers": {
            "Assembly_Lines": ["Precision Assembly", "AutoComp Systems"],
            "Automation": ["RoboPune", "Automation Solutions"]
        }
    }
}

# Function to get tool bit recommendations based on material and process
def get_tooling_recommendation(material, process, machine_type=None):
    """
    Provides tooling recommendations based on material and manufacturing process.
    
    Args:
        material: The material being machined
        process: The manufacturing process
        machine_type: Optional machine type for specific recommendations
        
    Returns:
        Dictionary with recommendations
    """
    recommendations = {
        "tool_type": None,
        "cutting_parameters": None,
        "supplier_options": ["Sandvik Coromant", "Kennametal", "Mitsubishi", "Taegutec"],
        "indian_suppliers": ["Miranda Tools", "Addison & Co", "ISCAR India", "Forbes & Company"]
    }
    
    # Lookup material and process
    material = material.upper()
    process = process.upper()
    
    if process == "TURNING":
        if material == "MILD_STEEL" or material == "CARBON_STEEL":
            recommendations["tool_type"] = "Carbide inserts CNMG/TNMG, grade P20/P30"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["TURNING"]["MILD_STEEL"]["CARBIDE"]
        elif material == "STAINLESS_STEEL":
            recommendations["tool_type"] = "Carbide inserts CNMG/DNMG, grade M20/M30"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["TURNING"]["STAINLESS_STEEL"]["CARBIDE"]
        elif material == "ALUMINUM" or material == "ALUMINIUM":
            recommendations["tool_type"] = "Carbide inserts CCMT/DCMT, grade K10/K20"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["TURNING"]["ALUMINUM"]["CARBIDE"]
    
    elif process == "MILLING":
        if material == "MILD_STEEL" or material == "CARBON_STEEL":
            recommendations["tool_type"] = "Carbide end mills, 4-flute for steel"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["MILLING"]["MILD_STEEL"]["CARBIDE"]
        elif material == "STAINLESS_STEEL":
            recommendations["tool_type"] = "Carbide end mills, special geometry for stainless"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["MILLING"]["STAINLESS_STEEL"]["CARBIDE"]
        elif material == "ALUMINUM" or material == "ALUMINIUM":
            recommendations["tool_type"] = "Carbide end mills, 2-3 flute for aluminum"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["MILLING"]["ALUMINUM"]["CARBIDE"]
    
    elif process == "DRILLING":
        if material == "MILD_STEEL" or material == "CARBON_STEEL":
            recommendations["tool_type"] = "HSS or Carbide-tipped drills"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["DRILLING"]["MILD_STEEL"]["HSS"]
        elif material == "STAINLESS_STEEL":
            recommendations["tool_type"] = "Cobalt HSS or Carbide drills"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["DRILLING"]["STAINLESS_STEEL"]["HSS"]
        elif material == "ALUMINUM" or material == "ALUMINIUM":
            recommendations["tool_type"] = "HSS drills with 130° point angle"
            recommendations["cutting_parameters"] = CUTTING_PARAMETERS["DRILLING"]["ALUMINUM"]["HSS"]
    
    # Machine-specific recommendations
    if machine_type == "LMW_LX20T":
        recommendations["specific_notes"] = [
            "Use toolholders compatible with the LMW LX20T quick-change system",
            "Recommended insert sizes: CNMG 12, TNMG 16, DNMG 15",
            "Use external coolant supply for better chip evacuation"
        ]
    
    return recommendations

# Function to generate basic G-code for a simple turning operation
def generate_simple_gcode(operation_type, material, diameter, length):
    """
    Generates a simple G-code program for a basic operation.
    
    Args:
        operation_type: Type of machining operation
        material: Material to be machined
        diameter: Workpiece diameter
        length: Workpiece length
        
    Returns:
        String containing G-code program
    """
    if operation_type.upper() == "TURNING":
        # Get cutting parameters based on material
        material = material.upper()
        cutting_params = None
        
        if material == "MILD_STEEL" or material == "CARBON_STEEL":
            cutting_params = CUTTING_PARAMETERS["TURNING"]["MILD_STEEL"]["CARBIDE"]
        elif material == "STAINLESS_STEEL":
            cutting_params = CUTTING_PARAMETERS["TURNING"]["STAINLESS_STEEL"]["CARBIDE"]
        elif material == "ALUMINUM" or material == "ALUMINIUM":
            cutting_params = CUTTING_PARAMETERS["TURNING"]["ALUMINUM"]["CARBIDE"]
        else:
            cutting_params = {"cutting_speed": "80 m/min", "feed": "0.2 mm/rev", "doc": "2 mm"}
        
        # Extract values from cutting parameters
        cutting_speed = cutting_params["cutting_speed"].split("-")[0].strip()
        if "m/min" in cutting_speed:
            cutting_speed = cutting_speed.replace("m/min", "").strip()
        cutting_speed = int(cutting_speed)
        
        feed_rate = cutting_params["feed"].split("-")[0].strip()
        if "mm/rev" in feed_rate:
            feed_rate = feed_rate.replace("mm/rev", "").strip()
        feed_rate = float(feed_rate)
        
        # Calculate spindle speed based on cutting speed and diameter
        spindle_speed = int((cutting_speed * 1000) / (3.14159 * float(diameter)))
        if spindle_speed > 3000:
            spindle_speed = 3000  # Cap at 3000 RPM for safety
        
        # Generate G-code
        gcode = f"""% 
O1000 (TURNING PROGRAM FOR {material})
G21 G40 G95 (MM, TOOL COMP CANCEL, FEED PER REV)
G28 U0 W0 (HOME POSITION RETURN)
T0101 (TOOL SELECTION AND OFFSET)
G50 S{spindle_speed} (MAX SPINDLE SPEED LIMIT)
G96 S{cutting_speed} M03 (CONSTANT SURFACE SPEED, SPINDLE ON CW)
G00 X{float(diameter) + 5.0} Z5.0 (RAPID TO POSITION)
G01 Z0 F{feed_rate} (LINEAR FEED TO Z0)
G01 X{float(diameter) - 2.0} F{feed_rate} (FACING CUT)
G00 X{float(diameter)} (RAPID TO DIAMETER)
G00 Z2.0 (RAPID TO Z2.0)
G01 Z-{length} F{feed_rate} (TURNING TO LENGTH)
G00 X{float(diameter) + 5.0} (RAPID AWAY FROM PART)
G00 Z5.0 (RAPID TO Z5.0)
G28 U0 W0 (HOME POSITION RETURN)
M30 (END OF PROGRAM)
%"""
        
        return gcode
    
    return "Operation type not supported for G-code generation."