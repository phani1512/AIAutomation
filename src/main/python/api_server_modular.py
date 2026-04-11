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
import warnings
from datetime import datetime

# Suppress urllib3 connection pool warnings
warnings.filterwarnings('ignore', message='Connection pool is full, discarding connection')

# Configure UTF-8 encoding for Windows console
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Add current directory to Python path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from flask import Flask, request, jsonify, send_from_directory, make_response
from flask_cors import CORS

# Don't import inference_improved at top level - will be loaded fresh in get_generator()

from browser.browser_executor import BrowserExecutor

# Import modular handlers
import auth_handler
from recorder import recorder_handler
from generators import code_generator
from browser import browser_handler
from test_management import test_executor
from test_management import test_suite_handler
from browser.url_monitor import URLMonitor
# Use ENHANCED semantic analyzer for 80%+ confidence
from semantic_analysis.semantic_analyzer_enhanced import get_analyzer

# ML-POWERED: Import ML semantic analyzer (falls back to rule-based if models not available)
try:
    from ml_models.ml_semantic_analyzer import MLSemanticAnalyzer
    from ml_models.feedback_collector import FeedbackCollector, create_feedback_routes
    from ml_models.auto_retrainer import get_on_demand_trainer
    from ml_models.test_case_generator import get_test_case_generator
    ml_semantic_analyzer = MLSemanticAnalyzer()
    feedback_collector = FeedbackCollector()
    on_demand_trainer = get_on_demand_trainer()
    test_case_generator = get_test_case_generator()
    ML_MODE_AVAILABLE = True
    logging.info("[INIT] ✓ ML Semantic Analyzer loaded successfully")
    logging.info("[INIT] ✓ On-demand trainer initialized")
    logging.info("[INIT] ✓ Test case generator initialized")
except Exception as e:
    ml_semantic_analyzer = None
    feedback_collector = None
    on_demand_trainer = None
    test_case_generator = None
    ML_MODE_AVAILABLE = False
    logging.warning(f"[INIT] ML models not available, using rule-based analyzer: {e}")

# FORCE RELOAD screenshot modules to pick up code changes
from ai_vision import screenshot_handler_enhanced
from ai_vision import visual_element_detector
from generators import multimodal_generator
importlib.reload(visual_element_detector)
importlib.reload(multimodal_generator)
importlib.reload(screenshot_handler_enhanced)
logging.info("[INIT] Reloaded screenshot modules to pick up latest code changes")

from ai_vision.screenshot_handler_enhanced import screenshot_bp

# Import Phase 0 modules for multi-prompt test suite builder
from test_management.test_session_manager import get_session_manager
from test_management.test_case_builder import get_test_case_builder
from test_management.test_suite_runner import get_test_runner
from nlp.smart_prompt_handler import SmartPromptHandler

# BACKWARD COMPATIBILITY: Add module aliases for old-style imports in generated code
# This allows generated code with "from browser_executor import BrowserExecutor" to work
sys.modules['browser_executor'] = sys.modules['browser.browser_executor']
sys.modules['test_case_builder'] = sys.modules['test_management.test_case_builder']
sys.modules['test_executor'] = sys.modules['test_management.test_executor']
sys.modules['test_suite_handler'] = sys.modules['test_management.test_suite_handler']
sys.modules['smart_prompt_handler'] = sys.modules['nlp.smart_prompt_handler']
sys.modules['recorder_handler'] = sys.modules['recorder.recorder_handler']
sys.modules['inference_improved'] = sys.modules.get('core.inference_improved', type('ModuleNotLoaded', (), {})())
sys.modules['intelligent_prompt_matcher'] = sys.modules['semantic_analysis.intelligent_prompt_matcher']
sys.modules['code_generator'] = sys.modules['generators.code_generator']
sys.modules['multimodal_generator'] = sys.modules['generators.multimodal_generator']

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'
app.config['SESSION_COOKIE_SAMESITE'] = 'Lax'
app.config['SESSION_COOKIE_SECURE'] = False
CORS(app, resources={r"/*": {"origins": "*"}})
logging.basicConfig(level=logging.INFO)

# Reduce waitress logging verbosity
logging.getLogger('waitress').setLevel(logging.ERROR)

# Register screenshot blueprint for multi-modal AI
app.register_blueprint(screenshot_bp)

# Get the project root directory
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

# Serve static web files
WEB_DIR = os.path.join(PROJECT_ROOT, 'src', 'web')

# Initialize improved model once at startup
MODEL_PATH = os.path.join(PROJECT_ROOT, 'resources', 'ml_data', 'models', 'selenium_ngram_model.pkl')
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
        from core import inference_improved
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
            // Clear auth if server instance changed - FIX: Set new ID BEFORE clearing to prevent loop
            const currentInstance = '{SERVER_INSTANCE_ID}';
            const storedInstance = localStorage.getItem('server_instance_id');
            if (storedInstance && storedInstance !== currentInstance) {{
                console.log('[AUTH] Server restarted - clearing authentication');
                // Set new instance ID FIRST to prevent reload loop
                localStorage.setItem('server_instance_id', currentInstance);
                // Now clear other auth data
                const instanceId = localStorage.getItem('server_instance_id'); // Save it
                localStorage.clear();
                sessionStorage.clear();
                localStorage.setItem('server_instance_id', instanceId); // Restore it
                document.cookie.split(";").forEach(c => {{
                    document.cookie = c.replace(/^ +/, "").replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
                }});
                // Only reload ONCE
                if (!sessionStorage.getItem('auth_cleared')) {{
                    sessionStorage.setItem('auth_cleared', 'true');
                    window.location.reload(true);
                }}
            }} else {{
                localStorage.setItem('server_instance_id', currentInstance);
            }}
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
        resources_dir = os.path.join(WEB_DIR)  # Already points to PROJECT_ROOT/src/web
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

@app.route('/screenshots/<path:filepath>')
def serve_screenshot(filepath):
    """Serve screenshot files from screenshots directory."""
    try:
        screenshots_dir = os.path.join(os.getcwd(), 'screenshots')
        return send_from_directory(screenshots_dir, filepath)
    except Exception as e:
        logging.error(f"Error serving screenshot: {str(e)}")
        return jsonify({'error': 'Screenshot not found'}), 404

