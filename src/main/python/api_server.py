"""
REST API server for Selenium SLM inference.
Provides HTTP endpoints for code generation from Java.
"""

from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
from inference_improved import ImprovedSeleniumGenerator
import logging
import os
import re

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes
logging.basicConfig(level=logging.INFO)

# Serve static web files
WEB_DIR = os.path.join(os.path.dirname(__file__), '..', '..', 'web')
WEB_DIR = os.path.abspath(WEB_DIR)

# Initialize improved model once at startup
generator = ImprovedSeleniumGenerator('selenium_ngram_model.pkl')

@app.route('/', methods=['GET'])
def index():
    """Serve the web interface"""
    return send_from_directory(WEB_DIR, 'index.html')

@app.route('/web/<path:filename>', methods=['GET'])
def web_files(filename):
    """Serve web assets"""
    return send_from_directory(WEB_DIR, filename)

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({'status': 'healthy', 'model': 'loaded'}), 200

@app.route('/generate', methods=['POST'])
def generate_code():
    """
    Generate Selenium code from prompt.
    
    Request JSON:
    {
        "prompt": "action: click\nelement_type: button",
        "max_tokens": 50,
        "temperature": 0.7
    }
    """
    try:
        data = request.get_json()
        
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 50)
        temperature = data.get('temperature', 0.7)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Generate code with improved cleaning
        generated = generator.generate_clean(
            prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )
        
        return jsonify({
            'prompt': prompt,
            'generated': generated,
            'tokens_generated': len(generated.split())
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating code: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest-locator', methods=['POST'])
def suggest_locator():
    """
    Suggest optimal locator for element from HTML.
    
    Request JSON:
    {
        "html": "<button id='submitBtn'>Submit</button>"
    }
    """
    try:
        data = request.get_json()
        
        html = data.get('html', '')
        
        if not html:
            return jsonify({'error': 'HTML is required'}), 400
        
        # Use improved generator
        result = generator.suggest_locator_from_html(html)
        
        return jsonify({
            'recommended_locators': result['recommended_locators'],
            'ai_suggestion': result['ai_suggestion'],
            'element_analysis': result['element_analysis']
        }), 200
        
    except Exception as e:
        logging.error(f"Error suggesting locator: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest-action', methods=['POST'])
def suggest_action():
    """
    Suggest action for element type.
    
    Request JSON:
    {
        "element_type": "input",
        "context": "login form"
    }
    """
    try:
        data = request.get_json()
        
        element_type = data.get('element_type', '')
        context = data.get('context', '')
        
        prompt = f"element_type: {element_type}\ncontext: {context}\nrecommended_action:"
        
        generated = generator.generate_from_prompt(prompt, max_tokens=20, temperature=0.3)
        
        # Extract action
        actions = []
        keywords = ['click', 'sendKeys', 'select', 'clear', 'submit', 'getText']
        for keyword in keywords:
            if keyword in generated:
                actions.append(keyword)
        
        return jsonify({
            'element_type': element_type,
            'suggested_actions': actions,
            'generation': generated
        }), 200
        
    except Exception as e:
        logging.error(f"Error suggesting action: {str(e)}")
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    print("\n" + "="*60)
    print("🚀 Selenium SLM API Server")
    print("="*60)
    print("🌐 Web Interface:")
    print("  http://localhost:5000")
    print("\nAPI Endpoints:")
    print("  GET  /health          - Health check")
    print("  POST /generate        - Generate code from prompt")
    print("  POST /suggest-locator - Suggest optimal locator")
    print("  POST /suggest-action  - Suggest action for element")
    print("="*60 + "\n")
    
    app.run(host='0.0.0.0', port=5000, debug=False)
