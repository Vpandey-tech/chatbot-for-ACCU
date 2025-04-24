import os
import logging
import json
from flask import Flask, request, jsonify, render_template
from model_handler import MechanicalEngineeringLLM
from engineering_prompts import ENGINEERING_CONTEXT, get_specialized_prompt

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")

# Initialize the LLM
model = MechanicalEngineeringLLM()

@app.route('/')
def home():
    """Render the home page with API documentation."""
    return render_template('index.html')

@app.route('/documentation')
def documentation():
    """Render the API documentation page."""
    return render_template('documentation.html')

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions."""
    try:
        data = request.json
        if not data or 'message' not in data:
            return jsonify({'error': 'Message is required'}), 400
        
        # Extract message and optional context from request
        user_message = data['message']
        context = data.get('context', [])
        domain = data.get('domain', 'general')
        
        # Get specialized prompt based on the domain
        specialized_prompt = get_specialized_prompt(domain)
        
        # Generate response using the model
        response = model.generate_response(user_message, context, specialized_prompt)
        
        return jsonify({
            'response': response,
            'domain': domain
        })
    
    except Exception as e:
        logger.exception("Error processing chat request")
        return jsonify({'error': str(e)}), 500

@app.route('/api/domains', methods=['GET'])
def get_domains():
    """Return available engineering domains for specialized knowledge."""
    domains = [
        {"id": "general", "name": "General Mechanical Engineering"},
        {"id": "thermodynamics", "name": "Thermodynamics"},
        {"id": "fluid_mechanics", "name": "Fluid Mechanics"},
        {"id": "materials", "name": "Materials Science"},
        {"id": "machine_design", "name": "Machine Design"},
        {"id": "manufacturing", "name": "Manufacturing Processes"},
        {"id": "dynamics", "name": "Dynamics and Vibrations"},
        {"id": "controls", "name": "Control Systems"}
    ]
    return jsonify(domains)

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint to verify the API is running."""
    return jsonify({
        'status': 'active',
        'model': model.model_name,
        'version': '1.0.0'
    })

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=5000, debug=True)