@app.route('/execution_results/<path:filepath>')
def serve_execution_results(filepath):
    """Serve files from execution_results directory (screenshots, reports, etc)."""
    try:
        execution_results_dir = os.path.join(os.getcwd(), 'execution_results')
        return send_from_directory(execution_results_dir, filepath)
    except Exception as e:
        logging.error(f"Error serving execution result file: {str(e)}")
        return jsonify({'error': 'File not found'}), 404

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
        language = data.get('language', 'python')  # Default to Python for Test Builder
        max_tokens = data.get('max_tokens', 30)
        temperature = data.get('temperature', 0.3)
        execute = data.get('execute', False)
        url = data.get('url', '')
        
        # Auto-detect verification prompts and use simple dataset code
        prompt_lower = prompt.lower()
        is_verification = any(verb in prompt_lower for verb in ['verify', 'assert', 'validate', 'confirm']) and \
                         any(target in prompt_lower for target in ['title', 'text', 'url', 'value'])
        
        print(f"[VERIFY-DEBUG] prompt='{prompt}', is_verification={is_verification}", flush=True)
        sys.stdout.flush()
        
        # For verification prompts, use simple mode by default
        with_fallbacks = data.get('with_fallbacks', not is_verification)
        max_fallbacks = data.get('max_fallbacks', 3)
        compact_mode = data.get('compact_mode', False)  # NEW: Compact self-healing code (70% smaller)
        comprehensive_mode = data.get('comprehensive_mode', not is_verification)  # Respect frontend comprehensive_mode setting
        
        print(f"[VERIFY-DEBUG] with_fallbacks={with_fallbacks}, max_fallbacks={max_fallbacks}, compact_mode={compact_mode}", flush=True)
        sys.stdout.flush()
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        print(f"[ENDPOINT DEBUG] /generate called with prompt: {prompt[:50]}..., language: {language}, with_fallbacks: {with_fallbacks}", flush=True)
        sys.stdout.flush()
        gen = get_generator()
        
        # **PRIORITY: Check if dataset has fallback_selectors first**
        # This prioritizes curated dataset fallbacks over auto-generated ones
        debug_log = []
        try:
            # DEBUG: Write to file
            with open('debug_api_endpoint.txt', 'a', encoding='utf-8') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"API /generate called\n")
                f.write(f"Prompt: {prompt}\n")
                f.write(f"Language: {language}\n")
                f.write(f"Comprehensive mode: {comprehensive_mode}\n")
                f.write(f"With fallbacks: {with_fallbacks}\n")
            
            dataset_match = gen._find_dataset_match(prompt, return_alternatives=False)
            has_dataset_fallbacks = (dataset_match and 
                                    dataset_match.get('fallback_selectors') and 
                                    len(dataset_match.get('fallback_selectors', [])) > 1)
            
            # DEBUG: Write result
            with open('debug_api_endpoint.txt', 'a', encoding='utf-8') as f:
                f.write(f"Dataset match found: {dataset_match is not None}\n")
                f.write(f"Has dataset fallbacks: {has_dataset_fallbacks}\n")
                if has_dataset_fallbacks:
                    f.write(f"Fallback count: {len(dataset_match.get('fallback_selectors', []))}\n")
            
            debug_log.append(f"[DATASET CHECK] Match: {dataset_match is not None}")
            if dataset_match:
                debug_log.append(f"[DATASET CHECK] Fallbacks count: {len(dataset_match.get('fallback_selectors', []))}")
                debug_log.append(f"[DATASET CHECK] Has fallbacks (>1): {has_dataset_fallbacks}")
            
            # Write debug to file
            with open('dataset_check_debug.txt', 'a') as f:
                f.write(f"\n{'='*80}\n")
                f.write(f"Prompt: {prompt}\n")
                f.write('\n'.join(debug_log) + '\n')
                
            print(f"[DATASET CHECK] Match: {dataset_match is not None}, Has: {has_dataset_fallbacks}", flush=True)
        except Exception as e:
            debug_log.append(f"[DATASET CHECK ERROR] {e}")
            with open('dataset_check_debug.txt', 'a') as f:
                f.write(f"\nERROR: {e}\n")
            print(f"[DATASET CHECK ERROR] {e}", flush=True)
            has_dataset_fallbacks = False
        
        if has_dataset_fallbacks:
            # DEBUG
            with open('debug_api_endpoint.txt', 'a', encoding='utf-8') as f:
                f.write(f"TAKING PATH: has_dataset_fallbacks (line 340)\n")
                f.write(f"Calling gen.generate_clean() with ignore_fallbacks={(not with_fallbacks)}\n")
            
            print(f"[DATASET FALLBACKS] Found {len(dataset_match.get('fallback_selectors', []))} curated fallback selectors in dataset", flush=True)
            if with_fallbacks:
                print(f"[DATASET FALLBACKS] with_fallbacks=True, using dataset fallbacks", flush=True)
            else:
                print(f"[DATASET FALLBACKS] with_fallbacks=False, ignoring dataset fallbacks (will use primary codeonly)", flush=True)
            # Use dataset fallbacks via generate_clean (comprehensive_mode already set from request)
            generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature, language=language, comprehensive_mode=comprehensive_mode, ignore_fallbacks=(not with_fallbacks), compact_mode=compact_mode)
            
            # Get alternatives from HYBRID mode for UI suggestions (even when using dataset fallbacks)
            raw_alternatives = gen.get_last_alternatives()
            
            # DEBUG: Write to file to see what we got
            with open('api_alternatives_debug.log', 'w', encoding='utf-8') as f:
                f.write(f"=== FALLBACKS PATH (line 340-348) ===\n")
                f.write(f"Called gen.get_last_alternatives() and got {len(raw_alternatives)} alternatives:\n\n")
                for i, alt in enumerate(raw_alternatives, 1):
                    f.write(f"{i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')}\n")
                    f.write(f"   Category: {alt.get('category', 'N/A')}\n")
                    f.write(f"   Code (first 80 chars): {alt.get('code', '')[:80]}\n\n")
            
            print(f"[ALTERNATIVES DEBUG] Called get_last_alternatives()", flush=True)
            print(f"[ALTERNATIVES DEBUG] Type: {type(raw_alternatives)}", flush=True)
            print(f"[ALTERNATIVES DEBUG] Length: {len(raw_alternatives)}", flush=True)
            print(f"[ALTERNATIVES DEBUG] Content: {raw_alternatives[:3] if raw_alternatives else '[]'}", flush=True)
            print(f"[ALTERNATIVES] Found {len(raw_alternatives)} alternatives from generator", flush=True)
            
            # NEW APPROACH: Generate alternatives based on DIFFERENT fallback selectors
            # This shows users multiple selector strategies they can choose from
            alternatives = []
            
            if with_fallbacks and dataset_match and dataset_match.get('fallback_selectors'):
                fallback_selectors = dataset_match.get('fallback_selectors', [])
                prompt_variations = dataset_match.get('metadata', {}).get('prompt_variations', [])
                print(f"[ALTERNATIVES] Generating {len(fallback_selectors)} selector-based alternatives", flush=True)
                
                # Generate one alternative per fallback selector (showing different selector approaches)
                from core.fallback_strategy import FallbackStrategyGenerator
                strategy_gen = FallbackStrategyGenerator()
                
                # Determine action type from category or code
                category = dataset_match.get('category', 'click').lower()
                if 'click' in category or 'button' in category:
                    action_type = 'click'
                elif 'sendkeys' in category or 'input' in category or 'enter' in category or 'type' in category:
                    action_type = 'sendKeys'
                elif 'dropdown' in category or 'select' in category:
                    action_type = 'select'
                else:
                    action_type = 'click'
                
                for idx, selector in enumerate(fallback_selectors[:6]):  # Show up to 6 selector alternatives
                    try:
                        # Generate simple code using just this single selector
                        selector_code = strategy_gen.generate_code_with_fallbacks(
                            prompt=f"{prompt} (using {selector})",
                            fallback_selectors=[selector],  # Only this one selector
                            action_type=action_type,
                            language=language,
                            comprehensive_mode=False,  # Simple code, not comprehensive
                            compact_mode=True  # Compact single-selector code
                        )
                        
                        alternatives.append({
                            'prompt': f"Option {idx + 1}: Using selector '{selector}'",
                            'score': 1.0 - (idx * 0.05),  # Decreasing score for each option
                            'code': selector_code,
                            'xpath': selector,
                            'category': category,
                            'prompt_variations': prompt_variations,  # Share variations across all
                            'strategy': 'selector_fallback'
                        })
                    except Exception as e:
                        print(f"[ALTERNATIVES] Failed to generate code for selector {selector}: {e}", flush=True)
                        continue
            else:
                # Fallback to original alternative prompts approach if no fallback selectors
                for alt in raw_alternatives[:5]:
                    alt_code = alt.get('code', '')
                    if alt_code and language != 'java':
                        alt_code = gen._convert_code_to_language(alt_code, language)
                    
                    alternatives.append({
                        'prompt': alt.get('prompt', ''),
                        'score': alt.get('score', 0.0),
                        'code': alt_code,
                        'xpath': alt.get('xpath', ''),
                        'category': alt.get('category', ''),
                        'prompt_variations': alt.get('prompt_variations', []),
                        'strategy': 'dataset'
                    })
        elif with_fallbacks:
            # DEBUG
            with open('debug_api_endpoint.txt', 'a', encoding='utf-8') as f:
                f.write(f"TAKING PATH: with_fallbacks (line 369)\n")
            
            # Check if fallback code generation is requested (if no dataset fallbacks)
            print(f"[FALLBACK MODE] No dataset fallbacks, generating with {max_fallbacks} fallback alternatives", flush=True)
            from generators.fallback_code_generator import FallbackCodeGenerator
            from semantic_analysis.intelligent_prompt_matcher import get_matcher
            
            # Get matcher and find matches with fallbacks
            matcher = get_matcher()
            match_result = matcher.match_with_fallbacks(prompt, max_fallbacks=max_fallbacks)
            
            primary_match = match_result['primary']
            fallbacks = match_result['fallbacks']
            
            print(f"[FALLBACK MODE] Primary: {primary_match.get('strategy')} ({primary_match.get('confidence', 0):.2%})", flush=True)
            print(f"[FALLBACK MODE] Found {len(fallbacks)} fallback alternatives", flush=True)
            
            # Generate code with fallbacks
            if match_result['has_fallbacks'] and primary_match.get('code'):
                fallback_gen = FallbackCodeGenerator()
                
                # NEW: If compact_mode enabled, use fallback_strategy.py instead for 70% smaller code
                if compact_mode:
                    print(f"[COMPACT MODE] Using fallback_strategy generators for compact code", flush=True)
                    
                    # IMPORTANT: Use dataset matcher to find template with substituted selectors
                    # This works for ALL templates dynamically: button, tab, link, menu, file, search, etc.
                    # The dataset matcher will:
                    # 1. Check for template match first (via _find_template_match)
                    # 2. Extract parameter (e.g., "Beneficiaries" from "click Beneficiaries button")
                    # 3. Find template in dataset (e.g., "click {VALUE} button")
                    # 4. Substitute {VALUE} in all fallback_selectors
                    # 5. Return the template with substituted selectors
                    
                    # Check if primary_match already has fallback_selectors (from dataset template match)
                    if primary_match.get('fallback_selectors') and len(primary_match.get('fallback_selectors', [])) > 1:
                        # Template match found! Use the curated fallback_selectors from dataset
                        # These are already substituted with the extracted value by process_template_match()
                        selectors = primary_match['fallback_selectors'][:10]  # Top 10 selectors
                        print(f"[COMPACT MODE] Using {len(selectors)} template selectors from dataset (already substituted)", flush=True)
                    else:
                        # No template selectors - use XPath from matches
                        selectors = []
                        for match in [primary_match] + fallbacks:
                            xpath = match.get('xpath', '')
                            if xpath and xpath not in selectors:
                                selectors.append(xpath)
                        print(f"[COMPACT MODE] Using {len(selectors)} selectors from matched entries", flush=True)
                    
                    # Use fallback_strategy for compact generation
                    from core.fallback_strategy import FallbackStrategyGenerator
                    strategy_gen = FallbackStrategyGenerator()
                    
                    # Determine action type
                    code_lower = primary_match.get('code', '').lower()
                    if '.click()' in code_lower:
                        action_type = 'click'
                    elif '.sendkeys(' in code_lower or '.clear()' in code_lower:
                        action_type = 'sendKeys'
                    elif 'selectbyvisibletext' in code_lower or 'select' in code_lower:
                        action_type = 'select'
                    else:
                        action_type = 'click'  # fallback
                    
                    # Extract value for input/select actions (for data entry, not for template substitution)
                    def extract_value_from_prompt(prompt_text):
                        """Extract data value from prompts like 'enter VALUE in field' or 'type VALUE in'."""
                        import re
                        # Pattern: enter/type VALUE in/into field_name
                        patterns = [
                            r'(?:enter|type|input)\s+["\']?([^"\']+?)["\']?\s+(?:in|into)',
                            r'(?:select|choose)\s+["\']?([^"\']+?)["\']?\s+(?:from|in)',
                        ]
                        for pattern in patterns:
                            match = re.search(pattern, prompt_text, re.IGNORECASE)
                            if match:
                                return match.group(1).strip()
                        return None
                    
                    generated = strategy_gen.generate_code_with_fallbacks(
                        prompt=prompt,
                        fallback_selectors=selectors[:10],  # Top 10 selectors
                        action_type=action_type,
                        language=language,
                        comprehensive_mode=False,
                        value_extractor_func=extract_value_from_prompt,
                        compact_mode=True
                    )
                    print(f"[COMPACT MODE] Generated compact code with {len(selectors[:6])} fallback selectors", flush=True)
                else:
                    # Standard verbose fallback generation
                    generated = fallback_gen.generate_with_fallbacks(
                        primary_match,
                        fallbacks,
                        language=language,
                        max_fallbacks=max_fallbacks
                    )
                    print(f"[FALLBACK MODE] Generated self-healing code with {len(fallbacks)} fallback locators", flush=True)
            else:
                # No fallbacks available, use standard generation
                print(f"[FALLBACK MODE] No fallbacks available, using standard generation", flush=True)
                # Use comprehensive_mode from request (already set above)
                generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature, language=language, comprehensive_mode=comprehensive_mode)
            
            # Prepare alternatives for UI (showing which fallbacks are available)
            # IMPORTANT: Convert alternative code to target language!
            alternatives = []
            for fb in fallbacks:
                fb_code = fb.get('code', '')
                # Convert Java code to target language
                if fb_code and language != 'java':
                    fb_code = gen._convert_code_to_language(fb_code, language)
                
                alternatives.append({
                    'prompt': fb.get('matched_prompt', ''),
                    'score': fb.get('confidence', 0.0),
                    'code': fb_code,
                    'strategy': fb.get('strategy', 'unknown')
                })
        else:
            # DEBUG  
            with open('debug_api_endpoint.txt', 'a', encoding='utf-8') as f:
                f.write(f"TAKING PATH: else (standard generation, line 468)\n")
                f.write(f"Calling gen.generate_clean() with language={language}, comprehensive_mode={comprehensive_mode}\n")
            
            # Standard generation without fallbacks
            print(f"[ENDPOINT DEBUG] Generator obtained, calling generate_clean with language={language}, comprehensive_mode={comprehensive_mode}...", flush=True)
            #Use comprehensive_mode from request (already set above)
            if is_verification and not comprehensive_mode:
                print(f"[VERIFICATION DETECTED] Using simple dataset mode for: {prompt}", flush=True)
            generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature, language=language, comprehensive_mode=comprehensive_mode)
            
            # Get alternatives from HYBRID mode for UI suggestions
            raw_alternatives = gen.get_last_alternatives()
            print(f"[ENDPOINT DEBUG] Found {len(raw_alternatives)} alternatives from HYBRID mode", flush=True)
            
            # DEBUG: Log what we got
            with open('api_alternatives_debug.log', 'w', encoding='utf-8') as f:
                f.write(f"API got {len(raw_alternatives)} alternatives from gen.get_last_alternatives():\n")
                for i, alt in enumerate(raw_alternatives, 1):
                    f.write(f"  {i}. [{alt.get('score', 0):.1%}] {alt.get('prompt', 'N/A')} (category: {alt.get('category', 'N/A')})\n")
            
            # IMPORTANT: Convert alternative code to target language!
            alternatives = []
            for alt in raw_alternatives:
                alt_code = alt.get('code', '')
                # Convert Java code to target language
                if alt_code and language != 'java':
                    alt_code = gen._convert_code_to_language(alt_code, language)
                
                alternatives.append({
                    'prompt': alt.get('prompt', ''),
                    'score': alt.get('score', 0.0),
                    'code': alt_code,
                    'prompt_variations': alt.get('prompt_variations', []),  # Include prompt variations for UI
                    'strategy': alt.get('strategy', 'unknown')
                })
        
        print(f"[ENDPOINT DEBUG] ✅ Generated code length: {len(generated)} characters", flush=True)
        print(f"[ENDPOINT DEBUG] First 200 chars: {generated[:200]}...", flush=True)
        
        # **CRITICAL FIX**: FINAL SAFETY CHECK - Ensure code is in correct language
        # This catches ANY path that might have missed conversion
        if language != 'python':
            # Check if code is still in Python format
            if 'wait = WebDriverWait' in generated or '.send_keys(' in generated or 'EC.' in generated:
                print(f"[SAFETY CHECK] ⚠️ Generated code is still Python, converting to {language}", flush=True)
                generated = gen._convert_code_to_language(generated, language)
                print(f"[SAFETY CHECK] ✅ Converted to {language}: {generated[:150]}...", flush=True)
        
        response = {
            'prompt': prompt,
            'generated': generated,
            'code': generated,  # Also include as 'code' for consistency
            'alternatives': alternatives,  # NEW: Include alternatives for "Did you mean?" UI
            'has_fallbacks': with_fallbacks and len(alternatives) > 0,
            'fallback_count': len(alternatives) if with_fallbacks else 0,
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
    """Enhanced action suggestion with confidence scoring and test scenarios."""
    try:
        data = request.get_json()
        element_type = data.get('element_type', 'button')
        context = data.get('context', '')
        language = data.get('language', 'java')
        
        gen = get_generator()
        result = gen.suggest_action(element_type, context, language)
        
        # Return enhanced response with all new fields
        return jsonify({
            'element_type': result['element_type'],
            'context': result['context'],
            'confidence': result['confidence'],
            'confidence_level': result['confidence_level'],
            'recommended_actions': result['recommended_actions'],
            'top_actions': result['top_actions'],
            'test_scenarios': result['test_scenarios'],
            'code_samples': result['code_samples'],
            'ai_generated_code': result['ai_generated_code'],  # backward compatibility
            'context_hints': result['context_hints'],
            'total_actions': result['total_actions']
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
    # Generator needed for AI-suggested locators
    return recorder_handler.record_action(generator=get_generator())

@app.route('/recorder/stop', methods=['POST'])
def stop_recording():
    global browser_executor
    return recorder_handler.stop_recording(browser_executor, url_monitor)


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

@app.route('/recorder/rename-test/<test_case_id>', methods=['POST'])
def rename_recorder_test(test_case_id):
    """Rename a saved recorder test case."""
    return recorder_handler.rename_test(test_case_id)

@app.route('/recorder/save-test-case', methods=['POST'])
def save_test_case_to_disk():
    """
    Save recorded session as permanent test case to test_suites/ (single source of truth).
    """
    return recorder_handler.save_test_case_to_disk()

@app.route('/recorder/saved-tests', methods=['GET'])
def list_saved_recorder_tests():
    """
    List all saved recorder test cases from user folders.
    """
    return recorder_handler.list_saved_recorder_tests()

@app.route('/recorder/test/<test_case_id>', methods=['GET'])
def get_saved_recorder_test(test_case_id):
    """
    Load a specific saved recorder test with full details including actions.
    Used for data override modal and detailed test viewing.
    """
    session_data = recorder_handler.load_saved_test_from_disk(test_case_id)
    
    if session_data:
        return jsonify({
            'success': True,
            'session_data': session_data,
            'test_case_id': test_case_id
        }), 200
    else:
        return jsonify({
            'success': False,
            'error': 'Test case not found'
        }), 404

@app.route('/test-suite/execution-results/<test_case_id>', methods=['GET'])
def get_execution_results(test_case_id):
    """
    Get execution history/results for a specific test case.
    Returns list of execution results with screenshots for failed tests.
    """
    try:
        import glob
        import json
        
        # Search for execution results matching this test case
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))  # Already correct
        
        # Search in both recorder and builder results
        patterns = [
            os.path.join(project_root, 'execution_results', 'recorder', f'{test_case_id}_*.json'),
            os.path.join(project_root, 'execution_results', 'builder', f'{test_case_id}_*.json'),
            os.path.join(project_root, 'execution_results', 'recorder', f'*{test_case_id}*.json'),
            os.path.join(project_root, 'execution_results', 'builder', f'*{test_case_id}*.json')
        ]
        
        execution_results = []
        
        for pattern in patterns:
            for filepath in glob.glob(pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        result_data = json.load(f)
                        
                        # Add metadata
                        result_data['result_file'] = os.path.basename(filepath)
                        result_data['filepath'] = filepath
                        
                        execution_results.append(result_data)
                except Exception as e:
                    logging.error(f"Error reading execution result {filepath}: {e}")
                    continue
        
        # Sort by timestamp (newest first)
        execution_results.sort(
            key=lambda x: x.get('start_time', ''), 
            reverse=True
        )
        
        return jsonify({
            'success': True,
            'test_case_id': test_case_id,
            'execution_results': execution_results,
            'count': len(execution_results)
        }), 200
        
    except Exception as e:
        logging.error(f"Error fetching execution results: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

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
    """Suggest test scenarios based on saved test case."""
    try:
        logging.info("[SEMANTIC] ========== SUGGEST SCENARIOS START ==========")
        data = request.json
        test_case_id = data.get('test_case_id', '')
        logging.info(f"[SEMANTIC] Step 1: Got test_case_id={test_case_id}")
        
        if not test_case_id:
            return jsonify({'success': False, 'error': 'Test case ID is required'}), 400
        
        # Try to get test case from test builder first
        logging.info("[SEMANTIC] Step 2: Loading test case from builder...")
        builder = get_test_case_builder()
        test_case_obj = builder.load_test_case(test_case_id)
        logging.info(f"[SEMANTIC] Step 2 result: builder returned {type(test_case_obj)}")
        
        test_case = None
        if test_case_obj:
            # Convert TestCase object to dict
            test_case = test_case_obj.to_dict()
            logging.info(f"[SEMANTIC] Step 3: Converted to dict")
        else:
            # Try to load from recorder saved tests
            logging.info("[SEMANTIC] Step 3: Loading from recorder...")
            test_case = recorder_handler.load_saved_test_from_disk(test_case_id)
            logging.info(f"[SEMANTIC] Step 3 result: recorder returned {type(test_case)}")
        
        if not test_case:
            return jsonify({'success': False, 'error': 'Test case not found'}), 404
        
        # Extract actions for semantic analysis
        # Support multiple formats: steps (builder), actions (recorder), prompts (builder v2)
        actions = []
        test_name = test_case.get('name', 'Test Case')
        test_description = test_case.get('description', '')
        
        if 'actions' in test_case and test_case['actions']:
            # Recorder format: [{action, selector, value, ...}]
            actions = test_case['actions']
            logging.info(f"[SEMANTIC] Using {len(actions)} recorder actions")
            # DEBUG: Check for None values that might cause regex errors
            for i, action in enumerate(actions):
                if action.get('value') is None or action.get('value_') is None:
                    logging.debug(f"[SEMANTIC] Action {i} has None value: {action.get('action_type', 'unknown')}")
        elif 'steps' in test_case and test_case['steps']:
            # Builder format: [{prompt, code, type, ...}]
            # Convert steps to action-like structure for analyzer
            steps = test_case['steps']
            actions = []
            for step in steps:
                if isinstance(step, dict):
                    # Extract prompt and code if available
                    prompt_text = step.get('prompt', step.get('description', ''))
                    code_text = step.get('code', '')
                    actions.append({
                        'action': prompt_text,
                        'type': step.get('type', 'action'),
                        'code': code_text
                    })
                else:
                    # Simple string step
                    actions.append({
                        'action': str(step),
                        'type': 'action'
                    })
            logging.info(f"[SEMANTIC] Using {len(actions)} test builder steps")
        elif 'prompts' in test_case and test_case['prompts']:
            # Alternative builder format: prompts array
            prompts = test_case['prompts']
            actions = [{'action': p.get('prompt', ''), 'type': p.get('type', 'action')} 
                       for p in prompts]
            logging.info(f"[SEMANTIC] Using {len(actions)} test builder prompts")
        
        if not actions:
            logging.warning(f"[SEMANTIC] No actions found for test case {test_case_id}")
            return jsonify({
                'success': False, 
                'error': 'No test actions found. This test case appears to be empty.'
            }), 400
        
        # Get generated code if available (for better context)
        generated_code = ''
        if 'generated_code' in test_case:
            # Builder format - has code for multiple languages
            code_dict = test_case['generated_code']
            if isinstance(code_dict, dict):
                generated_code = code_dict.get('python', '') or code_dict.get('java', '') or code_dict.get('javascript', '')
        elif 'code' in test_case:
            # Some recorder tests have code field
            generated_code = test_case.get('code', '')
        
        # Build enhanced context for semantic analyzer
        context = {
            'test_name': test_name,
            'description': test_description,
            'actions': actions,
            'generated_code': generated_code,
            'url': test_case.get('url', ''),
            'tags': test_case.get('tags', []),
            'priority': test_case.get('priority', 'medium')
        }
        
        logging.info(f"[SEMANTIC] Step 7: Analyzing test case: {test_name}")
        logging.info(f"[SEMANTIC] Step 7 details: Actions={len(actions)}, Has code={len(generated_code) > 0}")
        logging.info(f"[SEMANTIC] Test formats supported: Recorder + Prompt-based Test Builder")
        
        # ====================================================================
        # INTELLIGENT TEST GENERATION - ML-First Approach
        # 
        # Priority Order:
        # 1. ML-Powered Analyzer (RandomForest model, higher accuracy)
        # 2. Rule-based Analyzer (fallback, consistent baseline)
        # 
        # Supports BOTH:
        # - Recorder format: {'action_type': 'click', 'value': '...'}
        # - Prompt-based Test Builder: {'action': '...', 'prompt': '...'}
        # ====================================================================
        
        suggestions = []
        ml_used = False
        
        # Try ML-powered analyzer first (BETTER test suggestions)
        if ML_MODE_AVAILABLE and ml_semantic_analyzer and ml_semantic_analyzer.model is not None:
            logging.info(f"[SEMANTIC] Step 8A: 🤖 Using ML-Powered Analyzer (RandomForest)")
            try:
                suggestions = ml_semantic_analyzer.suggest_scenarios(actions, context['url'], context)
                ml_used = True
                logging.info(f"[SEMANTIC] Step 8A result: ✓ ML generated {len(suggestions)} high-quality scenarios")
            except Exception as e:
                logging.error(f"[SEMANTIC] Step 8A ERROR in ML analyzer: {e}")
                logging.error(f"[SEMANTIC] Full traceback:", exc_info=True)  # ADDED: Full traceback
                logging.info(f"[SEMANTIC] Falling back to rule-based analyzer...")
        
        # Fallback to rule-based if ML failed or unavailable
        if not suggestions:
            logging.info(f"[SEMANTIC] Step 8B: Using Rule-based Analyzer (fallback)")
            try:
                analyzer = get_analyzer()
                suggestions = analyzer.suggest_scenarios(actions, context['url'], context)
                logging.info(f"[SEMANTIC] Step 8B result: ✓ Rule-based generated {len(suggestions)} scenarios")
            except Exception as e:
                logging.error(f"[SEMANTIC] Step 8B ERROR in rule-based analyzer: {e}", exc_info=True)
                # Return minimal error response instead of crashing
                suggestions = [{
                    'type': 'error',
                    'title': 'Test Scenario Generation Failed',
                    'description': 'Unable to generate test scenarios. Please check test case format.',
                    'priority': 'high',
                    'confidence': 0.0
                }]
        
        # Generate comprehensive report (optional, uses rule-based for intent analysis)
        logging.info("[SEMANTIC] Step 9: Generating comprehensive report...")
        report = None
        intent_analysis = None
        
        try:
            analyzer = get_analyzer()
            intent_analysis = analyzer.analyze_intent(f"{test_name} - {test_description}")
            report = analyzer.generate_test_report(intent_analysis, suggestions)
            logging.info("[SEMANTIC] Step 9: ✓ Report generated successfully")
        except Exception as e:
            logging.error(f"[SEMANTIC] Step 9 WARNING: Report generation failed (non-critical): {e}")
            # Continue without report - suggestions are more important
            report = {'summary': 'Report generation skipped', 'scenarios_count': len(suggestions)}
            intent_analysis = {'category': 'unknown', 'confidence': 0.0}
        
        logging.info(f"[SEMANTIC] ========== COMPLETE: {len(suggestions)} scenarios (ML: {ml_used}) ==========")
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'report': report,
            'intent': intent_analysis,
            'ml_used': ml_used,  # NEW: Indicate if ML was used
            'analyzer_type': 'ml_random_forest' if ml_used else 'rule_based',  # NEW: Which analyzer
            'test_case_context': {
                'name': test_name,
                'actions_count': len(actions),
                'has_code': len(generated_code) > 0,
                'test_format': 'prompt_builder' if any('prompt' in str(a) for a in actions) else 'recorder'  # NEW: Detect format
            }
        }), 200
    except Exception as e:
        # Capture FULL traceback for debugging
        import traceback
        import datetime
        error_trace = ''.join(traceback.format_exception(type(e), e, e.__traceback__))
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Write detailed error to log
        logging.error(f"[SEMANTIC] ============ ERROR DETAILS ============")
        logging.error(f"[SEMANTIC] Time: {timestamp}")
        logging.error(f"[SEMANTIC] Error: {type(e).__name__}: {e}")
        logging.error(f"[SEMANTIC] Full Traceback:\n{error_trace}")
        logging.error(f"[SEMANTIC] =========================================")
        
        # Also write to dedicated error file for easier access
        try:
            with open('semantic_error_trace.txt', 'w', encoding='utf-8') as f:
                f.write(f"Error Time: {timestamp}\n")
                f.write(f"Error Type: {type(e).__name__}\n")
                f.write(f"Error Message: {e}\n\n")
                f.write(f"Full Traceback:\n{error_trace}\n")
        except:
            pass
        
        return jsonify({'success': False, 'error': str(e)}), 500

# ============================================================================
# NEW ML-POWERED TEST SUGGESTIONS ENDPOINT
# Clean implementation that works with both recorder and prompt-based tests
# ============================================================================
@app.route('/ml/suggest-test-scenarios', methods=['POST'])
def ml_suggest_test_scenarios():
    """
    🤖 NEW ML-POWERED TEST SCENARIO GENERATOR
    
    Directly uses MLSemanticAnalyzer for high-quality test suggestions.
    Supports BOTH recorder and prompt-based test builder formats.
    """
    try:
        data = request.json
        test_case_id = data.get('test_case_id')
        
        if not test_case_id:
            return jsonify({'success': False, 'error': 'test_case_id required'}), 400
        
        logging.info(f"[ML-SUGGEST] Processing test case: {test_case_id}")
        
        # Load test case (try builder first, then recorder)
        test_case = None
        source_type = 'unknown'
        
        # Try test builder
        try:
            builder = get_test_case_builder()
            test_case_obj = builder.load_test_case(test_case_id)
            if test_case_obj:
                test_case = test_case_obj.to_dict()
                source_type = 'builder'
                logging.info(f"[ML-SUGGEST] Loaded from test builder")
        except Exception as e:
            logging.debug(f"[ML-SUGGEST] Test builder load failed: {e}")
        
        # Try recorder if builder didn't work
        if not test_case:
            try:
                test_case = recorder_handler.load_saved_test_from_disk(test_case_id)
                if test_case:
                    source_type = 'recorder'
                    logging.info(f"[ML-SUGGEST] Loaded from recorder")
            except Exception as e:
                logging.debug(f"[ML-SUGGEST] Recorder load failed: {e}")
        
        if not test_case:
            return jsonify({
                'success': False, 
                'error': f'Test case not found: {test_case_id}'
            }), 404
        
        # Extract actions (handle both formats)
        actions = []
        
        if 'actions' in test_case and test_case['actions']:
            # Recorder format
            actions = test_case['actions']
            logging.info(f"[ML-SUGGEST] Using {len(actions)} recorder actions")
        elif 'steps' in test_case and test_case['steps']:
            # Test builder format  
            for step in test_case['steps']:
                if isinstance(step, dict):
                    actions.append({
                        'action': step.get('prompt', step.get('description', '')),
                        'type': step.get('type', 'action')
                    })
                else:
                    actions.append({'action': str(step), 'type': 'action'})
            logging.info(f"[ML-SUGGEST] Using {len(actions)} builder steps")
        elif 'prompts' in test_case and test_case['prompts']:
            # Alternative builder format
            for p in test_case['prompts']:
                actions.append({
                    'action': p.get('prompt', ''),
                    'type': p.get('type', 'action')
                })
            logging.info(f"[ML-SUGGEST] Using {len(actions)} prompts")
        
        if not actions:
            return jsonify({
                'success': False,
                'error': 'No actions found in test case'
            }), 400
        
        # Build context
        context = {
            'test_name': test_case.get('name', 'Test'),
            'description': test_case.get('description', ''),
            'url': test_case.get('url', ''),
            'tags': test_case.get('tags', []),
            'priority': test_case.get('priority', 'medium'),
            'actions': actions
        }
        
        # Use ML analyzer if available
        suggestions = []
        ml_used = False
        
        if ML_MODE_AVAILABLE and ml_semantic_analyzer and ml_semantic_analyzer.model is not None:
            try:
                logging.info(f"[ML-SUGGEST] 🤖 Using ML RandomForest model")
                suggestions = ml_semantic_analyzer.suggest_scenarios(
                    actions, 
                    context['url'], 
                    context
                )
                ml_used = True
                logging.info(f"[ML-SUGGEST] ✓ Generated {len(suggestions)} ML scenarios")
            except Exception as e:
                logging.error(f"[ML-SUGGEST] ML generation failed: {e}", exc_info=True)
                suggestions = [{
                    'type': 'error',
                    'title': 'ML Generation Failed',
                    'description': f'Error: {str(e)}',
                    'priority': 'high',
                    'confidence': 0.0
                }]
        else:
            logging.warning(f"[ML-SUGGEST] ML model not available")
            suggestions = [{
                'type': 'info',
                'title': 'ML Model Not Available',
                'description': 'Please train or load the ML model',
                'priority':  'medium',
                'confidence': 0.0
            }]
        
        # Return response
        return jsonify({
            'success': True,
            'test_case_id': test_case_id,
            'test_name': context['test_name'],
            'source_type': source_type,
            'actions_count': len(actions),
            'ml_used': ml_used,
            'suggestions_count': len(suggestions),
            'suggestions': suggestions,
            'metadata': {
                'analyzer': 'ml_random_forest' if ml_used else 'unavailable',
                'model_loaded': ml_semantic_analyzer.model is not None if ml_semantic_analyzer else False,
                'url': context['url'],
                'priority': context['priority']
            }
        }), 200
        
    except Exception as e:
        logging.error(f"[ML-SUGGEST] Error: {e}", exc_info=True)
        return jsonify({
            'success': False,
            'error': str(e),
            'error_type': type(e).__name__
        }), 500

# TEST ENDPOINT - Verify routing works
@app.route('/ml/field-aware-test', methods=['POST', 'GET'])
def test_field_aware_routing():
    """Test if routing works"""
    with open('c:\\Users\\valaboph\\AIAutomation\\debug_routing_test.txt', 'w') as f:
        f.write(f"Test endpoint reached at {datetime.now()}\n")
    return jsonify({'success': True, 'message': 'Routing works!'})

@app.route('/ml/field-aware-suggestions', methods=['POST'])
def get_field_aware_suggestions():
    """Field-Aware Semantic Suggestions - generates boundary/security test data for input fields"""
    import traceback as tb
    debug_file = 'c:\\Users\\valaboph\\AIAutomation\\debug_field_aware.txt'
    
    try:
        # CHECKPOINT 1: Endpoint reached
        with open(debug_file, 'w', encoding='utf-8') as f:
            f.write(f"=== {datetime.now()} ===\n")
            f.write("CHECKPOINT 1: Endpoint reached\n")
        
        # CHECKPOINT 2: Parse request
        data = request.json
        test_case_id = data.get('test_case_id')
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 2: test_case_id={test_case_id}\n")
        
        if not test_case_id:
            return jsonify({'success': False, 'error': 'test_case_id required'}), 400
        
        # CHECKPOINT 3: Load test case
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 3: Loading test case...\n")
        
        test_case = None
        source_type = 'unknown'
        
        # Try recorder first
        try:
            test_case = recorder_handler.load_saved_test_from_disk(test_case_id)
            if test_case:
                source_type = 'recorder'
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  Loaded from recorder\n")
        except Exception as e:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"  Recorder failed: {str(e)[:100]}\n")
        
        # Try test builder if recorder didn't work
        if not test_case:
            try:
                builder = get_test_case_builder()
                # Load raw JSON file instead of using TestCase object
                # because to_dict() doesn't include actions/prompts fields  
                import json
                import glob
                import pathlib
                
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  Attempting builder JSON load...\n")
                
                # Get workspace root (3 levels up from src/main/python)
                script_dir = pathlib.Path(__file__).parent
                workspace_root = script_dir.parent.parent.parent
                
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  Script dir: {script_dir}\n")
                    f.write(f"  Workspace root: {workspace_root}\n")
                
                # Search for test case JSON file using pathlib (better cross-platform support)
                test_suites_dir = workspace_root / "test_suites"
                
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  Test suites dir: {test_suites_dir}\n")
                    f.write(f"  Dir exists: {test_suites_dir.exists()}\n")
                    f.write(f"  Search pattern: builder/{test_case_id}*.json\n")
                
                json_files = list(test_suites_dir.rglob(f"builder/{test_case_id}*.json"))
                
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  Found {len(json_files)} JSON files\n")
                    if json_files:
                        f.write(f"  First file: {json_files[0]}\n")
                
                if json_files:
                    json_file_path = str(json_files[0])
                    with open(json_file_path, 'r', encoding='utf-8') as f:
                        test_case = json.load(f)
                    source_type = 'builder'
                    with open(debug_file, 'a', encoding='utf-8') as f:
                        f.write(f"  ✓ Loaded from builder JSON file: {json_file_path}\n")
                else:
                    # Fallback to TestCase object if JSON file not found
                    test_case_obj = builder.load_test_case(test_case_id)
                    if test_case_obj:
                        test_case = test_case_obj.to_dict()
                        source_type = 'builder'
                        with open(debug_file, 'a', encoding='utf-8') as f:
                            f.write(f"  Loaded from builder object (no JSON file found)\n")
            except Exception as e:
                import traceback
                with open(debug_file, 'a', encoding='utf-8') as f:
                    f.write(f"  ✗ Builder exception: {str(e)}\n")
                    f.write(f"  Traceback: {traceback.format_exc()[:500]}\n")
        
        if not test_case:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"ERROR: Test case not found\n")
            return jsonify({'success': False, 'error': f'Test case not found: {test_case_id}'}), 404
        
        # CHECKPOINT 4: Extract actions
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 4: Extracting actions...\n")
            f.write(f"  test_case keys: {list(test_case.keys())}\n")
        
        actions = test_case.get('actions', [])
        if not actions:
            actions = test_case.get('prompts', [])
        if not actions:
            steps = test_case.get('steps', [])
            if steps and len(steps) > 0 and isinstance(steps[0], dict):
                actions = steps
        
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"  Found {len(actions)} actions\n")
            if actions:
                f.write(f"  First action type: {type(actions[0])}\n")
                if isinstance(actions[0], dict):
                    f.write(f"  First action keys: {list(actions[0].keys())}\n")
        
        if not actions:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"ERROR: No actions found\n")
            return jsonify({'success': False, 'error': 'No input fields found'}), 400
        
        # CHECKPOINT 5: Detect test variant type for smart filtering
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 5: Detecting variant type...\n")
        
        # Auto-detect category from test case metadata
        variant_type = test_case.get('variant_type') or test_case.get('type') or test_case.get('generation_type')
        
        # Map variant types to suggestion categories
        category_map = {
            'edge_case': 'edge_case',
            'boundary': 'boundary',
            'security': 'security',
            'i18n': 'i18n',
            'internationalization': 'i18n'
        }
        
        # User can override via request, otherwise use auto-detected variant
        category_filter = data.get('category') if data and data.get('category') else None
        if not category_filter and variant_type:
            category_filter = category_map.get(variant_type.lower())
        
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"  Variant type: {variant_type}\n")
            f.write(f"  Category filter: {category_filter}\n")
        
        # CHECKPOINT 6: Generate suggestions
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 6: Generating suggestions...\n")
            f.write(f"  Actions to analyze:\n")
            for i, action in enumerate(actions):
                f.write(f"    Action {i}: {action}\n")
        
        # Force fresh module reload to avoid cache issues
        import sys
        import importlib
        if 'ml_models.field_aware_suggestions' in sys.modules:
            importlib.reload(sys.modules['ml_models.field_aware_suggestions'])
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"  Reloaded cached module\n")
        
        from ml_models.field_aware_suggestions import generate_field_aware_semantic_scenarios
        
        test_name = test_case.get('name', 'Test')
        scenarios = generate_field_aware_semantic_scenarios(actions, test_name, category_filter)
        
        with open(debug_file, 'a', encoding='utf-8') as f:
            f.write(f"CHECKPOINT 7: Generated {len(scenarios) if scenarios else 0} scenarios\n")
            f.write(f"=== SUCCESS ===\n")
        
        if not scenarios:
            return jsonify({'success': False, 'error': 'No suggestions generated'}), 400
        
        # Return field suggestions
        return jsonify({
            'success': True,
            'test_case_id': test_case_id,
            'test_name': test_name,
            'source_type': source_type,
            'scenarios_count': len(scenarios),
            'scenarios': scenarios,
            'metadata': {
                'analyzer': 'field_aware_suggestions',
                'actions_analyzed': len(actions),
                'input_fields_found': len(scenarios[0]['field_suggestions']) if scenarios else 0
            }
        }), 200
        
    except Exception as e:
        # Write full traceback to file
        try:
            with open(debug_file, 'a', encoding='utf-8') as f:
                f.write(f"\n=== EXCEPTION ===\n")
                f.write(f"Error: {str(e)}\n")
                f.write(f"Type: {type(e).__name__}\n")
                f.write(f"Traceback:\n{tb.format_exc()}\n")
        except:
            pass  # If even error logging fails, continue
        
        logging.error(f"[FIELD-AWARE] Error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e), 'error_type': type(e).__name__}), 500

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

# ==================== Multi-Prompt Test Suite Endpoints (PHASE 0) ====================

@app.route('/test-suite/session/start', methods=['POST'])
def start_test_session():
    """Start a new test creation session."""
    return test_suite_handler.start_test_session(get_session_manager)

@app.route('/test-suite/session/<session_id>/add-prompt', methods=['POST'])
def add_prompt_to_session(session_id):
    """Add a prompt to an existing test session."""
    return test_suite_handler.add_prompt_to_session(session_id, get_session_manager, get_generator)

@app.route('/test-suite/session/<session_id>/execute', methods=['POST'])
def execute_session_directly(session_id):
    """Execute a session directly without saving (Test Builder quick execution)."""
    return test_suite_handler.execute_session_directly(session_id, get_session_manager, get_generator)

@app.route('/test-suite/session/<session_id>/remove-prompt', methods=['POST'])
def remove_prompt_from_session(session_id):
    """Remove a prompt step from the session."""
    return test_suite_handler.remove_prompt_from_session(session_id, get_session_manager)

@app.route('/test-suite/session/<session_id>/update-prompt', methods=['POST'])
def update_prompt_in_session(session_id):
    """Update an existing prompt step."""
    return test_suite_handler.update_prompt_in_session(session_id, get_session_manager, get_generator)

@app.route('/test-suite/session/<session_id>/reorder-prompt', methods=['POST'])
def reorder_prompt_in_session(session_id):
    """Reorder a prompt step (move up or down)."""
    return test_suite_handler.reorder_prompt_in_session(session_id, get_session_manager)

@app.route('/test-suite/session/<session_id>', methods=['GET'])
def get_test_session(session_id):
    """Get test session details."""
    return test_suite_handler.get_test_session(session_id, get_session_manager)

@app.route('/test-suite/session/<session_id>', methods=['DELETE'])
def delete_test_session(session_id):
    """Delete a test session."""
    return test_suite_handler.delete_test_session(session_id, get_session_manager)

@app.route('/test-suite/session/<session_id>/preview', methods=['GET'])
def preview_test_code(session_id):
    """Preview generated code for entire test session."""
    return test_suite_handler.preview_test_code(session_id, get_session_manager)

@app.route('/test-suite/session/<session_id>/save', methods=['POST'])
def save_test_case(session_id):
    """Save test session as executable test case."""
    return test_suite_handler.save_test_case(session_id, get_session_manager, get_test_case_builder, get_generator)

@app.route('/test-suite/sessions', methods=['GET'])
def list_test_sessions():
    """List all active test sessions."""
    return test_suite_handler.list_test_sessions(get_session_manager)

@app.route('/test-suite/cache/clear', methods=['POST'])
def clear_test_builder_cache():
    """Clear the test builder inference cache for better performance."""
    return test_suite_handler.clear_inference_cache()

@app.route('/test-suite/test-cases', methods=['GET'])
def list_test_cases():
    """List all saved test cases."""
    return test_suite_handler.list_test_cases(get_test_case_builder)

@app.route('/test-suite/test-cases/<test_case_id>', methods=['GET'])
def get_test_case(test_case_id):
    """Get test case details."""
    return test_suite_handler.get_test_case(test_case_id, get_test_case_builder)

@app.route('/test-suite/test-cases/<test_case_id>', methods=['DELETE'])
def delete_test_case_endpoint(test_case_id):
    """Delete a test case."""
    return test_suite_handler.delete_test_case_endpoint(test_case_id, get_test_case_builder)

@app.route('/test-suite/test-cases/<test_case_id>/rename', methods=['POST'])
def rename_test_case(test_case_id):
    """Rename a test case."""
    return test_suite_handler.rename_test_case(test_case_id, get_test_case_builder)

@app.route('/test-suite/execute/<test_case_id>', methods=['POST'])
def execute_test_case(test_case_id):
    """Execute a saved test case."""
    return test_suite_handler.execute_test_case(test_case_id, get_test_runner)

@app.route('/test-suite/execute-suite', methods=['POST'])
def execute_test_suite_endpoint():
    """Execute multiple test cases."""
    return test_suite_handler.execute_test_suite(get_test_runner)

# ==================== Healing Approval Workflow ====================

@app.route('/healing/pending-approvals', methods=['GET'])
def get_pending_approvals():
    """Get all pending healing approval requests."""
    try:
        from self_healing.healing_approval import get_approval_workflow
        workflow = get_approval_workflow()
        
        pending = workflow.get_pending_approvals()
        
        return jsonify({
            'success': True,
            'approvals': pending,
            'count': len(pending)
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting pending approvals: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/healing/approve/<approval_id>', methods=['POST'])
def approve_healing_endpoint(approval_id):
    """Approve a healing decision."""
    try:
        from self_healing.healing_approval import get_approval_workflow
        workflow = get_approval_workflow()
        
        data = request.get_json() or {}
        user_id = data.get('user_id', 'unknown')
        update_test_case = data.get('update_test_case', True)
        
        result = workflow.approve_healing(approval_id, user_id, update_test_case)
        
        return jsonify(result), 200 if result['success'] else 404
        
    except Exception as e:
        logging.error(f"Error approving healing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/healing/reject/<approval_id>', methods=['POST'])
def reject_healing_endpoint(approval_id):
    """Reject a healing decision."""
    try:
        from self_healing.healing_approval import get_approval_workflow
        workflow = get_approval_workflow()
        
        data = request.get_json() or {}
        user_id = data.get('user_id', 'unknown')
        reason = data.get('reason', None)
        
        result = workflow.reject_healing(approval_id, user_id, reason)
        
        return jsonify(result), 200 if result['success'] else 404
        
    except Exception as e:
        logging.error(f"Error rejecting healing: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/healing/statistics', methods=['GET'])
def get_healing_statistics():
    """Get healing approval statistics."""
    try:
        from self_healing.healing_approval import get_approval_workflow
        workflow = get_approval_workflow()
        
        stats = workflow.get_approval_statistics()
        
        return jsonify({
            'success': True,
            'statistics': stats
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting healing statistics: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ML Test Case Generation Routes ====================

@app.route('/semantic/generate-test-cases', methods=['POST'])
def generate_test_cases():
    """
    Generate multiple complete test cases from a single source test.
    
    Workflow:
    1. User selects saved test case
    2. Optionally retrains ML with that test case (if retrain=true)
    3. Generates 20-50 complete test case variants
    4. Returns full test cases (not just scenario names)
    
    NOTE: Retraining is SLOW. Use /ml/suggest-test-scenarios for fast suggestions.
    """
    try:
        if not test_case_generator or not on_demand_trainer:
            return jsonify({
                'success': False,
                'error': 'Test case generator not available'
            }), 503
        
        # Handle both parsed JSON and string JSON
        data = request.json
        if isinstance(data, str):
            import json
            data = json.loads(data)
        
        test_case_id = data.get('test_case_id')
        generation_types = data.get('generation_types')  # Optional: ['negative', 'boundary', 'edge_case', 'security', 'data_validation']
        retrain = data.get('retrain', False)  # NEW: Make retraining optional (default: False)
        
        if not test_case_id:
            return jsonify({
                'success': False,
                'error': 'test_case_id is required'
            }), 400
        
        logging.info(f"[GENERATE] Generating test cases from: {test_case_id} (retrain={retrain})")
        
        # STEP 1: Optionally retrain ML with this test case (SLOW!)
        retrain_result = {'success': False}
        if retrain:
            logging.info(f"[GENERATE] Step 1: Retraining ML with test case {test_case_id}")
            retrain_result = on_demand_trainer.retrain_with_test_case(test_case_id)
            
            if not retrain_result['success']:
                logging.warning(f"[GENERATE] Retraining failed, but continuing: {retrain_result.get('error')}")
        else:
            logging.info(f"[GENERATE] Skipping retraining (using existing ML model)")
        
        if not retrain_result['success']:
            logging.warning(f"[GENERATE] Retraining failed, but continuing with generation: {retrain_result.get('error')}")
        
        # STEP 2: Generate test case variants
        logging.info(f"[GENERATE] Step 2: Generating test case variants")
        generation_result = test_case_generator.generate_test_cases(test_case_id, generation_types)
        
        if not generation_result['success']:
            return jsonify(generation_result), 500
        
        logging.info(f"[GENERATE] ✓ Generated {generation_result['total_generated']} test cases")
        
        return jsonify({
            'success': True,
            'source_test': generation_result['source_test'],
            'generated_tests': generation_result['generated_tests'],
            'total_generated': generation_result['total_generated'],
            'ml_retrained': retrain_result['success']
        }), 200
        
    except Exception as e:
        logging.error(f"Error generating test cases: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/semantic/save-generated-tests', methods=['POST'])
def save_generated_tests():
    """
    Save selected generated test cases back to test_suites/.
    
    NEW: Properly saves to recorder or builder format based on original test source.
    Adds semantic identification tags for filtering in test suite.
    
    Request body:
    {
      "tests": [  // or "test_cases"
        {"test_case_id": "...", "name": "...", "actions": [...], "source": "recorder/builder", ...},
        ...
      ],
      "test_type": "regression"   # Required: regression, smoke, integration, general, etc.
    }
    """
    try:
        logging.info("[SAVE-GENERATED] ========== SAVE SEMANTIC TESTS START ==========")
        data = request.json
        logging.info(f"[SAVE-GENERATED] Received request with keys: {list(data.keys())}")
        
        # Accept both 'tests' (from frontend) and 'test_cases' for compatibility
        test_cases = data.get('tests', data.get('test_cases', []))
        test_type = data.get('test_type', 'general')  # Default to 'general'
        
        logging.info(f"[SAVE-GENERATED] Processing {len(test_cases)} tests for test_type={test_type}")
        
        if not test_cases:
            logging.warning("[SAVE-GENERATED] No test cases provided in request")
            return jsonify({
                'success': False,
                'error': 'No test cases provided'
            }), 400
        
        # Save each test case to appropriate test_suites/ directory
        from pathlib import Path
        import json
        
        # Use the already-defined PROJECT_ROOT from top of file
        project_root = Path(PROJECT_ROOT)
        
        saved_files = []
        saved_as_builder = 0
        saved_as_recorder = 0
        
        for test_case in test_cases:
            # LOG: Debug incoming test data
            parent_id_value = test_case.get('parent_test_case_id')
            url_value = test_case.get('url')
            logging.info(f"[SAVE-GENERATED] 🔍 Incoming test data: test_case_id={test_case.get('test_case_id')}, parent_test_case_id={parent_id_value}, url={url_value}")
            
            # Determine source (builder or recorder) - default to builder since we have executable actions
            source = test_case.get('source', 'builder')
            
            # Sanitize test ID
            test_id = test_case.get('test_case_id', f"test_{int(time.time())}")
            test_id = test_id.replace('/', '_').replace('\\', '_').replace(' ', '_')
            test_name = test_case.get('name', test_id)
            
            # Add common metadata
            test_case['test_type'] = test_type
            test_case['saved_at'] = time.time()
            test_case['saved_to_suite_at'] = datetime.now().isoformat()
            
            # Add semantic identification tags and metadata
            test_case['generated_by'] = 'semantic-analysis'
            test_case['variant_type'] = test_case.get('generation_type', 'semantic-generated')
            
            # Add tags for filtering
            existing_tags = test_case.get('tags', [])
            semantic_tags = ['semantic', 'ai-generated', test_type]
            if test_case.get('generation_type'):
                semantic_tags.append(test_case['generation_type'])
            test_case['tags'] = list(set(existing_tags + semantic_tags))
            
            # Save to appropriate directory based on source
            if source == 'recorder' or 'recorded' in str(test_case.get('test_case_id', '')).lower():
                # Save as recorder test: test_suites/{test_type}/recorded/{test_id}.json
                suite_dir = project_root / "test_suites" / test_type / "recorded"
                suite_dir.mkdir(parents=True, exist_ok=True)
                
                test_case['source'] = 'recorded'
                test_case['action_count'] = len(test_case.get('actions', []))
                
                filename = f"{test_id}.json"
                filepath = suite_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(test_case, f, indent=2, ensure_ascii=False)
                
                saved_files.append(str(filepath))
                saved_as_recorder += 1
                logging.info(f"[SAVE-GENERATED] ✓ Saved as recorder: test_suites/{test_type}/recorded/{filename}")
                
            else:
                # Save as builder test: test_suites/{test_type}/builder/{test_id}.json
                suite_dir = project_root / "test_suites" / test_type / "builder"
                suite_dir.mkdir(parents=True, exist_ok=True)
                
                test_case['source'] = 'builder'
                test_case['prompt_count'] = len(test_case.get('actions', []))
                
                # === CRITICAL: Copy URL from parent FIRST, before any other processing ===
                # Check if variant needs URL (missing, None, empty string, or empty array)
                url_value = test_case.get('url')
                needs_url = not url_value or url_value == [] or (isinstance(url_value, str) and url_value.strip() == '')
                if test_case.get('parent_test_case_id') and needs_url:
                    parent_id = test_case['parent_test_case_id']
                    logging.info(f"[URL-COPY-EARLY] ⚠️  Variant {test_id} has empty URL, needs copy from parent {parent_id}")
                    try:
                        builder = get_test_case_builder()
                        parent_test = builder.load_test_case(parent_id)
                        if parent_test:
                            parent_url = parent_test.url if hasattr(parent_test, 'url') else ''
                            logging.info(f"[URL-COPY-EARLY] Parent test URL: [{parent_url}]")
                            if parent_url and parent_url.strip():
                                test_case['url'] = parent_url
                                logging.info(f"[URL-COPY-EARLY] ✅ SUCCESS - Copied URL: {parent_url}")
                            else:
                                logging.error(f"[URL-COPY-EARLY] ❌ Parent {parent_id} has no URL!")
                        else:
                            logging.error(f"[URL-COPY-EARLY] ❌ Could not load parent {parent_id}")
                    except Exception as e:
                        logging.error(f"[URL-COPY-EARLY] ❌ Error loading parent: {e}", exc_info=True)
                else:
                    logging.info(f"[URL-COPY-EARLY] Variant {test_id} already has URL or no parent: url={test_case.get('url')}, parent={test_case.get('parent_test_case_id')}")
                
                # Builder expects 'prompts' or 'steps' field
                if 'actions' in test_case and 'prompts' not in test_case:
                    logging.info(f"[SAVE-GENERATED] Converting {len(test_case['actions'])} actions to prompts for {test_id}")
                    # Log first action to debug structure
                    if test_case['actions']:
                        sample_action = test_case['actions'][0]
                        logging.info(f"[SAVE-GENERATED] Sample action structure: {list(sample_action.keys())}")
                        logging.info(f"[SAVE-GENERATED] Sample action: {sample_action}")
                    
                    # Convert actions to prompts format for builder
                    # ✓ FIX: Use 'prompt' first (clean action text) instead of 'description' (which has test name prefix)
                    test_case['prompts'] = [
                        {
                            'step': i + 1,  # ✓ CRITICAL: Add step number for build_from_session
                            'prompt': action.get('prompt') or action.get('description') or action.get('action') or f'Step {i+1}',
                            'type': action.get('type', 'action'),
                            'value': action.get('value', '')
                        } for i, action in enumerate(test_case.get('actions', []))
                    ]
                    logging.info(f"[SAVE-GENERATED] Converted to {len(test_case['prompts'])} prompts")
                    if test_case['prompts']:
                        logging.info(f"[SAVE-GENERATED] Sample prompt: {test_case['prompts'][0]}")
                elif 'prompts' in test_case:
                    # Ensure existing prompts have step numbers
                    logging.info(f"[SAVE-GENERATED] Test {test_id} already has prompts, ensuring step numbers")
                    for i, prompt in enumerate(test_case['prompts']):
                        if 'step' not in prompt:
                            prompt['step'] = i + 1
                
                # ===== CRITICAL FIX: Copy parent step code to variant prompts =====
                # For semantic variants, copy generated_code from parent test steps to variant prompts
                # This allows Python executor to use the parent's working code
                if test_case.get('parent_test_case_id') and test_case.get('generated_by') == 'semantic-analysis':
                    parent_id = test_case['parent_test_case_id']
                    logging.info(f"[SEMANTIC-FIX] Test {test_id} is semantic variant of {parent_id}, copying parent step code...")
                    
                    try:
                        builder = get_test_case_builder()
                        parent_test = builder.load_test_case(parent_id)
                        
                        if parent_test and parent_test.steps:
                            logging.info(f"[SEMANTIC-FIX] Loaded parent with {len(parent_test.steps)} steps")
                            
                            # Copy URL from parent test if variant doesn't have one
                            if not test_case.get('url'):
                                # Try parent's test_case.url first, then first step's URL
                                parent_url = parent_test.url or (parent_test.steps[0].get('url') if parent_test.steps else '')
                                if parent_url:
                                    test_case['url'] = parent_url
                                    logging.info(f"[SEMANTIC-FIX] ✓ Copied URL from parent: {test_case['url']}")
                            
                            # Match variant prompts to parent steps by prompt text (with fuzzy matching)
                            for variant_prompt in test_case.get('prompts', []):
                                variant_prompt_text = variant_prompt.get('prompt', '').lower().strip()
                                
                                for parent_step in parent_test.steps:
                                    parent_prompt_text = parent_step.get('prompt', '').lower().strip()
                                    
                                    # Exact match first
                                    if variant_prompt_text == parent_prompt_text:
                                        parent_code = parent_step.get('generated_code')
                                        if parent_code:
                                            variant_prompt['generated_code'] = parent_code
                                            logging.info(f"[SEMANTIC-FIX] ✓ Copied code (exact match): '{variant_prompt_text[:50]}'")
                                        break
                                    # Fuzzy match: check if parent prompt is contained in variant (handles prefixed descriptions)
                                    elif parent_prompt_text in variant_prompt_text or variant_prompt_text in parent_prompt_text:
                                        parent_code = parent_step.get('generated_code')
                                        if parent_code:
                                            variant_prompt['generated_code'] = parent_code
                                            logging.info(f"[SEMANTIC-FIX] ✓ Copied code (fuzzy match): variant='{variant_prompt_text[:40]}' parent='{parent_prompt_text[:40]}'")
                                        break
                            
                            logging.info(f"[SEMANTIC-FIX] ✓ Finished copying parent code to variant prompts")
                        else:
                            logging.warning(f"[SEMANTIC-FIX] Could not load parent test {parent_id}")
                    except Exception as e:
                        logging.error(f"[SEMANTIC-FIX] Error copying parent code: {e}", exc_info=True)
                
                # Generate executable code for builder tests if not already present
                # Check if generated_code is missing OR empty
                logging.info(f"[CODE-GEN] Processing test {test_id} for code generation")
                
                needs_code_generation = (
                    'generated_code' not in test_case or 
                    not test_case.get('generated_code') or
                    not test_case['generated_code'].get('python')
                )
                
                logging.info(f"[CODE-GEN] needs_code_generation: {needs_code_generation}")
                
                if needs_code_generation and test_case.get('prompts'):
                    try:
                        logging.info(f"[SAVE-GENERATED] Generating code for {test_id} with {len(test_case['prompts'])} prompts")
                        logging.info(f"[SAVE-GENERATED] Sample prompt: {test_case['prompts'][0] if test_case['prompts'] else 'none'}")
                        
                        # SEMANTIC FIX: For semantic variants, copy step-level generated_code from parent
                        parent_test_id = test_case.get('parent_test_case_id')
                        is_semantic_variant = parent_test_id and test_case.get('generated_by') == 'semantic-analysis'
                        
                        # For semantic variants, copy generated_code from parent STEPS to variant PROMPTS
                        if is_semantic_variant and parent_test_id:
                            logging.info(f"[SAVE-GENERATED] Semantic variant detected, copying step code from parent: {parent_test_id}")
                            
                            # Load parent test case
                            builder = get_test_case_builder()
                            
                            # Find original parent (in case of nested variants)
                            original_parent_id = parent_test_id
                            max_depth = 10
                            depth = 0
                            
                            while '_variant_' in original_parent_id and depth < max_depth:
                                logging.info(f"[SAVE-GENERATED] Parent {original_parent_id} is also a variant, looking for original...")
                                base_id = original_parent_id.split('_variant_')[0]
                                base_test = builder.load_test_case(base_id)
                                if base_test:
                                    original_parent_id = base_id
                                    logging.info(f"[SAVE-GENERATED] Found original parent: {original_parent_id}")
                                    break
                                else:
                                    logging.warning(f"[SAVE-GENERATED] Base test {base_id} not found, using {original_parent_id}")
                                    break
                                depth += 1
                            
                            parent_test = builder.load_test_case(original_parent_id)
                            logging.info(f"[SAVE-GENERATED] Using parent test: {original_parent_id} (original requested: {parent_test_id})")
                            
                            # Copy generated_code from parent STEPS to variant PROMPTS
                            if parent_test and parent_test.steps:
                                logging.info(f"[SAVE-GENERATED] Parent has {len(parent_test.steps)} steps")
                                variant_prompts = test_case.get('prompts', [])
                                
                                # Match variant prompts to parent steps by prompt text
                                for variant_prompt in variant_prompts:
                                    variant_prompt_text = variant_prompt.get('prompt', '').lower().strip()
                                    
                                    # Find matching parent step
                                    for parent_step in parent_test.steps:
                                        parent_prompt_text = parent_step.get('prompt', '').lower().strip()
                                        
                                        # If prompts match, copy the generated_code
                                        if variant_prompt_text == parent_prompt_text:
                                            parent_code = parent_step.get('generated_code')
                                            if parent_code:
                                                variant_prompt['generated_code'] = parent_code
                                                logging.info(f"[SAVE-GENERATED] ✓ Copied code for step: '{variant_prompt_text[:40]}...'")
                                            break
                                
                                logging.info(f"[SAVE-GENERATED] ✓ Copied step-level code from parent")
                                
                                # CRITICAL FIX: Add URL navigation to each prompt's generated_code
                                variant_url = test_case.get('url') or (parent_test.url if parent_test else '')
                                
                                # ✅ DON'T add URL to individual prompts - let TestCaseBuilder handle it at test level
                                # The _generate_python_code_execution_ready() method will add URL once at the beginning
                                logging.info(f"[URL-FIX] ✓ URL will be added by TestCaseBuilder at test level")
                            else:
                                logging.warning(f"[SAVE-GENERATED] Parent test {parent_test_id} not found or has no steps")
                        
                        # Now generate full test code using build_from_session
                        # (which will use the copied step-level generated_code)
                        # Check again if we still need to generate code
                        still_needs_code = (
                            'generated_code' not in test_case or 
                            not test_case.get('generated_code') or
                            not test_case['generated_code'].get('python')
                        )
                        
                        if still_needs_code:
                            logging.info(f"[SAVE-GENERATED] Generating full test code from prompts...")
                            
                            # Use test case builder to generate code from prompts
                            builder = get_test_case_builder()
                            
                            # Create a temporary session-like dict for code generation
                            temp_session = {
                                'session_id': test_id,
                                'name': test_name,
                                'url': test_case.get('url', ''),
                                'prompts': test_case['prompts']  # Now includes generated_code copied from parent
                            }
                            
                            logging.info(f"[SAVE-GENERATED] Created temp session with {len(temp_session['prompts'])} prompts")
                            
                            # Build test case from session (generates code)
                            temp_test_case = builder.build_from_session(
                                session_data=temp_session,
                                test_case_id=test_id,
                                tags=test_case.get('tags', []),
                                priority=test_case.get('priority', 'medium'),
                                compact_mode=True,
                                execution_ready=is_semantic_variant  # Generate execution-ready code for semantic tests
                            )
                            
                            # Extract generated code
                            if temp_test_case and temp_test_case.generated_code:
                                # Check if code was actually generated
                                has_python = bool(temp_test_case.generated_code.get('python', '').strip())
                                has_javascript = bool(temp_test_case.generated_code.get('javascript', '').strip())
                                has_java = bool(temp_test_case.generated_code.get('java', '').strip())
                                
                                if has_python or has_javascript or has_java:
                                    test_case['generated_code'] = temp_test_case.generated_code
                                    logging.info(f"[SAVE-GENERATED] ✓ Generated code for {test_id} (Python: {has_python}, JS: {has_javascript}, Java: {has_java})")
                                else:
                                    logging.warning(f"[SAVE-GENERATED] ⚠ Code generation returned empty code for {test_id}")
                            else:
                                logging.warning(f"[SAVE-GENERATED] ⚠ build_from_session returned None or no generated_code for {test_id}")
                    except Exception as code_gen_error:
                        logging.error(f"[SAVE-GENERATED] ❌ Code generation failed for {test_id}: {code_gen_error}")
                        logging.error(f"[SAVE-GENERATED] Traceback:", exc_info=True)
                        # Continue saving without code - can be generated on demand
                else:
                    if 'generated_code' in test_case:
                        logging.info(f"[SAVE-GENERATED] ✓ Test {test_id} already has generated code")
                    elif not test_case.get('prompts'):
                        logging.warning(f"[SAVE-GENERATED] ⚠ Test {test_id} has no prompts, cannot generate code")
                
                safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                                   for c in test_name)
                filename = f"{test_id}_{safe_name}.json"
                filepath = suite_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(test_case, f, indent=2, ensure_ascii=False)
                
                saved_files.append(str(filepath))
                saved_as_builder += 1
                logging.info(f"[SAVE-GENERATED] ✓ Saved as builder: test_suites/{test_type}/builder/{filename}")
        
        summary_msg = f"Saved {len(saved_files)} test cases to test_suites/{test_type}/"
        if saved_as_builder > 0 and saved_as_recorder > 0:
            summary_msg += f" ({saved_as_builder} builder, {saved_as_recorder} recorder)"
        
        return jsonify({
            'success': True,
            'message': summary_msg,
            'saved_count': len(saved_files),
            'saved_as_builder': saved_as_builder,
            'saved_as_recorder': saved_as_recorder,
            'test_type': test_type,
            'saved_files': [f.replace('\\', '/').split('AIAutomation/')[-1] for f in saved_files]
        }), 200
        
    except Exception as e:
        logging.error(f"Error saving generated tests: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== ML Training Routes (On-Demand) ====================

@app.route('/ml/training-status', methods=['GET'])
def get_training_status():
    """Get last training info (not threshold-based)."""
    try:
        if not on_demand_trainer:
            return jsonify({
                'success': False,
                'error': 'On-demand trainer not available'
            }), 503
        
        # Get last training info
        last_training = on_demand_trainer._load_last_training_info()
        
        if not last_training:
            return jsonify({
                'success': True,
                'has_trained': False,
                'message': 'No training history found'
            }), 200
        
        return jsonify({
            'success': True,
            'has_trained': True,
            'last_training': last_training
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting training status: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/ml/trigger-training', methods=['POST'])
def trigger_training():
    """Manually trigger ML model retraining (on-demand)."""
    try:
        if not on_demand_trainer:
            return jsonify({
                'success': False,
                'error': 'On-demand trainer not available'
            }), 503
        
        logging.info("[MANUAL-RETRAIN] Manual retraining triggered")
        
        # Trigger retraining
        result = on_demand_trainer.trigger_retraining()
        
        if result['success']:
            return jsonify({
                'success': True,
                'message': 'Model retrained successfully',
                'results': result['results']
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': result.get('error', 'Training failed')
            }), 500
        
    except Exception as e:
        logging.error(f"Error triggering training: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


# ==================== Server Startup ====================

if __name__ == '__main__':
    from waitress import serve
    
    # Register feedback collection routes if ML mode available
    if ML_MODE_AVAILABLE and feedback_collector is not None:
        create_feedback_routes(app, feedback_collector)
        logging.info("[INIT] ✓ Feedback collection routes registered")
    
    # Model will be loaded lazily on first request via get_generator()
    print("[SERVER] AI model will be loaded on first request...")
    if ML_MODE_AVAILABLE:
        print("[SERVER] ML Semantic Analysis: ENABLED")
    else:
        print("[SERVER] ML Semantic Analysis: DISABLED (using rule-based)")
    print()
    
    print("="*60)
    print("[SERVER] Selenium SLM API Server (Modular)")
    print("="*60)
    print("[WEB] Interface: http://localhost:5003")
    print("[WEB] Screenshot AI: http://localhost:5003/screenshot-generator")
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
    print("  POST /recorder/save-test-case - Save recorded test to disk")
    print("  GET  /recorder/sessions   - List active sessions")
    print("  GET  /recorder/saved-tests - List all saved recorder test cases")
    print("  GET  /recorder/test/<id>  - Get saved test with full details (actions)")
    
    print("\n[ML-POWERED] Test Scenario Generator 🤖:")
    print("  POST /ml/suggest-test-scenarios  - NEW! ML-powered test suggestions (Recorder + Builder)")
    
    print("\n[SEMANTIC] Analysis:")
    print("  POST /semantic/analyze-intent    - Analyze test intent")
    print("  POST /semantic/suggest-scenarios - Suggest test scenarios")
    print("  GET  /semantic/cache-stats       - View cache statistics")
    print("  POST /semantic/clear-cache       - Clear cache")
    if ML_MODE_AVAILABLE:
        print("  POST /semantic/feedback/rate-scenario   - Rate suggested scenario")
        print("  POST /semantic/feedback/test-result     - Record test result")
        print("  POST /semantic/feedback/suggest-scenario - Submit user suggestion")
        print("  GET  /semantic/feedback/summary         - Get feedback statistics")
    print("\n[SCREENSHOT] Multi-modal AI:")
    print("  POST /screenshot/analyze        - Detect elements from screenshot")
    print("  POST /screenshot/generate-code  - Generate test from screenshot")
    print("  POST /screenshot/annotate       - Annotate screenshot with elements")
    print("\n[TEST SUITE] Execution:")
    print("  POST /recorder/execute-test - Execute single test")
    print("  GET  /test-suite/execution-results/<test_case_id> - Get execution history with screenshots")
    print("  POST /recorder/delete-session - Delete specific test case")
    print("  POST /recorder/clear-sessions - Clear all test cases")
    print("="*60 + "\n")
    
    print("[SERVER] Starting production server on http://localhost:5003")
    print(f"[SERVER] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("[SERVER] Press CTRL+C to quit\n")
    
    # DEBUG: Print all registered routes (commented out for cleaner output)
    # Uncomment below to see all registered Flask routes during development
    # print("[DEBUG] Registered Flask routes:")
    # for rule in app.url_map.iter_rules():
    #     methods = ', '.join(sorted(rule.methods - {'HEAD', 'OPTIONS'}))
    #     print(f"  {rule.rule:50s} [{methods}] -> {rule.endpoint}")
    # print()
    
    sys.stdout.flush()
    
    try:
        serve(app, host='0.0.0.0', port=5003, threads=6, channel_timeout=120)
    except KeyboardInterrupt:
        print("\n[INFO] Server shutting down...")
    except Exception as e:
        print(f"\n[ERROR] Server error: {e}")
        traceback.print_exc()
