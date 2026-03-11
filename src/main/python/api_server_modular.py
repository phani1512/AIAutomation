"""
REST API server for Selenium SLM inference - Main entry point (Modular).
Provides HTTP endpoints for code generation from any client.
"""
import sys
import os
import io
import time
import logging
import traceback
import importlib

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

# Don't import inference_improved at top level - will be loaded fresh in get_generator()

from browser_executor import BrowserExecutor

# Import modular handlers
import auth_handler
import recorder_handler
import code_generator
import browser_handler
import test_executor
from url_monitor import URLMonitor
# Use optimized semantic analyzer for better performance
from semantic_analyzer_optimized import get_analyzer

# FORCE RELOAD screenshot modules to pick up code changes
import screenshot_handler_enhanced
import visual_element_detector
import multimodal_generator
importlib.reload(visual_element_detector)
importlib.reload(multimodal_generator)
importlib.reload(screenshot_handler_enhanced)
logging.info("[INIT] Reloaded screenshot modules to pick up latest code changes")

from screenshot_handler_enhanced import screenshot_bp

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO)

# Register screenshot blueprint for multi-modal AI
app.register_blueprint(screenshot_bp)

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Serve static web files
WEB_DIR = os.path.join(PROJECT_ROOT, 'src', 'web')

# Initialize improved model once at startup
MODEL_PATH = os.path.join(PROJECT_ROOT, 'selenium_ngram_model.pkl')
generator = None  # Lazy loading

# Initialize browser executor
browser_executor = None

# Initialize URL monitor
url_monitor = URLMonitor(WEB_DIR)

# Generate unique server instance ID to invalidate old sessions
SERVER_INSTANCE_ID = os.urandom(16).hex()

print(f"[INIT] Server started fresh - recorded_sessions cleared (count: {len(recorder_handler.recorded_sessions)})")
print(f"[INIT] Server Instance ID: {SERVER_INSTANCE_ID}")
print(f"[INIT] All previous auth sessions invalidated")

# Clear all authentication sessions on server restart
auth_handler.clear_all_sessions()

def get_generator():
    """Get or initialize the generator instance (cached for performance)"""
    global generator
    
    if generator is None:
        import inference_improved
        print(f"[INIT] Loading AI model for first time...", flush=True)
        generator = inference_improved.ImprovedSeleniumGenerator(MODEL_PATH, silent=True)
        print(f"[INIT] AI model loaded - Version: {generator.version}", flush=True)
        sys.stdout.flush()
    
    return generator

# ==================== Web Interface ====================

@app.route('/', methods=['GET'])
def index():
    """Serve the web interface"""
    timestamp = str(int(time.time()))
    print(f"[DEBUG] Index route called with timestamp={timestamp}")
    try:
        html_path = os.path.join(WEB_DIR, 'index-new.html')  # Serve index-new.html
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Inject timestamp to bypass cache - multiple injection points
        html_content = html_content.replace(
            '<title>🤖 AI Test Automation Studio v3.0</title>',
            f'<title>🤖 AI Test Automation Studio [MODULAR-{timestamp}]</title>'
        )
        # Also inject timestamp as meta tag and data attribute
        html_content = html_content.replace(
            '<head>',
            f'<head><meta name="cache-buster" content="{timestamp}"><meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">'
        )
        html_content = html_content.replace(
            '<body',
            f'<body data-server-version="modular-{timestamp}" data-timestamp="{timestamp}" data-server-instance="{SERVER_INSTANCE_ID}"'
        )
        
        # Inject script to clear localStorage/sessionStorage if server restarted
        clear_auth_script = f"""
        <script>
            // Clear auth if server instance changed
            const currentInstance = '{SERVER_INSTANCE_ID}';
            const storedInstance = localStorage.getItem('server_instance_id');
            if (storedInstance && storedInstance !== currentInstance) {{
                console.log('[AUTH] Server restarted - clearing authentication');
                localStorage.clear();
                sessionStorage.clear();
                document.cookie.split(";").forEach(c => {{
                    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                }});
                window.location.reload(true);
            }}
            localStorage.setItem('server_instance_id', currentInstance);
        </script>
        """
        if '</head>' in html_content:
            html_content = html_content.replace('</head>', f'{clear_auth_script}</head>')
        
        response = make_response(html_content)
        response.headers['Content-Type'] = 'text/html; charset=utf-8'
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate, max-age=0, private'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        response.headers['X-Timestamp'] = timestamp
        response.headers['X-Server-Version'] = 'modular'
        response.headers['X-Server-Instance'] = SERVER_INSTANCE_ID
        # Additional cache-busting headers
        response.headers['Last-Modified'] = timestamp
        response.headers['ETag'] = f'"modular-{timestamp}"'
        response.headers['Clear-Site-Data'] = '"cache", "cookies", "storage"'
        return response
    except Exception as e:
        print(f"[ERROR] Failed to serve index.html: {e}")
        traceback.print_exc()
        return f"Error: {e}", 500

