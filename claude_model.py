import os
import logging
import anthropic
from typing import List, Dict, Any, Optional
from anthropic import Anthropic

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class ClaudeEngineeringAssistant:
    """Advanced mechanical engineering assistant using Claude."""
    
    def __init__(self, model_name: str = "claude-3-5-sonnet-20241022"):
        """
        Initialize the Claude model handler.
        
        Args:
            model_name: The name of the Claude model to use
        """
        self.model_name = model_name
        self.temperature = 0.7
        self.max_tokens = 4096
        
        # Initialize the Anthropic client
        anthropic_key = os.environ.get("ANTHROPIC_API_KEY")
        if not anthropic_key:
            raise ValueError("ANTHROPIC_API_KEY environment variable is not set")
        
        self.client = Anthropic(api_key=anthropic_key)
        logger.info(f"Initialized Claude model: {model_name}")
    
    def get_system_prompt(self, domain: str = "general") -> str:
        """
        Get the system prompt based on the domain.
        
        Args:
            domain: The engineering domain
            
        Returns:
            System prompt string
        """
        base_prompt = """You are MechExpert, an advanced mechanical engineering assistant specialized in 3D printing, manufacturing, metals, and material science. You help solve complex technical problems and provide expert knowledge about mechanical engineering concepts and applications.

Your expertise spans various mechanical engineering disciplines, with a special focus on:
1. 3D printing technologies and additive manufacturing processes
2. Traditional and advanced manufacturing processes
3. Materials science, metallurgy, and composite materials
4. Structural analysis and mechanical design
5. Thermal and fluid systems
6. Mechanical properties and failure analysis

When responding:
1. Be accurate, precise, and technically sound
2. Use a conversational, advisor-like tone
3. Include numerical values, technical references, and engineering principles
4. Structure your answers clearly with concise explanations
5. Format key points in bold using <b>text</b> syntax
6. Use lists and structured formats for complex information
7. Acknowledge if you're uncertain about specific details

If examining technical images or PDFs:
1. Carefully analyze any diagrams, schematics, or technical drawings
2. Extract relevant engineering information from provided content
3. Reference specific parts or elements when explaining
4. Interpret technical specifications or measurements
5. Explain underlying principles relevant to what's shown

Always aim to provide genuinely helpful engineering insights that would be expected from a senior mechanical engineer with deep domain expertise."""

        # Add domain-specific instructions
        domain_instructions = {
            "manufacturing": "Focus on manufacturing processes, tolerances, production optimization, and industrial engineering concepts.",
            "materials": "Focus on material properties, selection criteria, structure-property relationships, and performance characteristics.",
            "thermodynamics": "Focus on heat transfer mechanisms, thermal systems, energy conversion, and thermodynamic principles.",
            "fluid_mechanics": "Focus on fluid behavior, flow analysis, hydraulic systems, and aerodynamic principles.",
            "3d_printing": "Focus on additive manufacturing technologies, 3D printing materials, design for additive manufacturing, and process optimization."
        }
        
        if domain in domain_instructions:
            base_prompt += f"\n\n{domain_instructions[domain]}"
            
        return base_prompt
        
    def generate_response(self, 
                       user_message: str,
                       file_content: Optional[List[Dict]] = None,
                       context: Optional[List[Dict[str, str]]] = None,
                       domain: str = "general") -> str:
        """
        Generate a response using Claude.
        
        Args:
            user_message: The user's message
            file_content: Optional list of content parts from processed files
            context: Optional list of previous messages
            domain: Engineering domain for specialized prompting
            
        Returns:
            Claude's response
        """
        try:
            # Get system prompt based on domain
            system_prompt = self.get_system_prompt(domain)
            
            # Build message history
            messages = []
            
            if context:
                # Add previous conversation context
                for message in context:
                    role = "user" if message.get("role") == "user" else "assistant"
                    content = message.get("content", "")
                    
                    messages.append({
                        "role": role,
                        "content": content
                    })
            
            # Build the user message with file content if available
            user_content = []
            
            # Add the user's text message
            user_content.append({
                "type": "text",
                "text": user_message
            })
            
            # Add file content if available
            if file_content:
                user_content.extend(file_content)
            
            # Create the message request
            message_request = {
                "model": self.model_name,
                "max_tokens": self.max_tokens,
                "temperature": self.temperature,
                "system": system_prompt,
                "messages": []
            }
            
            # Add previous messages if available
            if messages:
                message_request["messages"] = messages
            
            # Add current user message
            message_request["messages"].append({
                "role": "user",
                "content": user_content
            })
            
            # Make the API call
            response = self.client.messages.create(**message_request)
            
            # Extract and return the response text
            return response.content[0].text
            
        except Exception as e:
            logger.error(f"Error generating Claude response: {str(e)}")
            return f"I apologize, but I encountered an error processing your request: {str(e)}"