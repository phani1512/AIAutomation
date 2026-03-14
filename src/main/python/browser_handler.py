"""
Browser control endpoints.
"""
import time
import logging
import os
from flask import request, jsonify

def navigate_and_inject(browser_executor, web_dir, url_monitor):
    """Navigate to URL and inject recorder script."""
    try:
        data = request.json
        url = data.get('url', '')
        
        if not url:
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        # Check if browser executor exists and has driver
        if not browser_executor:
            logging.error("Browser executor is None")
            return jsonify({'success': False, 'error': 'Browser executor not initialized'}), 400
            
        if not hasattr(browser_executor, 'driver') or not browser_executor.driver:
            logging.error("Browser driver is None or not initialized")
            return jsonify({'success': False, 'error': 'Browser driver not initialized. Please initialize browser first.'}), 400
        
        # Navigate to the URL
        logging.info(f"Attempting to navigate to: {url}")
        browser_executor.driver.get(url)
        logging.info(f"Successfully navigated to: {url}")
        
        # Wait for page to load
        time.sleep(2)
        
        # Close sticky popup by clicking the sticky-close div
        try:
            popup_closed = browser_executor.driver.execute_script("""
                var stickyClose = document.getElementById('sticky-close');
                if (stickyClose) {
                    stickyClose.click();
                    return 'Popup closed';
                }
                return 'No popup found';
            """)
            logging.info(f"Popup handling: {popup_closed}")
            time.sleep(0.5)
        except Exception as e:
            logging.debug(f"Popup close attempt failed: {e}")
        
        # Read and inject the recorder script
        recorder_script_path = os.path.join(web_dir, 'recorder-inject.js')
        logging.info(f"Reading recorder script from: {recorder_script_path}")
        
        if not os.path.exists(recorder_script_path):
            return jsonify({'success': False, 'error': f'Recorder script not found at {recorder_script_path}'}), 500
        
        with open(recorder_script_path, 'r', encoding='utf-8') as f:
            recorder_script = f.read()
        
        # Inject the script
        try:
            browser_executor.driver.execute_script(recorder_script)
            logging.info("✅ Injected recorder script successfully")
            
            # Wait a moment for script to initialize
            time.sleep(0.5)
            
            # Verify script was loaded
            result = browser_executor.driver.execute_script("return typeof window.startRecorderCapture === 'function';")
            logging.info(f"🔍 Recorder script check: startRecorderCapture function exists = {result}")
            
            if result:
                # Start capturing
                browser_executor.driver.execute_script("window.startRecorderCapture();")
                logging.info("✅ Started recorder capture (called window.startRecorderCapture())")
                
                # Verify it's recording
                is_recording = browser_executor.driver.execute_script("return window.isRecording;")
                logging.info(f"🔍 Recording status: window.isRecording = {is_recording}")
                
                if not is_recording:
                    logging.error("❌ WARNING: window.isRecording is false after calling startRecorderCapture()")
                
                # Initialize window handle tracking
                try:
                    url_monitor.last_window_handle = browser_executor.driver.current_window_handle
                    url_monitor.last_window_count = len(browser_executor.driver.window_handles)
                    logging.info(f"[Recorder] Initialized with {url_monitor.last_window_count} window(s)")
                except:
                    pass
                
                # Start URL monitoring to persist recorder across page navigations
                url_monitor.start()
                logging.info("✅ Started URL monitoring for recorder persistence")
            else:
                logging.error("❌ startRecorderCapture function not found - script injection may have failed")
                return jsonify({'success': False, 'error': 'Failed to start recorder - injection error'}), 500
                
        except Exception as e:
            logging.error(f"Script injection error: {str(e)}")
            return jsonify({'success': False, 'error': f'Script injection failed: {str(e)}'}), 500
        
        return jsonify({
            'success': True,
            'url': url,
            'message': 'Navigated and recorder script injected'
        }), 200
        
    except Exception as e:
        logging.error(f"Error navigating and injecting recorder: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500

def start_new_test(browser_executor, web_dir, url_monitor, recorder):
    """Start a new test recording in the existing browser session."""
    import uuid
    
    try:
        data = request.json
        test_name = data.get('name', f'Test_{len(recorder.recorded_sessions) + 1}')
        url = data.get('url', '')
        module = data.get('module', '')
        
        if not url:
            logging.error("No URL provided for new test")
            return jsonify({'success': False, 'error': 'URL is required'}), 400
        
        # Check if browser is still available
        if not browser_executor:
            logging.error("Browser executor is None")
            return jsonify({
                'success': False, 
                'error': 'Browser not available. Please start a new recording session.'
            }), 400
            
        if not hasattr(browser_executor, 'driver') or not browser_executor.driver:
            logging.error("Browser driver is None or not initialized")
            return jsonify({
                'success': False, 
                'error': 'Browser not available. Please start a new recording session.'
            }), 400
        
        # Create new session
        session_id = str(uuid.uuid4())
        recorder.recorded_sessions[session_id] = {
            'name': test_name,
            'url': url,
            'module': module,
            'actions': [],
            'created_at': time.time(),
            'active': True,
            'stopped': False
        }
        
        recorder.active_session_id = session_id
        logging.info(f"Created new session: {session_id} (Module: {module})")
        
        # Navigate to new URL
        logging.info(f"Navigating to new URL: {url}")
        try:
            browser_executor.driver.get(url)
            logging.info(f"Successfully navigated to: {url}")
        except Exception as nav_error:
            logging.error(f"Navigation failed: {str(nav_error)}")
            return jsonify({
                'success': False,
                'error': f'Failed to navigate to URL: {str(nav_error)}'
            }), 500
        
        # Wait for page to load
        time.sleep(3)
        
        # Read and inject the recorder script
        recorder_script_path = os.path.join(web_dir, 'recorder-inject.js')
        logging.info(f"Reading recorder script from: {recorder_script_path}")
        
        if not os.path.exists(recorder_script_path):
            logging.error(f"Recorder script not found at: {recorder_script_path}")
            return jsonify({
                'success': False,
                'error': f'Recorder script not found at {recorder_script_path}'
            }), 500
            
        try:
            with open(recorder_script_path, 'r', encoding='utf-8') as f:
                recorder_script = f.read()
            
            logging.info("Injecting recorder script...")
            browser_executor.driver.execute_script(recorder_script)
            logging.info("✅ Recorder script injected successfully")
            
            # Wait a moment for script to initialize
            time.sleep(1)
            
            # Verify the script was loaded
            script_loaded = browser_executor.driver.execute_script(
                "return typeof window.startRecorderCapture === 'function';"
            )
            
            logging.info(f"🔍 Script loaded check: startRecorderCapture exists = {script_loaded}")
            
            if script_loaded:
                browser_executor.driver.execute_script("window.startRecorderCapture();")
                logging.info("✅ Started recorder capture")
                
                # Verify it's recording
                is_recording = browser_executor.driver.execute_script("return window.isRecording;")
                logging.info(f"🔍 Recording status: window.isRecording = {is_recording}")
                
                if not is_recording:
                    logging.error("❌ WARNING: Recorder not started properly")
                
                # Restart URL monitoring
                url_monitor.start()
                logging.info("✅ Restarted URL monitoring")
                
                return jsonify({
                    'success': True,
                    'session_id': session_id,
                    'message': 'New test recording started'
                }), 200
            else:
                logging.error("startRecorderCapture function not found after injection")
                return jsonify({
                    'success': False,
                    'error': 'Recorder script injection failed'
                }), 500
                
        except Exception as script_error:
            logging.error(f"Error injecting/starting recorder script: {str(script_error)}")
            return jsonify({
                'success': False,
                'error': f'Script injection error: {str(script_error)}'
            }), 500
            
    except Exception as e:
        logging.error(f"Error starting new test: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500

# Global variable to store the last created browser executor
_last_browser_executor = None

def get_last_browser_executor():
    """Get the last created browser executor."""
    global _last_browser_executor
    return _last_browser_executor

def initialize_browser(browser_executor, browser_executor_class):
    """Initialize browser for execution."""
    global _last_browser_executor
    try:
        data = request.get_json() or {}
        browser = data.get('browser', 'chrome')
        headless = data.get('headless', False)
        
        if not browser_executor:
            browser_executor = browser_executor_class()
            _last_browser_executor = browser_executor
        
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

def execute_in_browser(browser_executor, browser_executor_class):
    """Execute code in browser."""
    global _last_browser_executor
    try:
        data = request.get_json()
        code = data.get('code', '')
        url = data.get('url', '')
        
        if not code:
            return jsonify({'success': False, 'error': 'Code is required'}), 400
        
        # Check if browser is initialized and driver is active
        if not browser_executor or not hasattr(browser_executor, 'driver') or not browser_executor.driver:
            logging.warning("[BROWSER] Browser not initialized or driver closed, creating new instance")
            browser_executor = browser_executor_class()
            browser_executor.initialize_driver()
            _last_browser_executor = browser_executor
            logging.info("[BROWSER] New browser executor created and initialized")
            
            # Return the browser executor back to the caller to update the global reference
            # Note: This is a limitation - we need to modify the calling code to handle this
        
        # IMPORTANT: Only navigate if URL is provided AND it's different from current URL
        # This prevents re-navigation on subsequent requests, preserving the session
        execute_url = None
        if url:
            try:
                current_url = browser_executor.driver.current_url
                if current_url != url and not current_url.startswith(url):
                    logging.info(f"[BROWSER] URL changed from {current_url} to {url}, will navigate")
                    execute_url = url
                else:
                    logging.info(f"[BROWSER] Already on correct URL ({current_url}), skipping navigation to preserve session")
            except:
                # If can't get current URL, navigate to be safe
                execute_url = url
        
        result = browser_executor.execute_code(code, execute_url)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logging.error(f"Error executing in browser: {str(e)}")
        return jsonify({'error': str(e)}), 500

def get_browser_info(browser_executor):
    """Get current browser page information."""
    try:
        if not browser_executor or not browser_executor.driver:
            return jsonify({'success': False, 'error': 'Browser not initialized'}), 400
        
        info = browser_executor.get_page_info()
        
        return jsonify(info), 200
        
    except Exception as e:
        logging.error(f"Error getting browser info: {str(e)}")
        return jsonify({'error': str(e)}), 500

def take_screenshot(browser_executor):
    """Take screenshot of current page."""
    try:
        if not browser_executor or not browser_executor.driver:
            return jsonify({'success': False, 'error': 'Browser not initialized'}), 400
        
        data = request.get_json() or {}
        filename = data.get('filename', 'screenshot.png')
        
        result = browser_executor.take_screenshot(filename)
        
        return jsonify(result), 200 if result.get('success') else 500
        
    except Exception as e:
        logging.error(f"Error taking screenshot: {str(e)}")
        return jsonify({'error': str(e)}), 500

def close_browser(browser_executor):
    """Close browser and cleanup."""
    try:
        if browser_executor:
            browser_executor.close()
            return jsonify({'success': True, 'message': 'Browser closed'}), 200
        else:
            return jsonify({'success': False, 'message': 'Browser not initialized'}), 400
        
    except Exception as e:
        logging.error(f"Error closing browser: {str(e)}")
        return jsonify({'error': str(e)}), 500
