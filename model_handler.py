import os
import logging
from typing import List, Dict, Any, Optional
import random
import time

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class MechanicalEngineeringLLM:
    """Handles interactions with the language model for mechanical engineering domain."""
    
    def __init__(self, model_name: str = "TinyLlama/TinyLlama-1.1B-Chat-v1.0"):
        """
        Initialize the model handler.
        
        Args:
            model_name: The name of the Hugging Face model to use
        """
        self.model_name = model_name
        self.max_length = 1024
        self.max_new_tokens = 512
        self.temperature = 0.7
        
        # Pre-defined responses based on domain
        self.domain_responses = {
            "general": [
                "In mechanical engineering, this question involves several fundamental principles. The main considerations include material properties, design constraints, and engineering standards. For optimal solutions, you'll need to account for safety factors and performance requirements.",
                "This is a common mechanical engineering problem. I would approach it by first identifying the boundary conditions, then applying the relevant mechanical principles like Newton's laws or conservation of energy. The solution typically requires iterative calculations to optimize the design."
            ],
            "thermodynamics": [
                "From a thermodynamic perspective, this involves analyzing energy transfers and transformations. The first law of thermodynamics (conservation of energy) tells us that energy cannot be created or destroyed, only transferred or converted. In this case, we need to consider the heat transfer mechanisms: conduction, convection, and radiation.",
                "When analyzing this thermodynamic system, we need to consider entropy production and energy efficiency. The most efficient processes are reversible, but real-world applications always involve some irreversibility leading to entropy generation. The second law of thermodynamics sets theoretical limits on efficiency."
            ],
            "fluid_mechanics": [
                "In fluid mechanics, this question relates to the behavior of fluids in motion or at rest. We can apply Bernoulli's equation to understand how pressure, velocity, and elevation interact in fluid flow. For viscous fluids, we may need to consider the Navier-Stokes equations for more accurate modeling.",
                "This fluid mechanics problem requires analyzing both hydrostatic and hydrodynamic conditions. Reynolds number helps determine whether the flow is laminar or turbulent. For pipe systems, we also need to account for major and minor losses due to friction and fittings."
            ],
            "materials": [
                "Material selection for this application depends on several factors: mechanical properties (strength, ductility, toughness), environmental conditions (temperature, corrosion), and manufacturing considerations. Steel alloys offer good strength-to-weight ratios, while polymers provide corrosion resistance but lower mechanical properties.",
                "The material behavior you're describing relates to its stress-strain relationship. Under elastic deformation, materials follow Hooke's Law where stress is proportional to strain. Beyond the elastic limit, plastic deformation occurs, leading to permanent changes in the material structure."
            ],
            "machine_design": [
                "For this machine design problem, we need to consider the kinematics and dynamics of the mechanism. The design should account for static and dynamic loading conditions, fatigue life, and manufacturability. I recommend using factor of safety calculations based on the maximum stress theory or distortion energy theory.",
                "In designing this mechanical system, gear selection is critical. Spur gears offer simplicity and efficiency for parallel shafts, while helical gears provide smoother operation but introduce axial forces. Bevel gears are appropriate for intersecting shafts, and worm gears provide high reduction ratios."
            ],
            "manufacturing": [
                "This manufacturing process requires careful consideration of material properties, tooling, and process parameters. For precision components, CNC machining offers tight tolerances but at higher cost. Investment casting might be suitable for complex geometries, while injection molding is economical for high-volume polymer parts.",
                "Optimizing this manufacturing process involves balancing quality, cost, and production rate. Consider implementing statistical process control (SPC) to monitor key variables. Modern approaches like Design for Manufacturing (DFM) can help identify and eliminate potential manufacturing issues early in the design phase."
            ],
            "dynamics": [
                "This dynamics problem involves analyzing the motion of mechanical systems. We can use Newton's second law (F=ma) for particle dynamics or principles like work-energy and impulse-momentum for more complex systems. For rotating bodies, we need to consider moments of inertia and angular momentum.",
                "Vibration analysis for this system requires identifying natural frequencies and mode shapes. Resonance occurs when the forcing frequency matches a natural frequency, potentially causing excessive amplitudes. Damping mechanisms can help control unwanted vibrations and prevent structural damage."
            ],
            "controls": [
                "This control system can be analyzed using both time-domain and frequency-domain approaches. For stability analysis, we can examine the system's poles or apply the Routh-Hurwitz criterion. PID controllers offer a robust solution with tunable proportional, integral, and derivative terms to achieve desired performance metrics.",
                "Designing a control system for this mechanical application requires modeling the plant dynamics, selecting appropriate sensors and actuators, and implementing a control algorithm. Feedback control provides robustness against disturbances and parameter variations, while feedforward control can improve response to reference inputs."
            ]
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
        system_prompt = f"""You are MechAssist, a mechanical engineering assistant. You help solve problems related to mechanical engineering concepts and calculations.
{specialized_prompt}
Respond with accurate, technical information. If you're unsure, indicate your uncertainty rather than providing incorrect information.
Use proper units and cite fundamental principles when appropriate."""
        
        # Format conversation context
        formatted_context = ""
        if context:
            for message in context:
                role = message.get("role", "user")
                content = message.get("content", "")
                if role == "user":
                    formatted_context += f"User: {content}\n"
                else:
                    formatted_context += f"MechAssist: {content}\n"
        
        # Combine all parts into a single prompt
        prompt = f"{system_prompt}\n\n"
        if formatted_context:
            prompt += f"Previous conversation:\n{formatted_context}\n\n"
            
        prompt += f"User: {user_message}\nMechAssist:"
        
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
        
        try:
            # Format the prompt
            prompt = self.format_prompt(user_message, context, specialized_prompt)
            
            # Log the prompt
            logger.debug(f"Generating response for prompt: {prompt[:100]}...")
            
            # Simulate processing time
            time.sleep(0.5)
            
            # Determine which domain to use
            domain = "general"
            for key in self.domain_responses.keys():
                if key in specialized_prompt.lower():
                    domain = key
                    break
            
            # Get appropriate response and add some customization
            response_templates = self.domain_responses.get(domain, self.domain_responses["general"])
            response = random.choice(response_templates)
            
            # Add mentions of user's specific question
            keywords = ["stress", "strain", "heat", "temperature", "pressure", "force", 
                       "motor", "gear", "material", "fluid", "design", "efficiency", 
                       "vibration", "control", "system"]
            
            user_keywords = [kw for kw in keywords if kw.lower() in user_message.lower()]
            
            if user_keywords:
                # Add specific keyword references
                keyword_str = ", ".join(user_keywords)
                response += f"\n\nRegarding your specific question about {keyword_str}, "
                response += "it's important to consider standard engineering principles and methodologies for accurate analysis and problem-solving."
            
            return response
            
        except Exception as e:
            logger.exception(f"Error generating response: {str(e)}")
            return "I encountered an error while processing your request. Please try again."