@app.route('/screenshot-generator', methods=['GET'])
def screenshot_generator_ui():
    """Serve the multi-modal screenshot-based test generator UI"""
    try:
        resources_dir = os.path.join(PROJECT_ROOT, 'src', 'main', 'resources', 'web')
        response = send_from_directory(resources_dir, 'screenshot-generator.html')
        response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
        response.headers['Pragma'] = 'no-cache'
        response.headers['Expires'] = '0'
        return response
    except Exception as e:
        print(f"[ERROR] Failed to serve screenshot-generator.html: {e}")
        return f"Error: {e}", 500

@app.route('/web/<path:filename>', methods=['GET'])
def web_files(filename):
    """Serve web assets with cache busting"""
    response = send_from_directory(WEB_DIR, filename)
    # Add cache control headers for all static files
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'
    return response

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint."""
    return jsonify({
        'status': 'healthy', 
        'model': 'loaded',
        'version': '3.0-modular-UPDATED',
        'server': 'api_server_modular.py',
        'sessions': len(recorder_handler.recorded_sessions),
        'timestamp': int(time.time())
    }), 200

@app.route('/api/version', methods=['GET'])
def api_version():
    """API version endpoint to check which server is running."""
    return jsonify({
        'server': 'api_server_modular.py',
        'version': '3.0-modular',
        'status': 'running',
        'modules': [
            'auth_handler',
            'recorder_handler', 
            'code_generator',
            'browser_handler',
            'test_executor',
            'url_monitor'
        ],
        'timestamp': int(time.time())
    }), 200

# ==================== Authentication Endpoints ====================

@app.route('/auth/register', methods=['POST'])
def register():
    return auth_handler.register()

@app.route('/auth/login', methods=['POST'])
def login():
    return auth_handler.login()

@app.route('/auth/logout', methods=['POST'])
def logout():
    return auth_handler.logout()

@app.route('/auth/check', methods=['GET'])
def check_auth():
    return auth_handler.check_auth()

@app.route('/auth/profile', methods=['GET'])
def get_profile():
    return auth_handler.get_profile()

# ==================== Code Generation Endpoints ====================

@app.route('/generate', methods=['POST'])
def generate_code():
    """Generate Selenium code from prompt with improved cleaning."""
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        max_tokens = data.get('max_tokens', 30)
        temperature = data.get('temperature', 0.3)
        execute = data.get('execute', False)
        url = data.get('url', '')
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        print(f"[ENDPOINT DEBUG] /generate called with prompt: {prompt[:50]}...", flush=True)
        sys.stdout.flush()
        gen = get_generator()
        print(f"[ENDPOINT DEBUG] Generator obtained, calling generate_clean...", flush=True)
        generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature)
        print(f"[ENDPOINT DEBUG] Generated: {generated[:100]}...", flush=True)
        
        response = {
            'prompt': prompt,
            'generated': generated,
            'tokens_generated': len(generated.split())
        }
        
        print(f"[DEBUG /generate] execute={execute}, url='{url}'", flush=True)
        
        if execute:
            global browser_executor
            print("[DEBUG /generate] execute=True - entering execution branch", flush=True)
            if not browser_executor:
                browser_executor = BrowserExecutor()
                browser_executor.initialize_driver()
                print("[DEBUG /generate] Initialized new browser_executor", flush=True)
            else:
                print("[DEBUG /generate] Reusing existing browser_executor", flush=True)
            
            # Pass URL to execute_code - it will handle smart navigation
            print(f"[DEBUG /generate] Calling browser_executor.execute_code(url='{url}')", flush=True)
            execution_result = browser_executor.execute_code(generated, url if url else None)
            print(f"[DEBUG /generate] Execution completed: {execution_result.get('success', False)}", flush=True)
            response['execution'] = execution_result
        
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f"Error generating code: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/suggest-locator', methods=['POST'])
def suggest_locator():
    """Suggest optimal locator for element from HTML."""
    try:
        data = request.get_json()
        html = data.get('html', '')
        
        if not html:
            return jsonify({'error': 'HTML is required'}), 400
        
        gen = get_generator()
        result = gen.suggest_locator_from_html(html)
        
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
    """Suggest action for element type."""
    try:
        data = request.get_json()
        element_type = data.get('element_type', 'button')
        context = data.get('context', '')
        
        gen = get_generator()
        result = gen.suggest_action(element_type, context)
        
        return jsonify({
            'element_type': result['element_type'],
            'recommended_actions': result['recommended_actions'],
            'ai_generated_code': result['ai_generated_code'],
            'context': result['context']
        }), 200
        
    except Exception as e:
        logging.error(f"Error suggesting action: {str(e)}")
        return jsonify({'error': str(e)}), 500

# ==================== Browser Control Endpoints ====================

@app.route('/browser/initialize', methods=['POST'])
def initialize_browser():
    """Initialize browser for execution."""
    global browser_executor
    
    try:
        data = request.get_json() or {}
        browser = data.get('browser', 'chrome')
        headless = data.get('headless', False)
        
        if not browser_executor:
            browser_executor = BrowserExecutor()
        
        success = browser_executor.initialize_driver(browser, headless)
        
        return jsonify({
            'success': success,
            'browser': browser,
            'headless': headless,
            'message': f'Browser initialized successfully' if success else 'Failed to initialize browser'
        }), 200 if success else 500
        
    except Exception as e:
        logging.error(f"Error initializing browser: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/browser/execute', methods=['POST'])
def execute_in_browser():
    global browser_executor
    
    # Initialize browser if needed
    if not browser_executor:
        browser_executor = BrowserExecutor()
        browser_executor.initialize_driver()
        logging.info("[SERVER] Initialized new browser executor for /browser/execute")
    
    # Execute the request
    result_response = browser_handler.execute_in_browser(browser_executor, BrowserExecutor)
    
    # Check if a new browser was created and update our global reference
    new_executor = browser_handler.get_last_browser_executor()
    if new_executor and new_executor != browser_executor:
        browser_executor = new_executor
        logging.info("[SERVER] Updated global browser_executor reference")
    
    return result_response

@app.route('/browser/info', methods=['GET'])
def get_browser_info():
    return browser_handler.get_browser_info(browser_executor)

@app.route('/browser/screenshot', methods=['POST'])
def take_screenshot():
    return browser_handler.take_screenshot(browser_executor)

@app.route('/browser/close', methods=['POST'])
def close_browser():
    global browser_executor
    result = browser_handler.close_browser(browser_executor)
    browser_executor = None
    return result

@app.route('/browser/focus', methods=['POST'])
def browser_focus():
    """Bring browser window to front."""
    global browser_executor
    if not browser_executor or not browser_executor.driver:
        return jsonify({'success': False, 'error': 'Browser not initialized'}), 400
    
    result = browser_executor.focus_window()
    if 'error' in result:
        return jsonify({'success': False, 'error': result['error']}), 500
    return jsonify(result)

# ==================== Recorder Endpoints ====================

@app.route('/recorder/start', methods=['POST'])
def start_recording():
    # Don't initialize browser here - web UI will call /browser/initialize
    # Just start the recording session
    return recorder_handler.start_recording()

@app.route('/recorder/navigate', methods=['POST'])
def navigate_and_inject():
    global browser_executor
    
    logging.info(f"[NAVIGATE] Request received. Browser executor status: {browser_executor is not None}")
    
    # Ensure browser is initialized
    if not browser_executor:
        logging.warning("[RECORDER] Browser not initialized, creating new instance")
        browser_executor = BrowserExecutor()
        browser_executor.initialize_driver('chrome', False)
        logging.info(f"[RECORDER] Browser initialized. Driver status: {browser_executor.driver is not None}")
    
    # Verify browser has driver
    if not hasattr(browser_executor, 'driver') or not browser_executor.driver:
        logging.error("[RECORDER] Browser driver is None, reinitializing")
        browser_executor = BrowserExecutor()
        browser_executor.initialize_driver('chrome', False)
        logging.info(f"[RECORDER] Browser reinitialized. Driver status: {browser_executor.driver is not None}")
    
    logging.info(f"[NAVIGATE] Passing browser_executor to handler: {browser_executor is not None}")
    url_monitor.set_browser(browser_executor)
    url_monitor.set_active_session(recorder_handler.active_session_id)
    
    return browser_handler.navigate_and_inject(browser_executor, WEB_DIR, url_monitor)

@app.route('/recorder/record-action', methods=['POST'])
def record_action():
    gen = get_generator()
    return recorder_handler.record_action(gen)

@app.route('/recorder/stop', methods=['POST'])
def stop_recording():
    global browser_executor
    return recorder_handler.stop_recording(browser_executor, url_monitor)

@app.route('/recorder/new-test', methods=['POST'])
def start_new_test():
    global browser_executor
    url_monitor.set_browser(browser_executor)
    return browser_handler.start_new_test(browser_executor, WEB_DIR, url_monitor, recorder_handler)

@app.route('/recorder/generate-test', methods=['POST'])
def generate_test_code():
    return code_generator.generate_test_code(recorder_handler.recorded_sessions)

@app.route('/recorder/update-test-code', methods=['POST'])
def update_test_code():
    return code_generator.update_test_code(recorder_handler.recorded_sessions)

@app.route('/recorder/sessions', methods=['GET'])
def get_sessions():
    return recorder_handler.get_sessions()

@app.route('/recorder/session/<session_id>', methods=['GET'])
def get_session_details(session_id):
    return recorder_handler.get_session_details(session_id)

@app.route('/recorder/browser-status/<session_id>', methods=['GET'])
def get_browser_status(session_id):
    """Get live browser status for recorder monitoring."""
    try:
        # Verify session exists
        if session_id not in recorder_handler.recorded_sessions:
            return jsonify({
                'success': False,
                'error': 'Session not found'
            }), 404
        
        # Get browser state
        if not browser_executor or not browser_executor.driver:
            return jsonify({
                'success': False,
                'error': 'Browser not initialized'
            }), 503
        
        # Get current URL
        current_url = browser_executor.driver.current_url
        
        # Get tab count
        tab_count = len(browser_executor.driver.window_handles)
        
        # Get action count
        session = recorder_handler.recorded_sessions[session_id]
        action_count = len(session.get('actions', []))
        
        # Check if browser is visible (basic check - window exists)
        browser_visible = True  # Assume visible if driver exists
        try:
            browser_executor.driver.title  # Will fail if browser closed
        except:
            browser_visible = False
        
        return jsonify({
            'success': True,
            'current_url': current_url,
            'tab_count': tab_count,
            'action_count': action_count,
            'browser_visible': browser_visible
        })
    
    except Exception as e:
        logging.error(f"[BROWSER-STATUS] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recorder/focus-browser', methods=['POST'])
def focus_browser():
    """Bring browser window to front."""
    try:
        if not browser_executor or not browser_executor.driver:
            return jsonify({
                'success': False,
                'error': 'Browser not initialized'
            }), 503
        
        # Switch to current window and maximize
        current_handle = browser_executor.driver.current_window_handle
        browser_executor.driver.switch_to.window(current_handle)
        browser_executor.driver.maximize_window()
        
        logging.info("[BROWSER-FOCUS] Browser window brought to front")
        
        return jsonify({
            'success': True,
            'message': 'Browser window focused'
        })
    
    except Exception as e:
        logging.error(f"[BROWSER-FOCUS] Error: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@app.route('/recorder/save-generated-test', methods=['POST'])
def save_generated_test():
    """Save a generated test to the test suite - INLINE VERSION."""
    import time
    from flask import request, jsonify
    
    logging.info("[SAVE-TEST] Route handler called!")
    
    try:
        data = request.json
        logging.info(f"[SAVE-TEST] Received data keys: {data.keys()}")
        logging.info(f"[SAVE-TEST] Test name from request: {data.get('name')}")
        
        test_name = data.get('name', 'Generated_Test')
        module_name = data.get('module', 'SemanticAnalysis')
        code = data.get('code', '')
        language = data.get('language', 'python')
        
        if not code:
            return jsonify({'success': False, 'error': 'Code is required'}), 400
        
        # Create a new session for this generated test - use sanitized name
        sanitized_name = test_name.replace(' ', '_').replace('[', '').replace(']', '')
        session_id = f"generated_{int(time.time())}_{sanitized_name[:30]}"
        
        logging.info(f"[SAVE-TEST] Creating session with ID: {session_id}")
        logging.info(f"[SAVE-TEST] Test name will be: {test_name}")
        
        recorder_handler.recorded_sessions[session_id] = {
            'id': session_id,
            'name': test_name,
            'module': module_name,
            'url': 'Generated from Semantic Analysis',
            'actions': [],
            'generated_code': code,
            'edited_code': code,
            'language': language,
            'description': data.get('description', ''),
            'type': data.get('type', 'test'),
            'priority': data.get('priority', 'medium'),
            'steps': data.get('steps', []),
            'timestamp': time.time(),
            'created_at': time.time(),
            'active': False,
            'stopped': True,
            'source': 'semantic_analysis'
        }
        
        logging.info(f"[SAVE-TEST] Saved generated test: {test_name} to module: {module_name}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Test saved to {module_name} module'
        }), 200
        
    except Exception as e:
        logging.error(f"[SAVE-TEST] Error: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/recorder/clear-sessions', methods=['POST'])
def clear_sessions():
    return recorder_handler.clear_sessions()

@app.route('/recorder/delete-session', methods=['POST'])
def delete_session():
    return recorder_handler.delete_session()

# ==================== Semantic Analysis Endpoints ====================

@app.route('/semantic/analyze-intent', methods=['POST'])
def analyze_intent():
    """Analyze user prompt to understand test intent."""
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        analyzer = get_analyzer()
        analysis = analyzer.analyze_intent(prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/semantic/suggest-scenarios', methods=['POST'])
def suggest_scenarios():
    """Suggest test scenarios based on recorded actions."""
    try:
        data = request.json
        session_id = data.get('session_id', '')
        
        if not session_id or session_id not in recorder_handler.recorded_sessions:
            return jsonify({'success': False, 'error': 'Invalid session'}), 400
        
        session = recorder_handler.recorded_sessions[session_id]
        actions = session.get('actions', [])
        
        analyzer = get_analyzer()
        suggestions = analyzer.suggest_scenarios(actions, '')
        
        # Generate report
        intent_analysis = analyzer.analyze_intent(session.get('name', ''))
        report = analyzer.generate_test_report(intent_analysis, suggestions)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'report': report,
            'intent': intent_analysis
        }), 200
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
@app.route('/semantic/cache-stats', methods=['GET'])
def semantic_cache_stats():
    """Get semantic analyzer cache statistics."""
    try:
        analyzer = get_analyzer()
        cache_info = analyzer.get_cache_info()
        return jsonify({
            'success': True,
            'cache': cache_info
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/semantic/clear-cache', methods=['POST'])
def semantic_clear_cache():
    """Clear semantic analyzer cache."""
    try:
        analyzer = get_analyzer()
        analyzer.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
# ==================== Test Execution Endpoints ====================

@app.route('/recorder/execute-test', methods=['POST'])
def execute_test():
    return test_executor.execute_test(BrowserExecutor, recorder_handler.recorded_sessions)

@app.route('/recorder/execute-suite', methods=['POST'])
def execute_suite():
    """Execute all test cases in the suite."""
    return test_executor.execute_test_suite(BrowserExecutor, recorder_handler.recorded_sessions)

# ==================== Server Startup ====================

if __name__ == '__main__':
    from waitress import serve
    
    # Model will be loaded lazily on first request via get_generator()
    print("[SERVER] AI model will be loaded on first request...")
    print()
    
    print("="*60)
    print("[SERVER] Selenium SLM API Server (Modular)")
    print("="*60)
    print("[WEB] Interface: http://localhost:5002")
    print("[WEB] Screenshot AI: http://localhost:5002/screenshot-generator")
    print("\n[API] Endpoints:")
    print("  GET  /health              - Health check")
    print("  POST /generate            - Generate code")
    print("  POST /suggest-locator     - Suggest locator")
    print("  POST /suggest-action      - Suggest action")
    print("\n[BROWSER] Control:")
    print("  POST /browser/initialize  - Initialize")
    print("  POST /browser/execute     - Execute code")
    print("  POST /browser/close       - Close")
    print("\n[RECORDER] Actions:")
    print("  POST /recorder/start      - Start session")
    print("  POST /recorder/navigate   - Navigate & inject script")
    print("  POST /recorder/record-action - Record")
    print("  POST /recorder/stop       - Stop (keeps browser open)")
    print("  POST /recorder/new-test   - Start new test in same browser")
    print("  POST /recorder/generate-test - Generate test")
    print("  POST /recorder/save-generated-test - Save AI generated test")
    print("  GET  /recorder/sessions   - List sessions")
    print("\n[SEMANTIC] Analysis:")
    print("  POST /semantic/analyze-intent    - Analyze test intent")
    print("  POST /semantic/suggest-scenarios - Suggest test scenarios")
    print("  GET  /semantic/cache-stats       - View cache statistics")
    print("  POST /semantic/clear-cache       - Clear cache")
    print("\n[SCREENSHOT] Multi-modal AI:")
    print("  POST /screenshot/analyze        - Detect elements from screenshot")
    print("  POST /screenshot/generate-code  - Generate test from screenshot")
    print("  POST /screenshot/annotate       - Annotate screenshot with elements")
    print("\n[TEST SUITE] Execution:")
    print("  POST /recorder/execute-test - Execute single test")
    print("  POST /recorder/delete-session - Delete specific test case")
    print("  POST /recorder/clear-sessions - Clear all test cases")
    print("="*60 + "\n")
    
    print("[SERVER] Starting production server on http://localhost:5002")
    print("[SERVER] Press CTRL+C to quit\n")
    sys.stdout.flush()
    
    try:
        serve(app, host='0.0.0.0', port=5002, threads=6, channel_timeout=120)
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}")
        traceback.print_exc()
