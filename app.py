import os
import logging
import uuid
import json
from flask import Flask, request, jsonify, render_template, redirect, url_for, Response
from model_handler import MechanicalEngineeringLLM
from engineering_prompts import get_specialized_prompt
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from datetime import datetime
from werkzeug.utils import secure_filename
from typing import List, Dict, Any, Optional, Union

# Import Claude model and file processor utilities
from claude_model import ClaudeEngineeringAssistant
from file_processor import allowed_file, save_uploaded_file, process_file, prepare_for_claude

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
class Attachment(db.Model):
    """Model for storing file attachments"""
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    filepath = db.Column(db.String(255), nullable=False)
    file_type = db.Column(db.String(50), nullable=False)  # pdf, image, etc.
    question_id = db.Column(db.Integer, db.ForeignKey('question.id'), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f"<Attachment: {self.filename}>"
    
    def to_dict(self):
        return {
            "id": self.id,
            "filename": self.filename,
            "file_type": self.file_type,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }

class Question(db.Model):
    """Model for storing user questions and bot responses"""
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.Text, nullable=False)
    response = db.Column(db.Text, nullable=False)
    domain = db.Column(db.String(50), nullable=False, default="general")
    has_attachment = db.Column(db.Boolean, default=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    attachments = db.relationship('Attachment', backref='question', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<Question: {self.question[:30]}...>"
    
    def to_dict(self):
        result = {
            "id": self.id,
            "question": self.question,
            "response": self.response,
            "domain": self.domain,
            "has_attachment": self.has_attachment,
            "timestamp": self.timestamp.strftime("%Y-%m-%d %H:%M:%S")
        }
        
        if self.has_attachment:
            result["attachments"] = [attachment.to_dict() for attachment in self.attachments]
            
        return result

# Initialize the LLM models
model = MechanicalEngineeringLLM()
try:
    # Initialize Claude for multimodal capabilities
    claude_model = ClaudeEngineeringAssistant()
    claude_available = True
    logger.info("Claude model initialized successfully")
except Exception as e:
    claude_available = False
    logger.error(f"Failed to initialize Claude model: {str(e)}")

# Create all tables
with app.app_context():
    db.create_all()

@app.route('/')
def home():
    """Render the simple chatbot interface."""
    # Get history with newest conversations first (stack-like)
    history = Question.query.order_by(Question.timestamp.desc()).all()
    
    # Group conversations by session for a cleaner UI
    # For now we're using timestamp proximity as a simple way to group
    conversation_groups = []
    current_group = []
    last_timestamp = None
    
    for item in history:
        if last_timestamp and (item.timestamp - last_timestamp).total_seconds() > 600:
            # If more than 10 minutes between messages, start a new group
            if current_group:
                conversation_groups.append(current_group)
                current_group = []
        
        current_group.append(item)
        last_timestamp = item.timestamp
    
    # Add the last group if it exists
    if current_group:
        conversation_groups.append(current_group)
    
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
    return render_template('chatbot.html', history=history, conversation_groups=conversation_groups, domains=domains)

@app.route('/ask', methods=['POST'])
def ask():
    """Process user question and store in database, with optional file attachment."""
    user_message = request.form.get('question', '')
    domain = request.form.get('domain', 'general')
    
    if not user_message:
        return redirect(url_for('home'))
    
    # Check if a file was uploaded
    file_content = None
    has_attachment = False
    attachments = []
    
    if 'attachment' in request.files:
        file = request.files['attachment']
        if file and file.filename and allowed_file(file.filename):
            # Secure the filename and save the file
            filename = secure_filename(file.filename)
            unique_filename = f"{uuid.uuid4()}_{filename}"
            filepath = save_uploaded_file(file, unique_filename)
            
            # Process the file
            try:
                extracted_content = process_file(filepath)
                file_content = prepare_for_claude(extracted_content)
                has_attachment = True
                
                # Create attachment record
                file_type = filename.split('.')[-1].lower()
                attachment = Attachment(
                    filename=filename,
                    filepath=filepath,
                    file_type=file_type
                )
                attachments.append(attachment)
                
                # Add file details to user message
                user_message += f"\n\nI've attached a {file_type} file: {filename}. Please analyze it in your response."
                
            except Exception as e:
                logger.error(f"Error processing file: {str(e)}")
    
    # Get specialized prompt based on the domain
    specialized_prompt = get_specialized_prompt(domain)
    
    # Generate response using the appropriate model
    if has_attachment and claude_available:
        try:
            # Use Claude for handling files
            response = claude_model.generate_response(
                user_message=user_message,
                file_content=file_content,
                domain=domain
            )
        except Exception as e:
            logger.error(f"Error using Claude: {str(e)}")
            # Fallback to basic model
            response = model.generate_response(user_message, specialized_prompt=specialized_prompt)
    else:
        # Use standard model
        response = model.generate_response(user_message, specialized_prompt=specialized_prompt)
    
    # Store question and response in database
    new_question = Question(
        question=user_message,
        response=response,
        domain=domain,
        has_attachment=has_attachment
    )
    
    # Add to database
    db.session.add(new_question)
    db.session.flush()  # Flush to get the question ID
    
    # Associate attachments with the question
    for attachment in attachments:
        attachment.question_id = new_question.id
        db.session.add(attachment)
    
    db.session.commit()
    
    return redirect(url_for('home'))

@app.route('/api/chat', methods=['POST'])
def chat():
    """API endpoint for chat interactions with optional file attachments."""
    try:
        # Check if multipart form data (file upload) or JSON
        if request.content_type and 'multipart/form-data' in request.content_type:
            # Handle multipart form data with file
            user_message = request.form.get('message', '')
            domain = request.form.get('domain', 'general')
            context_json = request.form.get('context', '[]')
            try:
                context = json.loads(context_json)
            except:
                context = []
            
            # Check for file attachments
            file_content = None
            has_attachment = False
            attachments = []
            
            if 'attachment' in request.files:
                file = request.files['attachment']
                if file and file.filename and allowed_file(file.filename):
                    # Secure the filename and save the file
                    filename = secure_filename(file.filename)
                    unique_filename = f"{uuid.uuid4()}_{filename}"
                    filepath = save_uploaded_file(file, unique_filename)
                    
                    # Process the file
                    try:
                        extracted_content = process_file(filepath)
                        file_content = prepare_for_claude(extracted_content)
                        has_attachment = True
                        
                        # Create attachment record
                        file_type = filename.split('.')[-1].lower()
                        attachment = Attachment(
                            filename=filename,
                            filepath=filepath,
                            file_type=file_type
                        )
                        attachments.append(attachment)
                        
                        # Add file details to user message
                        user_message += f"\n\nI've attached a {file_type} file: {filename}. Please analyze it in your response."
                        
                    except Exception as e:
                        logger.error(f"Error processing file: {str(e)}")
        else:
            # Handle JSON data (no file)
            data = request.json
            if not data or 'message' not in data:
                return jsonify({'error': 'Message is required'}), 400
            
            # Extract message and optional context from request
            user_message = data['message']
            context = data.get('context', [])
            domain = data.get('domain', 'general')
            has_attachment = False
            file_content = None
            attachments = []
        
        # Get specialized prompt based on the domain
        specialized_prompt = get_specialized_prompt(domain)
        
        # Generate response using the appropriate model
        if has_attachment and claude_available:
            try:
                # Use Claude for handling files
                response = claude_model.generate_response(
                    user_message=user_message,
                    file_content=file_content,
                    context=context,
                    domain=domain
                )
            except Exception as e:
                logger.error(f"Error using Claude: {str(e)}")
                # Fallback to basic model
                response = model.generate_response(user_message, context, specialized_prompt)
        else:
            # Use standard model
            response = model.generate_response(user_message, context, specialized_prompt)
        
        # Store in database
        new_question = Question(
            question=user_message,
            response=response,
            domain=domain,
            has_attachment=has_attachment
        )
        db.session.add(new_question)
        db.session.flush()  # Flush to get the question ID
        
        # Associate attachments with the question
        for attachment in attachments:
            attachment.question_id = new_question.id
            db.session.add(attachment)
        
        db.session.commit()
        
        result = {
            'id': new_question.id,
            'response': response,
            'domain': domain,
            'has_attachment': has_attachment,
            'timestamp': new_question.timestamp.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        if has_attachment:
            result['attachments'] = [
                {
                    'filename': a.filename,
                    'file_type': a.file_type
                } for a in attachments
            ]
            
        return jsonify(result)
    
    except Exception as e:
        logger.exception("Error processing chat request")
        return jsonify({'error': str(e)}), 500
        
@app.route('/api/widget', methods=['GET'])
def widget_js():
    """Return JavaScript for embedding the chatbot in other websites."""
    return Response("""
// MechExpert Chatbot Widget
(function() {
    // Create widget container
    const container = document.createElement('div');
    container.id = 'mechexpert-chatbot-widget';
    container.style.position = 'fixed';
    container.style.bottom = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.alignItems = 'flex-end';
    
    // Create chat button
    const chatButton = document.createElement('button');
    chatButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M21 11.5a8.38 8.38 0 0 1-.9 3.8 8.5 8.5 0 0 1-7.6 4.7 8.38 8.38 0 0 1-3.8-.9L3 21l1.9-5.7a8.38 8.38 0 0 1-.9-3.8 8.5 8.5 0 0 1 4.7-7.6 8.38 8.38 0 0 1 3.8-.9h.5a8.48 8.48 0 0 1 8 8v.5z"></path></svg>';
    chatButton.style.backgroundColor = '#2563EB';
    chatButton.style.color = 'white';
    chatButton.style.border = 'none';
    chatButton.style.borderRadius = '50%';
    chatButton.style.width = '60px';
    chatButton.style.height = '60px';
    chatButton.style.cursor = 'pointer';
    chatButton.style.boxShadow = '0 4px 8px rgba(0, 0, 0, 0.1)';
    chatButton.style.display = 'flex';
    chatButton.style.alignItems = 'center';
    chatButton.style.justifyContent = 'center';
    
    // Create chat window (initially hidden)
    const chatWindow = document.createElement('div');
    chatWindow.style.display = 'none';
    chatWindow.style.flexDirection = 'column';
    chatWindow.style.width = '350px';
    chatWindow.style.height = '500px';
    chatWindow.style.backgroundColor = 'white';
    chatWindow.style.borderRadius = '12px';
    chatWindow.style.boxShadow = '0 10px 25px rgba(0, 0, 0, 0.1)';
    chatWindow.style.marginBottom = '16px';
    chatWindow.style.overflow = 'hidden';
    
    // Chat window header
    const chatHeader = document.createElement('div');
    chatHeader.style.backgroundColor = '#2563EB';
    chatHeader.style.color = 'white';
    chatHeader.style.padding = '16px';
    chatHeader.style.display = 'flex';
    chatHeader.style.justifyContent = 'space-between';
    chatHeader.style.alignItems = 'center';
    chatHeader.innerHTML = '<div><strong>MechExpert</strong><div style="font-size: 12px;">Engineering Assistant</div></div>';
    
    // Close button
    const closeButton = document.createElement('button');
    closeButton.innerHTML = '&times;';
    closeButton.style.background = 'none';
    closeButton.style.border = 'none';
    closeButton.style.color = 'white';
    closeButton.style.fontSize = '24px';
    closeButton.style.cursor = 'pointer';
    chatHeader.appendChild(closeButton);
    
    // Chat messages container
    const chatMessages = document.createElement('div');
    chatMessages.style.flex = '1';
    chatMessages.style.overflowY = 'auto';
    chatMessages.style.padding = '16px';
    chatMessages.style.display = 'flex';
    chatMessages.style.flexDirection = 'column';
    chatMessages.style.gap = '12px';
    
    // Welcome message
    const welcomeMessage = document.createElement('div');
    welcomeMessage.style.backgroundColor = '#F5F7FA';
    welcomeMessage.style.color = '#4B5563';
    welcomeMessage.style.padding = '12px 16px';
    welcomeMessage.style.borderRadius = '12px';
    welcomeMessage.style.maxWidth = '80%';
    welcomeMessage.style.alignSelf = 'flex-start';
    welcomeMessage.innerHTML = '<div style="font-size: 14px; line-height: 1.5;">Hello! I\'m MechExpert, your engineering assistant. Ask me anything about mechanical engineering, 3D printing, materials, or manufacturing.</div>';
    chatMessages.appendChild(welcomeMessage);
    
    // Chat input area
    const chatInputArea = document.createElement('div');
    chatInputArea.style.padding = '16px';
    chatInputArea.style.borderTop = '1px solid #E5E7EB';
    chatInputArea.style.display = 'flex';
    chatInputArea.style.gap = '8px';
    
    // Chat input
    const chatInput = document.createElement('input');
    chatInput.type = 'text';
    chatInput.placeholder = 'Ask about engineering...';
    chatInput.style.flex = '1';
    chatInput.style.padding = '8px 12px';
    chatInput.style.border = '1px solid #E5E7EB';
    chatInput.style.borderRadius = '8px';
    chatInput.style.outline = 'none';
    
    // Send button
    const sendButton = document.createElement('button');
    sendButton.innerHTML = '<svg xmlns="http://www.w3.org/2000/svg" width="16" height="16" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><line x1="22" y1="2" x2="11" y2="13"></line><polygon points="22 2 15 22 11 13 2 9 22 2"></polygon></svg>';
    sendButton.style.backgroundColor = '#2563EB';
    sendButton.style.color = 'white';
    sendButton.style.border = 'none';
    sendButton.style.borderRadius = '8px';
    sendButton.style.padding = '8px 12px';
    sendButton.style.cursor = 'pointer';
    sendButton.style.display = 'flex';
    sendButton.style.alignItems = 'center';
    sendButton.style.justifyContent = 'center';
    
    // Assemble chat window
    chatInputArea.appendChild(chatInput);
    chatInputArea.appendChild(sendButton);
    chatWindow.appendChild(chatHeader);
    chatWindow.appendChild(chatMessages);
    chatWindow.appendChild(chatInputArea);
    
    // Assemble final widget
    container.appendChild(chatWindow);
    container.appendChild(chatButton);
    document.body.appendChild(container);
    
    // Toggle chat window
    chatButton.addEventListener('click', function() {
        if (chatWindow.style.display === 'none') {
            chatWindow.style.display = 'flex';
            chatInput.focus();
        } else {
            chatWindow.style.display = 'none';
        }
    });
    
    // Close chat window
    closeButton.addEventListener('click', function(e) {
        e.stopPropagation();
        chatWindow.style.display = 'none';
    });
    
    // Add user message
    function addUserMessage(text) {
        const userMessage = document.createElement('div');
        userMessage.style.backgroundColor = '#2563EB';
        userMessage.style.color = 'white';
        userMessage.style.padding = '12px 16px';
        userMessage.style.borderRadius = '12px';
        userMessage.style.maxWidth = '80%';
        userMessage.style.alignSelf = 'flex-end';
        userMessage.style.wordBreak = 'break-word';
        userMessage.innerHTML = '<div style="font-size: 14px; line-height: 1.5;">' + text + '</div>';
        chatMessages.appendChild(userMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Add bot message
    function addBotMessage(text) {
        const botMessage = document.createElement('div');
        botMessage.style.backgroundColor = '#F5F7FA';
        botMessage.style.color = '#4B5563';
        botMessage.style.padding = '12px 16px';
        botMessage.style.borderRadius = '12px';
        botMessage.style.maxWidth = '80%';
        botMessage.style.alignSelf = 'flex-start';
        botMessage.style.wordBreak = 'break-word';
        botMessage.innerHTML = '<div style="font-size: 14px; line-height: 1.5;">' + text + '</div>';
        chatMessages.appendChild(botMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }
    
    // Show loading animation
    function showLoading() {
        const loadingMessage = document.createElement('div');
        loadingMessage.id = 'loading-message';
        loadingMessage.style.backgroundColor = '#F5F7FA';
        loadingMessage.style.color = '#4B5563';
        loadingMessage.style.padding = '12px 16px';
        loadingMessage.style.borderRadius = '12px';
        loadingMessage.style.maxWidth = '80%';
        loadingMessage.style.alignSelf = 'flex-start';
        loadingMessage.innerHTML = '<div style="display: flex; gap: 4px;"><div class="dot"></div><div class="dot"></div><div class="dot"></div></div>';
        
        // Add dot animation style
        const style = document.createElement('style');
        style.textContent = `
            .dot {
                width: 8px;
                height: 8px;
                background-color: #4B5563;
                border-radius: 50%;
                animation: dot-animation 1.5s infinite ease-in-out;
            }
            .dot:nth-child(2) {
                animation-delay: 0.5s;
            }
            .dot:nth-child(3) {
                animation-delay: 1s;
            }
            @keyframes dot-animation {
                0%, 100% { opacity: 0.3; transform: scale(0.8); }
                50% { opacity: 1; transform: scale(1.2); }
            }
        `;
        document.head.appendChild(style);
        
        chatMessages.appendChild(loadingMessage);
        chatMessages.scrollTop = chatMessages.scrollHeight;
        return loadingMessage;
    }
    
    // Hide loading animation
    function hideLoading(loadingMessage) {
        if (loadingMessage && loadingMessage.parentNode) {
            loadingMessage.parentNode.removeChild(loadingMessage);
        }
    }
    
    // Send message to API
    async function sendMessage(text) {
        try {
            addUserMessage(text);
            const loadingMessage = showLoading();
            
            const response = await fetch('YOUR_BASE_URL_HERE/api/chat', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    message: text
                })
            });
            
            const data = await response.json();
            hideLoading(loadingMessage);
            
            if (data.error) {
                addBotMessage('Sorry, I encountered an error: ' + data.error);
            } else {
                addBotMessage(data.response);
            }
        } catch (error) {
            hideLoading(document.getElementById('loading-message'));
            addBotMessage('Sorry, I encountered a network error. Please try again.');
            console.error('Error:', error);
        }
    }
    
    // Send message on button click
    sendButton.addEventListener('click', function() {
        const message = chatInput.value.trim();
        if (message) {
            sendMessage(message);
            chatInput.value = '';
        }
    });
    
    // Send message on Enter key
    chatInput.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') {
            const message = chatInput.value.trim();
            if (message) {
                sendMessage(message);
                chatInput.value = '';
            }
        }
    });
})();
    """, mimetype='application/javascript')

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
