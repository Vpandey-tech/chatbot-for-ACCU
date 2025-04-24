import os
import logging
from flask import Flask, request, jsonify, render_template, redirect, url_for
from model_handler import MechanicalEngineeringLLM
from engineering_prompts import get_specialized_prompt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Create the Flask app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET", "mechanical_engineering_assistant_secret")

# Configure database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL", "sqlite:///mechassist.db")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# Database setup
class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)
db.init_app(app)

# Define models
class Question(db.Model):
    """Model for storing user questions and bot responses"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False, default="general")
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Question: {self.question[:30]}...>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "question": self.question,
            "response": self.response,
            "domain": self.domain,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

# Initialize the LLM
model = MechanicalEngineeringLLM()

# Create all tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """Render the simple chatbot interface."""
    history = Question.query.order_by(Question.timestamp.desc()).all()
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
    return render_template('chatbot.html', history=history, domains=domains)

@app.route('/ask', methods=['POST'])
def ask():
    """Process user question and store in database."""
    user_message = request.form.get('question', '')
    domain = request.form.get('domain', 'general')
    
    if not user_message:
        return redirect(url_for('home'))
    
    # Get specialized prompt based on the domain
    specialized_prompt = get_specialized_prompt(domain)
    
    # Generate response using the model
    response = model.generate_response(user_message, specialized_prompt=specialized_prompt)
    
    # Store question and response in database
    new_question = Question(
        question=user_message,
        response=response,
        domain=domain
    )
    db.session.add(new_question)
    db.session.commit()
    
    return redirect(url_for('home'))

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
        
        # Store in database if API call
        new_question = Question(
            question=user_message,
            response=response,
            domain=domain
        )
        db.session.add(new_question)
        db.session.commit()
        
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

@app.route('/api/history', methods=['GET'])
def get_history():
    """Return chat history."""
    history = Question.query.order_by(Question.timestamp.desc()).all()
    return jsonify([q.to_dict() for q in history])

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
