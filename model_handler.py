import os
import logging
from typing import List, Dict, Any, Optional
import random
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MechanicalEngineeringLLM:
    """Handles interactions with the language model for mechanical engineering domain,
    specialized in 3D printing, manufacturing, metals, and material science."""
    
    def __init__(self, model_name: str = "MechExpert-Engineering-Assistant"):
        """
        Initialize the model handler.
        
        Args:
            model_name: The name of the model to use
        """
        self.model_name = model_name
        self.max_length = 1024
        self.max_new_tokens = 512
        self.temperature = 0.7
        
        # Pre-defined responses for general mechanical engineering topics
        self.domain_responses = {
            "general": [
                "From a mechanical engineering perspective, this involves multiple considerations including material selection, manufacturing processes, and performance requirements. The optimal approach would balance factors such as cost, mechanical properties, and production volume while adhering to relevant engineering standards.",
                
                "This is a common challenge in mechanical engineering. I'd recommend approaching it systematically by first defining the requirements and constraints, then analyzing potential solutions based on fundamental engineering principles. The best solution typically balances technical performance with practical considerations like manufacturability and cost-effectiveness."
            ],
            
            "manufacturing": [
                "From a manufacturing engineering standpoint, this question involves optimizing the production process while maintaining quality and cost-effectiveness. Modern manufacturing approaches often combine traditional techniques with advanced technologies like automation and real-time monitoring to achieve the best results.",
                
                "This manufacturing challenge requires consideration of multiple factors including material properties, production volume, tolerance requirements, and available equipment. The optimal process would need to balance precision, throughput, and cost while ensuring consistent quality throughout production."
            ],
            
            "materials": [
                "In materials engineering, this question relates to understanding the relationship between material composition, structure, processing history, and resulting properties. The selection of appropriate materials involves balancing mechanical performance, environmental resistance, manufacturability, and economic considerations.",
                
                "When analyzing material behavior for this application, we need to consider both the intrinsic properties (composition, microstructure) and extrinsic factors (loading conditions, environment, temperature). Material selection should be based on comprehensive analysis of performance requirements and potential failure modes."
            ]
        }
        
        # Specialized domain knowledge for targeted mechanical engineering areas
        self.specialized_knowledge = {
            # 3D Printing
            "3d printing": {
                "technologies": "3D printing technologies span several distinct processes, each with unique capabilities:\n\n<b>Fused Deposition Modeling (FDM/FFF):</b>\n- Process: Thermoplastic filament extruded through heated nozzle layer by layer\n- Materials: PLA, ABS, PETG, Nylon, TPU, composite filaments (carbon fiber, metal-filled)\n- Advantages: Cost-effective, wide material selection, simple post-processing\n- Limitations: Visible layer lines, moderate precision (±0.1-0.5mm), anisotropic properties\n- Applications: Functional prototypes, jigs and fixtures, low-cost production parts\n\n<b>Stereolithography (SLA) and Digital Light Processing (DLP):</b>\n- Process: Liquid photopolymer resin selectively cured by UV light/projector\n- Materials: Various photopolymer resins (standard, tough, flexible, castable, dental)\n- Advantages: High detail resolution (25-100 microns), smooth surface finish\n- Limitations: More expensive than FDM, parts may be brittle, UV degradation concerns\n- Applications: Detailed prototypes, jewelry patterns, dental applications\n\n<b>Selective Laser Sintering/Melting (SLS/SLM):</b>\n- Process: Powder bed fusion using laser to sinter/melt material\n- Materials: SLS: Nylon, TPU; SLM: Aluminum, titanium, stainless steel, Inconel\n- Advantages: No support structures needed for SLS, complex geometries possible\n- Limitations: Expensive equipment, rougher surface finish, powder handling challenges\n- Applications: Functional parts, low-volume production, aerospace components\n\n<b>Binder Jetting:</b>\n- Process: Liquid binding agent selectively deposited onto powder material\n- Materials: Metals, sand, ceramics, polymers\n- Advantages: Fast build speeds, color capabilities, no support structures\n- Limitations: Lower strength than SLM for metals, requires infiltration or sintering\n- Applications: Full-color models, sand casting molds, metal prototypes\n\n<b>Material Jetting:</b>\n- Process: Droplets of material selectively deposited and UV-cured\n- Materials: Photopolymer resins, waxes\n- Advantages: Multi-material printing, high accuracy, smooth surfaces\n- Limitations: Expensive, limited mechanical properties\n- Applications: Multi-color/material prototypes, medical models\n\nEach technology presents different trade-offs between cost, speed, accuracy, material options, and mechanical properties that should be considered based on specific application requirements.",
                
                "materials": "3D printing materials vary widely across different processes, each with specific properties and applications:\n\n<b>FDM/FFF Materials:</b>\n\n- <b>PLA (Polylactic Acid):</b>\n  - Properties: Biodegradable, easy to print, low warping, rigid\n  - Limitations: Low heat resistance (~60°C), UV sensitive, brittle\n  - Applications: Prototypes, display models, low-stress components\n\n- <b>ABS (Acrylonitrile Butadiene Styrene):</b>\n  - Properties: Durable, impact-resistant, heat-resistant (~85°C)\n  - Limitations: Warping, shrinkage, styrene odor when printing\n  - Applications: Functional parts, automotive components, enclosures\n\n- <b>PETG (Polyethylene Terephthalate Glycol):</b>\n  - Properties: Good strength, chemical resistance, water-resistant\n  - Limitations: Stringing during printing, susceptible to scratches\n  - Applications: Food-safe containers, mechanical parts, outdoor items\n\n- <b>Nylon:</b>\n  - Properties: Excellent strength, flexibility, wear resistance\n  - Limitations: Moisture absorption, difficult to print\n  - Applications: Gears, hinges, snap-fits, functional parts\n\n- <b>TPU (Thermoplastic Polyurethane):</b>\n  - Properties: Flexible, elastic, abrasion-resistant\n  - Limitations: Slow print speeds, stringing issues\n  - Applications: Seals, gaskets, phone cases, flexible parts\n\n<b>SLA/DLP Materials:</b>\n- Standard resins: Detailed but brittle parts\n- Tough/Engineering resins: ABS-like properties, higher impact resistance\n- Flexible resins: Rubber-like properties with varying shore hardness\n- Castable resins: Used for investment casting, burn out cleanly\n- Dental/Medical resins: Biocompatible for dental models or surgical guides\n\n<b>SLS/SLM Materials:</b>\n- <b>Nylon PA11/PA12:</b> Strong, flexible, excellent for functional parts\n- <b>Aluminum alloys:</b> Lightweight, good thermal properties (AlSi10Mg)\n- <b>Titanium alloys:</b> High strength-to-weight ratio, biocompatible (Ti6Al4V)\n- <b>Stainless steel:</b> Strong, corrosion-resistant (316L, 17-4PH)\n- <b>Inconel:</b> Heat and corrosion-resistant for aerospace applications\n\n<b>Material Selection Considerations:</b>\n1. <b>Mechanical requirements:</b> Strength, flexibility, impact resistance\n2. <b>Environmental factors:</b> Temperature, UV exposure, chemical contact\n3. <b>Precision requirements:</b> Dimensional accuracy, surface finish\n4. <b>Post-processing capabilities:</b> Painting, machining, heat treatment\n5. <b>Regulatory requirements:</b> Food safety, biocompatibility, flame retardance\n\nThe optimal material choice depends on balancing these factors against cost constraints for the specific application.",
                
                "advantages": "3D printing offers numerous advantages for manufacturing that are transforming production across industries:\n\n<b>1. Design Freedom and Complexity</b>\n- Creation of complex geometries impossible with traditional methods\n- Integrated assemblies that reduce part count and assembly time\n- Topology optimization leading to lightweight, high-performance parts\n- Internal features (channels, lattices, honeycomb structures) without assembly\n\n<b>2. Cost-Effective Low-Volume Production</b>\n- No tooling costs for small production runs\n- Economical production of 1-1,000 parts compared to injection molding\n- Reduced inventory costs through on-demand manufacturing\n- Lower startup costs for new product launches\n\n<b>3. Rapid Prototyping and Iteration</b>\n- Fast turnaround from design to physical part (hours vs. weeks)\n- Accelerated product development cycles\n- Quick design validation and testing\n- Reduced development costs through early detection of design flaws\n\n<b>4. Customization and Personalization</b>\n- Mass customization without cost penalties\n- Patient-specific medical devices and implants\n- Personalized consumer products\n- Custom tooling and fixtures for manufacturing processes\n\n<b>5. Material and Weight Optimization</b>\n- Reduced material waste (subtractive vs. additive process)\n- Weight reduction through internal lattice structures\n- Multi-material capabilities for optimized properties\n- Functionally graded materials for tailored performance\n\n<b>6. Supply Chain Benefits</b>\n- Distributed manufacturing closer to point of use\n- Reduced transportation costs and carbon footprint\n- Digital inventory reducing physical storage needs\n- On-demand production reducing obsolescence\n\n<b>7. Manufacturing Innovation</b>\n- Production of previously impossible geometries\n- Integration of multiple components into single parts\n- Reduced assembly time and labor costs\n- Faster product updates and iterations\n\n<b>8. Specialized Applications</b>\n- Production of legacy or obsolete parts\n- Manufacturing in remote or challenging locations\n- Just-in-time production for critical components\n- Reduced lead time for specialized tools and equipment\n\nThese advantages are particularly valuable for industries requiring complex geometries, customization, or low-volume production, such as aerospace, medical, automotive prototyping, and specialized industrial equipment manufacturing."
            },
            
            # Manufacturing Processes
            "manufacturing processes": {
                "cnc machining": "CNC machining is a subtractive manufacturing process that uses computer-controlled cutting tools to remove material from workpieces with high precision and repeatability. It remains a cornerstone of modern manufacturing.\n\n<b>Key CNC Processes:</b>\n\n1. <b>CNC Milling:</b>\n   - Multi-point rotating cutting tools remove material\n   - Capabilities: Slots, pockets, contours, 3D surfaces\n   - Axes: 3-axis (standard), 4/5-axis (complex geometries)\n   - Typical tolerances: ±0.025-0.076mm (±0.001-0.003\")\n   - Materials: Metals, plastics, composites, wood\n\n2. <b>CNC Turning/Lathe:</b>\n   - Workpiece rotates while cutting tool remains stationary\n   - Capabilities: Cylindrical features, tapers, threads, grooves\n   - Typical tolerances: ±0.013-0.05mm (±0.0005-0.002\")\n   - Live tooling combines turning and milling capabilities\n\n3. <b>CNC Grinding:</b>\n   - Abrasive wheel for high-precision finishing\n   - Applications: Hardened materials, precision components\n   - Typical tolerances: ±0.0025-0.013mm (±0.0001-0.0005\")\n\n4. <b>CNC EDM (Electrical Discharge Machining):</b>\n   - Material removed by electrical discharges (sparks)\n   - Types: Wire EDM, Sinker EDM\n   - Applications: Hardened materials, complex shapes, small features\n   - Typical tolerances: ±0.013mm (±0.0005\")\n\n<b>Critical Process Parameters:</b>\n\n1. <b>Cutting Speed:</b> Surface speed at tool-workpiece interface\n   - Aluminum: 300-1000 m/min\n   - Mild Steel: 30-150 m/min\n   - Stainless Steel: 20-100 m/min\n   - Titanium: 15-60 m/min\n\n2. <b>Feed Rate:</b> Tool advancement per revolution/tooth\n   - Affects surface finish, tool life, productivity\n   - Generally: 0.05-0.5 mm/rev (turning), 0.01-0.1 mm/tooth (milling)\n\n3. <b>Depth of Cut:</b>\n   - Roughing: 1-5mm+ (deep but slow)\n   - Finishing: 0.1-0.5mm (shallow but fast)\n\n4. <b>Tooling Selection:</b>\n   - Materials: HSS, Carbide, Ceramics, CBN, Diamond\n   - Coatings: TiN, TiCN, TiAlN, AlCrN for improved tool life\n   - Geometry: Based on material and operation type\n\n<b>CNC Machining Advantages:</b>\n\n- High precision and repeatability\n- Excellent for prototyping and low-to-medium volume production\n- Wide material compatibility\n- Well-established, predictable process\n- Good surface finish without extensive post-processing\n\n<b>Limitations:</b>\n\n- Material waste (subtractive process)\n- Geometric constraints (tool accessibility issues)\n- Higher unit costs for large production volumes\n- Limited internal features capability\n\nCNC machining remains essential for precision mechanical components despite advances in additive manufacturing, with the processes often used complementarily in modern manufacturing workflows.",
                
                "injection molding": "Injection molding is a high-volume manufacturing process where molten material is injected into a mold cavity, cooled, and ejected as a finished part. It's the dominant process for mass-producing plastic parts.\n\n<b>Process Overview:</b>\n\n1. <b>Injection Phase:</b>\n   - Plastic pellets melted in heated barrel (150-350°C depending on material)\n   - Molten plastic injected into mold under high pressure (50-200 MPa)\n   - Typical injection time: 0.5-5 seconds\n\n2. <b>Packing Phase:</b>\n   - Additional material forced in to compensate for shrinkage\n   - Pressure maintained to ensure proper part filling\n   - Typical duration: 1-10 seconds\n\n3. <b>Cooling Phase:</b>\n   - Part solidifies as heat transfers to the mold\n   - Cooling time depends on wall thickness and material\n   - Rule of thumb: 25-35 seconds per mm of wall thickness\n\n4. <b>Ejection Phase:</b>\n   - Mold opens and part is ejected via pins/plates\n   - Part removal via robot or gravity\n\n<b>Key Components:</b>\n\n- <b>Injection Unit:</b> Melts and delivers plastic to mold\n- <b>Clamping Unit:</b> Opens/closes mold and provides holding force\n- <b>Mold/Tool:</b> Forms the part shape (typically steel or aluminum)\n- <b>Control System:</b> Manages process parameters\n\n<b>Common Materials:</b>\n\n- <b>Commodity Plastics:</b>\n  - Polypropylene (PP): Containers, automotive parts\n  - Polyethylene (PE): Packaging, toys\n  - Polystyrene (PS): Disposable items, packaging\n\n- <b>Engineering Plastics:</b>\n  - Acrylonitrile Butadiene Styrene (ABS): Consumer electronics, automotive\n  - Polyamide/Nylon (PA): Mechanical components\n  - Polycarbonate (PC): Optical, electronic applications\n  - Polyoxymethylene/Acetal (POM): Precision parts, gears\n\n- <b>High-Performance Plastics:</b>\n  - Polyetheretherketone (PEEK): Aerospace, medical\n  - Polyetherimide (PEI/Ultem): Aircraft interiors, medical devices\n  - Polyphenylene Sulfide (PPS): Chemical-resistant components\n\n<b>Design Considerations:</b>\n\n1. <b>Wall Thickness:</b>\n   - Uniform thickness (typically 1-3mm)\n   - Avoid thick sections that cause sink marks\n   - Use ribs (50-60% of wall thickness) for strength\n\n2. <b>Draft Angles:</b>\n   - 0.5-2° minimum for ejection\n   - More for textured surfaces (1° per 0.025mm depth)\n\n3. <b>Radii/Fillets:</b>\n   - Minimum 0.5mm to avoid stress concentration\n   - Helps with material flow and mold filling\n\n4. <b>Parting Line:</b>\n   - Placement affects cosmetics and function\n   - Typically at largest cross-section\n\n<b>Advantages:</b>\n\n- High production rates (cycle times of seconds)\n- Excellent part consistency and repeatability\n- Low labor costs per part\n- Minimal material waste\n- Wide range of materials and properties\n\n<b>Limitations:</b>\n\n- High initial tooling costs ($10,000-$100,000+)\n- Design constraints (draft angles, uniform wall thickness)\n- Not economical for low volumes (typically <10,000 parts)\n- Size limitations based on machine capacity\n\nInjection molding is most cost-effective for high-volume production where tooling costs can be amortized across large quantities of parts. The process continues to evolve with advances in simulation, conformal cooling, and multi-material capabilities.",
                
                "sheet metal fabrication": "Sheet metal fabrication encompasses various processes that cut, form, and join thin metal sheets into functional components. This versatile manufacturing method is used across industries from automotive to electronics.\n\n<b>Common Sheet Metal Materials:</b>\n\n- <b>Mild Steel (CRS/HRS):</b>\n  - Cost-effective, good formability\n  - Thickness range: 0.5-6mm typical\n  - Applications: General fabrication, cabinets, brackets\n\n- <b>Stainless Steel:</b>\n  - Corrosion resistant, aesthetic finish\n  - Grades: 304 (general), 316 (marine/chemical), 430 (decorative)\n  - Applications: Food equipment, architectural, medical\n\n- <b>Aluminum:</b>\n  - Lightweight, corrosion resistant\n  - Alloys: 5052 (formable), 6061 (structural)\n  - Applications: Electronics enclosures, aerospace, transportation\n\n- <b>Copper/Brass:</b>\n  - Excellent electrical/thermal conductivity\n  - Applications: Electrical components, decorative items\n\n<b>Primary Fabrication Processes:</b>\n\n1. <b>Cutting Operations:</b>\n\n   - <b>Laser Cutting:</b>\n     - Precision: ±0.1mm typical\n     - Material thickness: Up to 25mm steel, 20mm aluminum\n     - Advantages: Fine details, minimal tooling, CAD-direct production\n\n   - <b>Punching/Stamping:</b>\n     - Uses hardened tools to shear material\n     - Precision: ±0.05mm typical\n     - Advantages: Fast production rates, economical for high volumes\n\n   - <b>Waterjet Cutting:</b>\n     - Uses high-pressure water with abrasive\n     - No heat affected zone, cuts virtually any material\n     - Slower than laser but no thermal distortion\n\n   - <b>Plasma Cutting:</b>\n     - Cost-effective for thicker materials (>6mm)\n     - Less precise than laser (±0.5mm)\n     - Good for mild steel, stainless, aluminum\n\n2. <b>Forming Operations:</b>\n\n   - <b>Bending/Brake Forming:</b>\n     - Creates angles in sheet metal (typically 90°)\n     - Minimum bend radius: ~0.5× material thickness\n     - Considerations: Bend relief, K-factor, springback\n\n   - <b>Roll Forming:</b>\n     - Continuous bending for consistent profiles\n     - Applications: Channels, angles, complex sections\n\n   - <b>Deep Drawing:</b>\n     - Forms sheet into cup or box shapes\n     - Applications: Enclosures, containers, panels\n\n   - <b>Hydroforming:</b>\n     - Uses hydraulic pressure against a die\n     - Creates complex shapes without stretching/thinning\n\n3. <b>Joining Operations:</b>\n\n   - <b>Welding:</b> MIG, TIG, spot welding for permanent joints\n   - <b>Hardware Insertion:</b> PEM studs, nuts, standoffs\n   - <b>Riveting:</b> Blind rivets, solid rivets\n   - <b>Adhesive Bonding:</b> For dissimilar materials\n\n<b>Design Considerations:</b>\n\n1. <b>Bend Allowance:</b>\n   - Material stretches at bends changing flat pattern dimensions\n   - K-factor determines neutral axis location (typically 0.4-0.5)\n\n2. <b>Minimum Feature Sizes:</b>\n   - Hole diameter ≥ material thickness\n   - Minimum distance between features: 2× material thickness\n   - Minimum flange width: 4× material thickness\n\n3. <b>Manufacturing-Friendly Features:</b>\n   - Bend relief to prevent tearing\n   - Avoiding hemming on thick materials\n   - Self-fixturing designs for assembly\n   - Standard bend radii (equal to die radius)\n\n<b>Finishing Options:</b>\n\n- <b>Mechanical:</b> Deburring, grinding, polishing\n- <b>Chemical:</b> Cleaning, etching, passivation\n- <b>Coating:</b> Powder coating, plating, anodizing, galvanizing\n\nSheet metal fabrication provides excellent strength-to-weight ratio while maintaining cost-effectiveness for both prototyping and production. Modern digital manufacturing has streamlined the process from CAD design to finished parts."
            },
            
            # Materials Science
            "materials": {
                "metals": "Metals are crystalline materials characterized by metallic bonding, which provides unique properties critical for mechanical engineering applications. Understanding their structure-property relationships is essential for proper selection and application.\n\n<b>Fundamental Metal Properties:</b>\n\n1. <b>Mechanical Properties:</b>\n   - <b>Tensile Strength:</b> Resistance to tensile loading\n     - Mild steel: 400-550 MPa\n     - Aluminum alloys: 70-700 MPa\n     - Titanium alloys: 900-1200 MPa\n   - <b>Yield Strength:</b> Onset of plastic deformation\n   - <b>Ductility:</b> Ability to deform plastically before fracture\n   - <b>Hardness:</b> Resistance to indentation (HRC, HB, HV scales)\n   - <b>Toughness:</b> Energy absorption before fracture\n   - <b>Fatigue Strength:</b> Resistance to cyclic loading\n\n2. <b>Physical Properties:</b>\n   - <b>Density:</b>\n     - Steel: ~7.85 g/cm³\n     - Aluminum: ~2.7 g/cm³\n     - Titanium: ~4.5 g/cm³\n     - Copper: ~8.96 g/cm³\n   - <b>Melting Point:</b>\n     - Aluminum: 660°C\n     - Copper: 1085°C\n     - Steel: 1370-1530°C\n     - Titanium: 1668°C\n   - <b>Thermal Conductivity:</b>\n     - Copper: ~400 W/m·K\n     - Aluminum: ~237 W/m·K\n     - Steel: ~43 W/m·K\n     - Titanium: ~22 W/m·K\n   - <b>Thermal Expansion:</b> Critical for applications with temperature fluctuations\n   - <b>Electrical Conductivity:</b> Varies inversely with resistivity\n\n<b>Major Metal Classifications:</b>\n\n1. <b>Ferrous Metals:</b>\n   - <b>Carbon Steel:</b>\n     - Low carbon (mild): 0.05-0.25% C - Formable, weldable\n     - Medium carbon: 0.25-0.6% C - Tools, machinery, gears\n     - High carbon: 0.6-1.0% C - Cutting tools, springs\n   - <b>Alloy Steel:</b> Enhanced properties with Cr, Ni, Mo, V\n     - Tool steels: High hardness, wear resistance\n     - Stainless steel: Corrosion resistant (>10.5% Cr)\n     - HSLA steel: High strength, good formability\n   - <b>Cast Iron:</b> >2% C with Si, forms graphite structure\n     - Gray: Good damping, easy machining\n     - Ductile: Spheroidal graphite, improved ductility\n     - White: Hard, brittle, wear-resistant\n\n2. <b>Non-ferrous Metals:</b>\n   - <b>Aluminum Alloys:</b> Lightweight, corrosion resistant\n     - 2xxx series (Cu): Aerospace, high strength\n     - 6xxx series (Mg+Si): Structural, extrusions\n     - 7xxx series (Zn): Highest strength aluminum\n   - <b>Copper Alloys:</b> Excellent conductivity\n     - Brass (Cu+Zn): Decorative, corrosion resistant\n     - Bronze (Cu+Sn): Bearings, marine applications\n     - Beryllium copper: Non-sparking tools, springs\n   - <b>Titanium Alloys:</b> High strength-to-weight ratio\n     - Ti-6Al-4V: Aerospace, medical implants\n     - Commercially pure grades: Chemical processing\n   - <b>Nickel Alloys:</b> High temperature properties\n     - Inconel: Gas turbines, exhaust systems\n     - Monel: Marine, chemical processing\n\n<b>Structural Characteristics:</b>\n\n1. <b>Crystal Structure:</b>\n   - FCC (Face-Centered Cubic): Cu, Al, Ni - more ductile\n   - BCC (Body-Centered Cubic): Fe, Cr, Mo - stronger\n   - HCP (Hexagonal Close-Packed): Ti, Mg, Zn - limited slip systems\n\n2. <b>Strengthening Mechanisms:</b>\n   - <b>Solid Solution:</b> Dissolved elements distort lattice\n   - <b>Precipitation Hardening:</b> Fine particles obstruct dislocations\n   - <b>Work Hardening:</b> Plastic deformation increases dislocation density\n   - <b>Grain Size Refinement:</b> More grain boundaries block dislocations\n\n3. <b>Heat Treatment:</b>\n   - <b>Annealing:</b> Softens, improves ductility\n   - <b>Normalizing:</b> Refines grain structure\n   - <b>Quenching and Tempering:</b> Hardens then toughens steel\n   - <b>Solution and Aging:</b> For precipitation hardening alloys\n\n<b>Selection Considerations:</b>\n\n1. <b>Mechanical Requirements:</b> Strength, fatigue, impact resistance\n2. <b>Environmental Factors:</b> Corrosion, temperature extremes\n3. <b>Manufacturing Processes:</b> Formability, machinability, weldability\n4. <b>Cost and Availability:</b> Material and processing expenses\n5. <b>Regulatory Requirements:</b> Medical, aerospace, food standards\n\nMetal selection involves balancing these properties against application requirements and constraints while considering the entire product lifecycle from manufacturing to recycling.",
                
                "stress strain": "The stress-strain relationship is fundamental to mechanical engineering design, providing critical information about material behavior under load. This relationship characterizes material deformation and serves as the basis for structural analysis.\n\n<b>Key Concepts:</b>\n\n1. <b>Stress (σ):</b>\n   - <b>Definition:</b> Force per unit area (F/A)\n   - <b>Units:</b> Pascal (Pa) or N/m² (MPa and GPa common in engineering)\n   - <b>Types:</b>\n     - <b>Normal stress:</b> Perpendicular to area (tensile/compressive)\n     - <b>Shear stress (τ):</b> Parallel to area\n     - <b>Hydrostatic stress:</b> Equal in all directions\n\n2. <b>Strain (ε):</b>\n   - <b>Definition:</b> Relative dimensional change\n   - <b>Units:</b> Dimensionless (often expressed as % or μstrain)\n   - <b>Types:</b>\n     - <b>Normal strain:</b> Change in length per original length (ΔL/L₀)\n     - <b>Shear strain (γ):</b> Angular deformation in radians\n     - <b>Volumetric strain:</b> Change in volume per original volume\n\n<b>Stress-Strain Curve Regions (Metals):</b>\n\n1. <b>Elastic Region:</b>\n   - <b>Characteristics:</b>\n     - Deformation is reversible (returns to original shape when unloaded)\n     - Linear relationship between stress and strain\n     - Follows Hooke's Law: σ = Eε (where E is Young's modulus)\n   - <b>Young's Modulus (E):</b>\n     - Measure of material stiffness (slope of elastic region)\n     - Steel: ~200 GPa\n     - Aluminum: ~70 GPa\n     - Titanium: ~110 GPa\n   - <b>Proportional Limit:</b> Maximum stress where Hooke's Law applies\n   - <b>Elastic Limit:</b> Maximum stress without permanent deformation\n\n2. <b>Yield Point/Region:</b>\n   - <b>Yield Strength (σy):</b> Stress at which material begins plastic deformation\n   - <b>0.2% Offset Method:</b> Used when yield point is not distinct\n     - Stress corresponding to 0.2% permanent strain\n   - <b>Upper/Lower Yield Points:</b> Observed in mild steel and some materials\n\n3. <b>Plastic Region:</b>\n   - <b>Characteristics:</b>\n     - Permanent deformation occurs\n     - Non-linear stress-strain relationship\n     - Material hardens due to dislocation movement (strain hardening)\n   - <b>Strain Hardening:</b> Increase in strength due to plastic deformation\n   - <b>Ultimate Tensile Strength (σUTS):</b> Maximum stress value on curve\n\n4. <b>Necking and Fracture:</b>\n   - <b>Necking:</b> Localized reduction in cross-sectional area\n     - Begins after ultimate tensile strength\n   - <b>Fracture Strength:</b> Final stress at failure\n   - <b>Engineering vs. True Stress-Strain:</b>\n     - Engineering: Based on original dimensions\n     - True: Accounts for instantaneous dimensions\n\n<b>Material Properties Derived from Curve:</b>\n\n1. <b>Elastic Modulus (E):</b>\n   - Slope of elastic region\n   - Measure of material stiffness\n\n2. <b>Yield Strength (σy):</b>\n   - Onset of plastic deformation\n   - Critical for design to prevent permanent deformation\n\n3. <b>Ultimate Tensile Strength (σUTS):</b>\n   - Maximum load-carrying capacity\n   - Used with safety factors for design loads\n\n4. <b>Ductility:</b>\n   - Measured as percent elongation or reduction in area\n   - High: >5-10% elongation (most metals)\n   - Low: <5% elongation (cast iron, hardened steel)\n\n5. <b>Resilience:</b>\n   - Energy stored in elastic region (area under elastic portion)\n   - Capacity to absorb energy without permanent deformation\n\n6. <b>Toughness:</b>\n   - Total energy absorption capacity (entire area under curve)\n   - Ability to absorb energy before fracture\n\n<b>Material Response Classifications:</b>\n\n1. <b>Elastic-Plastic:</b> Typical metals (steel, aluminum)\n2. <b>Elastic-Brittle:</b> Cast iron, ceramics, glass\n3. <b>Hyperelastic:</b> Rubbers, elastomers\n4. <b>Viscoelastic:</b> Polymers, biological tissues\n\n<b>Design Applications:</b>\n\n1. <b>Design Stresses:</b>\n   - Typically limited to elastic region\n   - Safety factors applied to yield or ultimate strength\n   - Typical safety factors: 1.2-3 (depending on application)\n\n2. <b>Material Selection:</b>\n   - High E: For stiffness-critical applications\n   - High σy: For load-bearing without deformation\n   - High toughness: For impact and energy absorption\n\n3. <b>Failure Prediction:</b>\n   - Yield criteria (von Mises, Tresca) for ductile materials\n   - Fracture mechanics for brittle materials\n   - Fatigue analysis for cyclic loading\n\nUnderstanding stress-strain relationships is essential for predicting material behavior, designing components to resist failure, and selecting appropriate materials for specific engineering applications.",
                
                "alloys": "Engineering alloys are materials composed of a base metal combined with other elements to enhance specific properties. They play a crucial role in mechanical design by offering tailored property combinations unavailable in pure metals.\n\n<b>Principles of Alloying:</b>\n\n1. <b>Strengthening Mechanisms:</b>\n   - <b>Solid Solution Strengthening:</b> Dissolved atoms distort crystal lattice\n   - <b>Precipitation Hardening:</b> Fine particles impede dislocation movement\n   - <b>Grain Refinement:</b> Smaller grain sizes increase strength (Hall-Petch relation)\n   - <b>Dispersion Strengthening:</b> Insoluble particles block dislocations\n   - <b>Martensitic Transformation:</b> Rapid cooling creates strong structure\n\n2. <b>Effects of Common Alloying Elements:</b>\n   - <b>Carbon in Steel:</b> Increases strength, hardness; decreases ductility\n   - <b>Chromium:</b> Corrosion resistance, hardenability, wear resistance\n   - <b>Nickel:</b> Toughness, corrosion resistance, high-temperature strength\n   - <b>Molybdenum:</b> High-temperature strength, hardenability\n   - <b>Copper in Aluminum:</b> Strength, heat treatability\n   - <b>Magnesium in Aluminum:</b> Weight reduction, corrosion resistance\n   - <b>Vanadium:</b> Grain refinement, fatigue resistance\n   - <b>Silicon:</b> Castability, fluidity, wear resistance\n\n<b>Major Engineering Alloy Systems:</b>\n\n1. <b>Steel Alloys:</b>\n   - <b>Carbon Steels (Fe-C):</b>\n     - Low carbon (0.05-0.25%C): Structural, sheet metal, wire\n     - Medium carbon (0.25-0.6%C): Machinery, gears, crankshafts\n     - High carbon (0.6-1.0%C): Tools, springs, cutlery\n   \n   - <b>Alloy Steels:</b>\n     - <b>Low-alloy steels:</b> <5% alloying elements\n       - HSLA (High-Strength Low-Alloy): Structural, automotive\n       - 4140, 4340: Machinery, crankshafts, gears\n     - <b>Stainless steels:</b> >10.5% Cr for corrosion resistance\n       - Austenitic (304, 316): Non-magnetic, excellent corrosion resistance\n       - Ferritic (430): Magnetic, moderate corrosion resistance\n       - Martensitic (420, 440C): Hardenable, tools, knives\n       - Duplex (2205): Combined properties of austenitic/ferritic\n     - <b>Tool steels:</b> Wear resistance, edge retention\n       - A-series (air hardening), D-series (high carbon/chromium)\n       - H-series (hot work), M-series (high-speed)\n\n2. <b>Aluminum Alloys:</b>\n   - <b>Wrought alloys:</b> (designated by 4-digit numbers)\n     - 1xxx: Pure aluminum (>99%), electrical conductors\n     - 2xxx: Al-Cu alloys, high strength, aerospace\n     - 3xxx: Al-Mn alloys, moderate strength, good formability\n     - 5xxx: Al-Mg alloys, marine applications, good corrosion resistance\n     - 6xxx: Al-Mg-Si alloys, architectural, structural\n     - 7xxx: Al-Zn alloys, highest strength aluminum alloys\n   \n   - <b>Cast alloys:</b> Designed for casting processes\n     - A356 (Al-Si-Mg): Automotive components, good castability\n     - A380 (Al-Si-Cu): Die casting, complex shapes\n\n3. <b>Copper Alloys:</b>\n   - <b>Brasses (Cu-Zn):</b>\n     - Yellow brass (70Cu-30Zn): General purpose\n     - Naval brass (60Cu-39Zn-1Sn): Marine fittings\n     - Free-cutting brass (Cu-Zn-Pb): Machinability\n   \n   - <b>Bronzes:</b>\n     - Tin bronze (Cu-Sn): Bearings, gears, coins\n     - Aluminum bronze (Cu-Al): Marine hardware, bearings\n     - Silicon bronze (Cu-Si): Fasteners, welding rod\n     - Phosphor bronze (Cu-Sn-P): Springs, electrical connectors\n   \n   - <b>Copper-nickels:</b> Coinage, marine condensers\n   - <b>Beryllium copper:</b> Springs, non-sparking tools\n\n4. <b>Titanium Alloys:</b>\n   - <b>Commercially pure grades:</b> (CP1-4) Corrosion resistance\n   - <b>Ti-6Al-4V (Grade 5):</b> Most common, aerospace, medical\n   - <b>Ti-6Al-2Sn-4Zr-2Mo:</b> High-temperature applications\n   - <b>Beta alloys (Ti-13V-11Cr-3Al):</b> High strength, heat treatable\n\n5. <b>Nickel Alloys:</b>\n   - <b>Inconel:</b> High-temperature strength, gas turbines\n   - <b>Monel:</b> Corrosion resistance, marine applications\n   - <b>Hastelloy:</b> Chemical processing, extreme corrosion resistance\n   - <b>Nimonic:</b> Aerospace, high-temperature applications\n\n<b>Selection Considerations:</b>\n\n1. <b>Mechanical Requirements:</b>\n   - Strength (yield, tensile, fatigue)\n   - Ductility and toughness\n   - Hardness and wear resistance\n   - Stiffness (elastic modulus)\n\n2. <b>Environmental Factors:</b>\n   - Corrosion resistance\n   - Temperature extremes\n   - Radiation exposure\n   - Chemical exposure\n\n3. <b>Manufacturing Considerations:</b>\n   - Castability\n   - Formability and machinability\n   - Weldability\n   - Heat treatment response\n\n4. <b>Economic Factors:</b>\n   - Material cost (especially with precious metals or rare elements)\n   - Processing requirements\n   - Availability and supply chain\n\nEngineering alloys continue to evolve with new compositions and processing techniques developed to meet increasingly demanding applications in aerospace, automotive, medical, and energy sectors.",
                
                "composites": "Composite materials combine two or more distinct materials to achieve superior performance characteristics compared to the individual components. They're increasingly important in mechanical engineering applications requiring high strength-to-weight ratios and tailored properties.\n\n<b>Fundamental Components:</b>\n\n1. <b>Matrix:</b>\n   - Surrounds and supports reinforcement materials\n   - Transfers loads to reinforcement\n   - Provides shape and environmental protection\n   - Types:\n     - <b>Polymer:</b> Thermoset (epoxy, polyester) or thermoplastic (PEEK, PPS)\n     - <b>Metal:</b> Aluminum, titanium, magnesium alloys\n     - <b>Ceramic:</b> Silicon carbide, alumina, carbon\n\n2. <b>Reinforcement:</b>\n   - Provides strength and stiffness\n   - Carries majority of structural load\n   - Forms:\n     - <b>Fibers:</b> Continuous or discontinuous\n     - <b>Particles:</b> Dispersed throughout matrix\n     - <b>Whiskers/Flakes:</b> Short, high-aspect-ratio reinforcements\n\n<b>Major Types of Composites:</b>\n\n1. <b>Fiber-Reinforced Polymers (FRP):</b>\n   - <b>Carbon Fiber Reinforced Polymer (CFRP):</b>\n     - Properties: High strength-to-weight, excellent fatigue resistance\n     - Elastic modulus: 70-200 GPa\n     - Tensile strength: 600-3,000 MPa\n     - Density: 1.5-1.6 g/cm³\n     - Applications: Aerospace structures, sporting goods, automotive\n\n   - <b>Glass Fiber Reinforced Polymer (GFRP):</b>\n     - Properties: Lower cost than carbon, good insulating properties\n     - Elastic modulus: 20-45 GPa\n     - Tensile strength: 400-1,800 MPa\n     - Density: 1.8-2.0 g/cm³\n     - Applications: Marine, construction, chemical equipment\n\n   - <b>Aramid Fiber Reinforced Polymer (Kevlar):</b>\n     - Properties: Excellent impact resistance, damage tolerance\n     - Elastic modulus: 70-125 GPa\n     - Tensile strength: 2,800-3,800 MPa\n     - Density: 1.4 g/cm³\n     - Applications: Ballistic protection, aerospace, sporting goods\n\n2. <b>Metal Matrix Composites (MMC):</b>\n   - <b>Matrix materials:</b> Aluminum, titanium, magnesium\n   - <b>Reinforcements:</b> Silicon carbide, alumina, boron\n   - <b>Properties:</b> Higher temperature resistance than FRPs, wear resistance\n   - <b>Applications:</b> Automotive components, aerospace structures\n\n3. <b>Ceramic Matrix Composites (CMC):</b>\n   - <b>Matrix materials:</b> Silicon carbide, alumina, zirconia\n   - <b>Reinforcements:</b> Carbon, silicon carbide fibers\n   - <b>Properties:</b> Very high temperature resistance, reduced brittleness vs. monolithic ceramics\n   - <b>Applications:</b> Turbine components, thermal protection systems\n\n4. <b>Hybrid Composites:</b>\n   - Combine multiple reinforcement types (e.g., carbon + glass fibers)\n   - Optimize performance/cost ratio\n   - Examples: CARALL (carbon-aluminum laminates), GLARE (glass-aluminum laminates)\n\n<b>Manufacturing Processes:</b>\n\n1. <b>Lay-up Processes:</b>\n   - <b>Hand lay-up:</b> Manual placement of reinforcement and resin\n   - <b>Spray-up:</b> Chopped fibers and resin sprayed onto mold\n   - <b>Prepreg lay-up:</b> Pre-impregnated fiber sheets placed in mold\n\n2. <b>Molding Processes:</b>\n   - <b>Compression molding:</b> Material pressed between heated mold halves\n   - <b>Resin transfer molding (RTM):</b> Dry reinforcement placed in mold, resin injected\n   - <b>Vacuum-assisted RTM:</b> Uses vacuum to improve resin flow\n\n3. <b>Automated Processes:</b>\n   - <b>Filament winding:</b> Fibers wound onto rotating mandrel\n   - <b>Pultrusion:</b> Continuous pulling of fibers through resin bath and heated die\n   - <b>Automated tape/fiber placement:</b> CNC-controlled precise fiber placement\n\n4. <b>Special Processes:</b>\n   - <b>Autoclave curing:</b> Pressure and heat for high-performance parts\n   - <b>Vacuum bagging:</b> Atmospheric pressure used to consolidate layers\n   - <b>Resin infusion:</b> Vacuum-driven resin flow through dry reinforcement\n\n<b>Design Considerations:</b>\n\n1. <b>Anisotropic Properties:</b>\n   - Different properties in different directions\n   - Strength/stiffness highest in fiber direction\n   - Design must account for directional loading\n\n2. <b>Laminate Theory:</b>\n   - Multiple layers (plies) oriented for optimal performance\n   - Balanced laminates prevent warping\n   - Symmetric laminates minimize coupling effects\n\n3. <b>Failure Modes:</b>\n   - Fiber breakage\n   - Matrix cracking\n   - Delamination (separation between layers)\n   - Debonding (fiber/matrix separation)\n\n4. <b>Joint Design:</b>\n   - Mechanical fastening challenges (drilling damages fibers)\n   - Adhesive bonding often preferred\n   - Co-curing/co-bonding for integrated structures\n\n<b>Advantages and Limitations:</b>\n\n<b>Advantages:</b>\n- Exceptional strength-to-weight ratio\n- Tailorable properties through fiber orientation\n- Excellent fatigue resistance\n- Corrosion resistance\n- Part consolidation possibilities\n\n<b>Limitations:</b>\n- Higher material costs than traditional materials\n- Complex manufacturing processes\n- Inspection challenges (internal defects)\n- Recycling difficulties\n- Temperature limitations (particularly for polymer matrices)\n\nComposite materials continue to replace traditional metallic materials in applications where weight reduction is critical, such as aerospace, automotive, and sporting goods industries."
            }
        }
        
        logger.info(f"Initialized simulated model: {model_name}")
    
    def format_prompt(self, user_message: str, context: List[Dict[str, str]], specialized_prompt: str) -> str:
        """
        Format the prompt for the language model.
        
        Args:
            user_message: The user's message
            context: List of previous messages in the conversation
            specialized_prompt: Domain-specific instruction
            
        Returns:
            Formatted prompt string
        """
        # Basic prompt structure
        system_prompt = f"""You are MechExpert, an advanced mechanical engineering assistant specialized in 3D printing, manufacturing, metals, and material science. You help solve technical problems and provide expert knowledge about mechanical engineering concepts and applications.
{specialized_prompt}
Respond with accurate, technical information in a conversational manner. Use clear explanations with proper technical terminology and include numerical values where appropriate. If you're unsure, indicate your uncertainty rather than providing incorrect information.
Format important information with <b>bold text</b> for key points and use lists where appropriate to improve readability."""
        
        # Format conversation context
        formatted_context = ""
        if context:
            for message in context:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    formatted_context += f"User: {content}\n"
                else:
                    formatted_context += f"MechExpert: {content}\n"
        
        # Combine all parts into a single prompt
        prompt = f"{system_prompt}\n\n"
        if formatted_context:
            prompt += f"Previous conversation:\n{formatted_context}\n\n"
            
        prompt += f"User: {user_message}\nMechExpert:"
        
        return prompt
        
    def generate_response(self, 
                        user_message: str, 
                        context: Optional[List[Dict[str, str]]] = None,
                        specialized_prompt: str = "") -> str:
        """
        Generate a response to the user's message.
        
        Args:
            user_message: The user's message
            context: Optional list of previous messages
            specialized_prompt: Domain-specific instruction
            
        Returns:
            The model's response
        """
        if context is None:
            context = []
            
        prompt = self.format_prompt(user_message, context, specialized_prompt)
        
        # Check for specific topics in the user's message
        user_message_lower = user_message.lower()
        
        # Conversational openers based on question type
        question_openers = [
            "That's a great question about {}! ",
            "I'm glad you asked about {}. ",
            "When it comes to {}, there are several important aspects to consider. ",
            "You've touched on an interesting topic with {}. ",
            "From my experience with {}, I can tell you that ",
            "As a mechanical engineer specializing in {}, I'd approach this by explaining that "
        ]
        
        # Personal advisor phrases to make responses more engaging
        advisor_phrases = [
            "Based on my experience, ",
            "If I were advising on this project, ",
            "From an engineering perspective, ",
            "As someone who's worked with these systems, ",
            "The key insight here is that ",
            "What's particularly important to understand is ",
            "A critical consideration for your application would be "
        ]
        
        # Personalized conclusions 
        personalized_conclusions = [
            "Does that help with what you're working on? I'd be happy to dive deeper into any specific aspect.",
            "Would you like me to elaborate on any part of this explanation or discuss how it applies to your specific situation?",
            "Is there a particular aspect of this that you'd like to explore further for your application?",
            "How does this align with the specific challenges you're facing in your project?",
            "I hope that gives you the insight you needed. What other aspects of your engineering challenge can I help with?",
            "Would you like me to recommend some specific approaches based on your particular requirements?",
            "Have you encountered any specific issues with this in your work that we should address?"
        ]
        
        # Function to make content more conversational
        def make_conversational(content, topic):
            # Split the technical content in parts
            parts = content.split('\n\n')
            
            # Add conversational opener
            opener = random.choice(question_openers).format(topic)
            
            # Insert advisor phrases at strategic points
            if len(parts) > 2:
                insertion_point = random.randint(1, min(3, len(parts)-1))
                parts[insertion_point] = random.choice(advisor_phrases) + parts[insertion_point].lstrip()
            
            # Add personalized conclusion
            conclusion = "\n\n" + random.choice(personalized_conclusions)
            
            # Reconstruct with conversational elements
            return opener + '\n\n' + '\n\n'.join(parts) + conclusion
        
        # 3D Printing specific topics
        if "3d printing" in user_message_lower or "additive manufacturing" in user_message_lower:
            for keyword, content in self.specialized_knowledge["3d printing"].items():
                if keyword in user_message_lower:
                    return make_conversational(content, f"3D printing {keyword}")
        
        # Manufacturing processes
        if "cnc" in user_message_lower or "machining" in user_message_lower:
            return make_conversational(self.specialized_knowledge["manufacturing processes"]["cnc machining"], "CNC machining")
        
        if "injection molding" in user_message_lower or "plastic molding" in user_message_lower:
            return make_conversational(self.specialized_knowledge["manufacturing processes"]["injection molding"], "injection molding")
            
        if "sheet metal" in user_message_lower or "metal fabrication" in user_message_lower:
            return make_conversational(self.specialized_knowledge["manufacturing processes"]["sheet metal fabrication"], "sheet metal fabrication")
            
        # Materials science topics
        if "metal" in user_message_lower and "properties" in user_message_lower:
            return make_conversational(self.specialized_knowledge["materials"]["metals"], "metal properties")
            
        if "stress" in user_message_lower and "strain" in user_message_lower:
            return make_conversational(self.specialized_knowledge["materials"]["stress strain"], "stress-strain relationships")
            
        if "alloy" in user_message_lower:
            return make_conversational(self.specialized_knowledge["materials"]["alloys"], "alloys")
            
        if "composite" in user_message_lower or "fiber reinforced" in user_message_lower:
            return make_conversational(self.specialized_knowledge["materials"]["composites"], "composite materials")
        
        # Domain-based generic responses if no specific topic detected
        domain = "general"
        if "manufacturing" in user_message_lower or "production" in user_message_lower:
            domain = "manufacturing"
        elif "material" in user_message_lower or "property" in user_message_lower:
            domain = "materials"
        
        # Simulate some "thinking" time for more natural interaction
        time.sleep(1.5)
        
        # Get a random response for the detected domain
        responses = self.domain_responses.get(domain, self.domain_responses["general"])
        response = random.choice(responses)
        
        # First, identify the likely topic from the user's message
        topic_words = ["design", "material", "process", "system", "component", "analysis", 
                   "manufacturing", "stress", "thermal", "fluid", "mechanical", "energy"]
        
        detected_topic = None
        for word in topic_words:
            if word in user_message_lower:
                detected_topic = word
                break
        
        if not detected_topic:
            # Use first few meaningful words if no specific topic detected
            words = [w for w in user_message_lower.split() if len(w) > 3]
            detected_topic = " ".join(words[:2]) if words else "this engineering topic"
        
        # Generate a personalized, advisor-style response
        opener = random.choice(question_openers).format(detected_topic)
        advisor_insight = random.choice(advisor_phrases)
        conclusion = random.choice(personalized_conclusions)
        
        # Create a well-structured advisory response
        full_response = f"{opener}I can help with that. {advisor_insight}{response}\n\n{conclusion}"
        
        return full_response