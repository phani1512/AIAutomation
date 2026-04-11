"""
Recording session management and action recording handlers.
"""
import os
import json
import time
import uuid
import logging
from datetime import datetime
from flask import request, jsonify

# Recorder storage
recorded_sessions = {}
active_session_id = None

def start_recording():
    """Start a new recording session."""
    global active_session_id, recorded_sessions
    
    session_id = f"session_{int(time.time())}"
    active_session_id = session_id
    recorded_sessions[session_id] = {
        'name': request.json.get('name', 'Untitled Test'),
        'url': request.json.get('url', ''),
        'module': request.json.get('module', ''),
        'actions': [],
        'created_at': time.time(),
        'active': True,
        'stopped': False
    }
    
    logging.info(f"Started recording session: {session_id} (Module: {request.json.get('module', 'None')})")
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Recording started'
    }), 200

def record_action(generator):
    """Record a user action with smart deduplication and framework detection."""
    # Note: generator parameter kept for API compatibility but not used for locators
    global active_session_id, recorded_sessions
    
    logging.info(f"[RECORD-ACTION] ===== New action received =====")
    logging.info(f"[RECORD-ACTION] Active session: {active_session_id}")
    logging.info(f"[RECORD-ACTION] Available sessions: {list(recorded_sessions.keys())}")
    
    if not active_session_id or active_session_id not in recorded_sessions:
        logging.warning(f"[WARNING] No active recording session. Session ID: {active_session_id}")
        return jsonify({'success': False, 'error': 'No active recording session'}), 400
    
    data = request.json
    action_type = data.get('action_type')
    element_info = data.get('element', {})
    value = data.get('value')
    message_type = data.get('message_type')  # For verify_message actions
    
    logging.info(f"[RECORD-ACTION] Action type: {action_type}, Element: {element_info.get('tagName', '?')}#{element_info.get('id', '?')}")
    
    # Special logging for scroll actions
    if action_type == 'scroll':
        logging.info(f"[SCROLL] Scroll action received with value: {value}")
    
    # Framework Detection - React
    element_id = element_info.get('id', '')
    element_class = element_info.get('className', '') or ''
    
    # Skip React Select internals - they should be recorded as select actions
    if action_type == 'click' and element_id and 'react-select' in element_id and '-option-' in element_id:
        logging.info(f"[SKIP] Ignoring React Select option click: {element_id}")
        return jsonify({
            'success': True,
            'skipped': True,
            'reason': 'React Select option - use select action instead',
            'total_actions': len(recorded_sessions[active_session_id]['actions'])
        }), 200
    
    # Skip clicks on React Select menu elements
    if action_type == 'click' and ('select__option' in element_class or 'select__menu' in element_class):
        logging.info(f"[SKIP] Ignoring React Select menu click: {element_class}")
        return jsonify({
            'success': True,
            'skipped': True,
            'reason': 'React Select menu',
            'total_actions': len(recorded_sessions[active_session_id]['actions'])
        }), 200
    
    # Framework Detection - Vue
    if 'v-' in element_class or element_info.get('data-v-') or element_info.get('vue'):
        logging.info(f"[FRAMEWORK] Detected Vue component")
        element_info['framework'] = 'vue'
    
    # Framework Detection - Angular  
    if any(attr in element_class.lower() for attr in ['ng-', 'ngx-', 'mat-']):
        logging.info(f"[FRAMEWORK] Detected Angular component")
        element_info['framework'] = 'angular'
    
    # Smart Deduplication for input actions
    if action_type in ['input', 'click_and_input']:
        actions_list = recorded_sessions[active_session_id]['actions']
        
        def is_same_element(prev_element, curr_element):
            """Check if two elements are the same using multiple criteria."""
            prev_xpath = prev_element.get('xpath')
            curr_xpath = curr_element.get('xpath')
            if prev_xpath and curr_xpath:
                return prev_xpath == curr_xpath
            
            matches = 0
            if prev_element.get('id') and curr_element.get('id') and prev_element.get('id') == curr_element.get('id'):
                matches += 1
            if prev_element.get('name') and curr_element.get('name') and prev_element.get('name') == curr_element.get('name'):
                matches += 1
            if prev_element.get('tagName') and curr_element.get('tagName') and prev_element.get('tagName') == curr_element.get('tagName'):
                matches += 1
            
            return matches >= 2
        
        # Remove previous input actions for the same element (keep only final value)
        recorded_sessions[active_session_id]['actions'] = [
            a for a in actions_list 
            if not is_same_element(a.get('element', {}), element_info)
        ]
        
        logging.info(f"[REPLACE] Removed previous input actions for element, adding new input with value '{value}'")
    
    # Smart Click Deduplication - prevent rapid duplicate clicks (within 500ms)
    if action_type == 'click':
        actions_list = recorded_sessions[active_session_id]['actions']
        current_time = time.time()
        
        # Check last 2 actions for duplicate clicks within 500ms
        for prev_action in actions_list[-2:]:
            if prev_action['action_type'] == 'click':
                time_diff = current_time - prev_action.get('timestamp', 0)
                
                def is_same_element_click(prev_elem, curr_elem):
                    """Compare elements for click deduplication"""
                    if prev_elem.get('xpath') and curr_elem.get('xpath'):
                        return prev_elem.get('xpath') == curr_elem.get('xpath')
                    
                    # Check multiple attributes
                    same_id = (prev_elem.get('id') and curr_elem.get('id') and 
                              prev_elem.get('id') == curr_elem.get('id'))
                    same_text = (prev_elem.get('text') and curr_elem.get('text') and 
                                prev_elem.get('text') == curr_elem.get('text'))
                    same_tag = prev_elem.get('tagName') == curr_elem.get('tagName')
                    
                    return same_id or (same_text and same_tag)
                
                if is_same_element_click(prev_action.get('element', {}), element_info) and time_diff < 0.5:
                    logging.info(f"[SKIP] Duplicate click detected within {time_diff:.3f}s")
                    return jsonify({
                        'success': True,
                        'skipped': True,
                        'reason': f'Duplicate click within {time_diff:.3f}s',
                        'total_actions': len(recorded_sessions[active_session_id]['actions'])
                    }), 200
    
    action = {
        'step': len(recorded_sessions[active_session_id]['actions']) + 1,
        'action_type': action_type,
        'element': element_info,
        'value': value,
        'timestamp': time.time()
    }
    
    # Add message type for verification actions
    if action_type == 'verify_message':
        action['message_type'] = message_type
        logging.info(f"[VERIFY] Captured {message_type} message: {value}")
    
    # Add target locator for drag_and_drop actions
    if action_type == 'drag_and_drop':
        target_locator = data.get('target_locator')
        if target_locator:
            action['target_locator'] = target_locator
            logging.info(f"[DRAG_DROP] Source → Target: {target_locator}")
    
    # Generate rule-based locator (no external AI used)
    if action_type not in ['verify_message', 'scroll']:
        tag_name = element_info.get('tagName', 'unknown')
        element_text = element_info.get('text', '').strip() if element_info.get('text') else ''
        inner_text = element_info.get('innerText', '').strip() if element_info.get('innerText') else ''
        
        logging.info(f"[DEBUG] Recording {action_type} for tag={tag_name}, text='{element_text}', innerText='{inner_text}'")
        
        suggested_locators = []
        
        # For links (a tags), prioritize linkText
        if tag_name == 'a' and (element_text or inner_text):
            link_text = inner_text or element_text
            suggested_locators.append(f'By.linkText("{link_text}")')
            if len(link_text) > 20:
                suggested_locators.append(f'By.partialLinkText("{link_text[:15]}")')
        
        # For buttons, prioritize text-based locators with normalize-space
        elif tag_name == 'button' and (element_text or inner_text):
            button_text = inner_text or element_text
            
            # Special handling for tab buttons with role='tab'
            if element_info.get('role') == 'tab':
                suggested_locators.append(f"By.xpath('//button[@role=\"tab\"]/span[normalize-space()=\"{button_text}\"]')")
                suggested_locators.append(f"By.xpath('//button[@role=\"tab\" and normalize-space()=\"{button_text}\"]')")
                suggested_locators.append(f"By.xpath('//button[@role=\"tab\"]/span[contains(normalize-space(), \"{button_text}\")]')")
            
            # Use normalize-space for robust text matching
            suggested_locators.append(f"By.xpath('//button[normalize-space()=\"{button_text}\"]')")
            suggested_locators.append(f"By.xpath('//button[contains(normalize-space(), \"{button_text}\")]')")
            suggested_locators.append(f"By.xpath('//*[@role=\"button\" and normalize-space()=\"{button_text}\"]')")
            if element_info.get('type'):
                suggested_locators.append(f"By.xpath('//button[@type=\"{element_info.get('type')}\" and normalize-space()=\"{button_text}\"]')")
        
        # For clickable elements with text (spans, divs, etc with button role)
        elif action_type == 'click' and (element_text or inner_text):
            click_text = inner_text or element_text
            # Prioritize elements with button role first
            if element_info.get('role') in ['button', 'link', 'tab', 'menuitem']:
                suggested_locators.append(f"By.xpath('//{tag_name}[@role=\"{element_info.get('role')}\" and normalize-space()=\"{click_text}\"]')")
                suggested_locators.append(f"By.xpath('//{tag_name}[@role=\"{element_info.get('role')}\"]//span[normalize-space()=\"{click_text}\"]')")
            # Generic text-based with normalize-space
            suggested_locators.append(f"By.xpath('//{tag_name}[normalize-space()=\"{click_text}\"]')")
            suggested_locators.append(f"By.xpath('//{tag_name}[contains(normalize-space(), \"{click_text}\")]')")
        
        # For elements with aria-label
        if element_info.get('ariaLabel'):
            aria_label = element_info.get('ariaLabel')
            suggested_locators.append(f'By.xpath("//{tag_name}[@aria-label=\\"{aria_label}\\"]")')
        
        # For elements with class names
        if element_info.get('className') and len(suggested_locators) < 2:
            class_names = element_info.get('className').strip()
            if class_names:
                # Skip generic Angular/framework classes
                skip_classes = ['ng-valid', 'ng-invalid', 'ng-dirty', 'ng-pristine', 'ng-touched', 'ng-untouched', 
                               'form-control', 'is-valid', 'is-invalid', 'was-validated']
                
                # Filter out generic classes
                filtered_classes = [cls for cls in class_names.split() if cls not in skip_classes]
                
                if filtered_classes:
                    css_class = '.' + '.'.join(filtered_classes)
                    suggested_locators.append(f'By.cssSelector("{css_class}")')
        
        # For input elements, prioritize name, ID, and placeholder
        if tag_name in ['input', 'select', 'textarea']:
            if element_info.get('name'):
                suggested_locators.insert(0, f'By.name("{element_info.get("name")}")')
            if element_info.get('id'):
                suggested_locators.insert(0, f'By.id("{element_info.get("id")}")')
            if element_info.get('placeholder') and len(suggested_locators) < 3:
                placeholder = element_info.get('placeholder')
                suggested_locators.append(f'By.xpath("//{tag_name}[@placeholder=\\"{placeholder}\\"]")')
        
        # For non-input elements, only add ID as fallback
        elif element_info.get('id') and len(suggested_locators) == 0:
            suggested_locators.append(f'By.id("{element_info.get("id")}")')
        
        # Use XPath as final fallback if no locators found
        if not suggested_locators:
            # Generate a simple XPath based on tag name and any unique attribute
            if element_info.get('id'):
                suggested_locators.append(f'By.id("{element_info.get("id")}")')
            elif element_info.get('name'):
                suggested_locators.append(f'By.name("{element_info.get("name")}")')
            else:
                # Generic XPath with tag and index
                suggested_locators.append(f'By.xpath("//{tag_name}")')
        
        action['suggested_locator'] = suggested_locators[0] if suggested_locators else None
        action['alternative_locators'] = suggested_locators[1:4] if len(suggested_locators) > 1 else []
        
        logging.info(f"[LOCATOR] Step {action['step']} ({action_type}): {action['suggested_locator']}")
    
    recorded_sessions[active_session_id]['actions'].append(action)
    
    if action_type == 'scroll':
        logging.info(f"✅ [SCROLL] Recorded scroll action: Step {action['step']}, Position: {value}")
    else:
        logging.info(f"Recorded action: {action['action_type']} (Step {action['step']})")
    
    return jsonify({
        'success': True,
        'action': action,
        'total_actions': len(recorded_sessions[active_session_id]['actions'])
    }), 200

def stop_recording(browser_executor, url_monitor):
    """Stop the current recording session without closing the browser."""
    global active_session_id, recorded_sessions
    
    logging.info(f"[STOP] Attempting to stop recording. Active session ID: {active_session_id}")
    logging.info(f"[STOP] Available sessions: {list(recorded_sessions.keys())}")
    
    if not active_session_id:
        # Try to find the most recent active session
        active_sessions = [sid for sid, sess in recorded_sessions.items() if sess.get('active', False)]
        if active_sessions:
            active_session_id = active_sessions[-1]  # Use most recent
            logging.info(f"[STOP] Found active session by search: {active_session_id}")
        else:
            logging.error("[STOP] No active recording session found")
            return jsonify({'success': False, 'error': 'No active recording session'}), 400
    
    session_id = active_session_id
    
    # Mark session as stopped
    if session_id in recorded_sessions:
        recorded_sessions[session_id]['active'] = False
        recorded_sessions[session_id]['stopped'] = True
        logging.info(f"[STOP] Marked session {session_id} as stopped")
    
    # Stop the recorder in the browser
    if browser_executor and browser_executor.driver:
        try:
            browser_executor.driver.execute_script("if (typeof window.stopRecorderCapture === 'function') { window.stopRecorderCapture(); }")
            logging.info("Stopped recorder in browser")
        except Exception as e:
            logging.warning(f"Could not stop recorder in browser: {e}")
    
    # Stop URL monitoring
    url_monitor.stop()
    
    active_session_id = None
    
    logging.info(f"Stopped recording session: {session_id} - Browser remains open for new test case")
    return jsonify({
        'success': True,
        'session_id': session_id,
        'message': 'Recording stopped. Browser remains open for new test case.'
    }), 200

def get_sessions():
    """Get all active recorded sessions (in-memory only, not saved)."""
    import time
    
    sessions_list = []
    
    # Add in-memory sessions (not yet saved)
    for session_id, session in recorded_sessions.items():
        sessions_list.append({
            'id': session_id,
            'name': session['name'],
            'url': session['url'],
            'module': session.get('module', ''),
            'action_count': len(session['actions']),
            'created_at': session['created_at'],
            'actions': session['actions'],
            'saved': False  # Mark as unsaved
        })
    
    return jsonify({
        'success': True,
        'sessions': sessions_list,
        'server_timestamp': int(time.time()),
        'cache_version': 'v2.2'  # Only active sessions now
    }), 200

def get_session_details(session_id):
    """Get details of a specific session (checks memory and disk)."""
    logging.info(f"[SESSION] Getting details for session: {session_id}")
    logging.info(f"[SESSION] Available in-memory sessions: {list(recorded_sessions.keys())}")
    
    # First check in-memory sessions
    if session_id in recorded_sessions:
        session_data = recorded_sessions[session_id]
        logging.info(f"[SESSION] Found in memory with {len(session_data.get('actions', []))} actions")
        return jsonify({
            'success': True,
            'session': session_data
        }), 200
    
    # Not in memory - check saved tests on disk
    logging.info(f"[SESSION] Not in memory, checking disk...")
    saved_test = load_saved_test_from_disk(session_id)
    
    if saved_test:
        logging.info(f"[SESSION] Found on disk with {len(saved_test.get('actions', []))} actions")
        return jsonify({
            'success': True,
            'session': saved_test
        }), 200
    
    # Not found anywhere
    logging.warning(f"[SESSION] Session {session_id} not found in memory or on disk")
    return jsonify({'success': False, 'error': 'Session not found'}), 404

def clear_sessions():
    """Clear all recorded sessions."""
    global recorded_sessions, active_session_id
    
    recorded_sessions = {}
    active_session_id = None
    
    logging.info("Cleared all recorded sessions")
    return jsonify({
        'success': True,
        'message': 'All sessions cleared'
    }), 200

def delete_session():
    """
    Delete a specific recorded session or saved test case.
    
    Handles both:
    1. In-memory sessions (not yet saved)
    2. Saved test cases on disk (in test_suites/recorded/)
    """
    global recorded_sessions
    
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'}), 400
    
    # First check in-memory sessions (unsaved)
    if session_id in recorded_sessions:
        del recorded_sessions[session_id]
        logging.info(f"[DELETE] Deleted in-memory session: {session_id}")
        return jsonify({'success': True, 'message': 'Session deleted from memory'}), 200
    
    # Not in memory - check if it's a saved test case on disk
    # Search across ALL test type directories (regression, smoke, integration, etc.)
    import glob
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        # Search all test type directories
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general', 'recorded']
        
        for test_type in test_types:
            # Check both new structure (test_suites/{test_type}/recorded/) and old (test_suites/recorded/)
            if test_type == 'recorded':
                # Old structure: test_suites/recorded/*.json
                recorder_pattern = os.path.join(project_root, 'test_suites', 'recorded', '*.json')
            else:
                # New structure: test_suites/{test_type}/recorded/*.json
                recorder_pattern = os.path.join(project_root, 'test_suites', test_type, 'recorded', '*.json')
            
            logging.info(f"[DELETE] Searching for {session_id} in pattern: {recorder_pattern}")
            
            # Search for the test file
            for filepath in glob.glob(recorder_pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                        
                    # Match by test_case_id or session_id
                    if test_data.get('test_case_id') == session_id or test_data.get('session_id') == session_id:
                        # Delete the file
                        os.remove(filepath)
                        logging.info(f"[DELETE] ✓ Deleted saved test case file: {filepath}")
                        return jsonify({
                            'success': True, 
                            'message': 'Saved test case deleted',
                            'filepath': filepath
                        }), 200
                        
                except Exception as e:
                    logging.error(f"[DELETE] Error reading test file {filepath}: {e}")
                    continue
        
        # Not found anywhere
        logging.warning(f"[DELETE] Session/test case not found: {session_id}")
        return jsonify({'success': False, 'error': 'Session not found'}), 404
        
    except Exception as e:
        logging.error(f"[DELETE] Error during deletion: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500

def rename_test(test_case_id):
    """Rename a saved recorder test case."""
    try:
        from flask import request, jsonify
        import json
        import os
        import glob
        
        data = request.get_json() or {}
        new_name = data.get('new_name', '').strip()
        
        if not new_name:
            return jsonify({'error': 'new_name is required'}), 400
        
        logging.info(f"[RENAME] Renaming recorder test {test_case_id} to '{new_name}'")
        
        # Search across ALL test type directories
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general', 'recorded']
        
        for test_type in test_types:
            # Check both new structure and old structure
            if test_type == 'recorded':
                recorder_pattern = os.path.join(project_root, 'test_suites', 'recorded', '*.json')
            else:
                recorder_pattern = os.path.join(project_root, 'test_suites', test_type, 'recorded', '*.json')
            
            logging.info(f"[RENAME] Searching for {test_case_id} in pattern: {recorder_pattern}")
            
            for filepath in glob.glob(recorder_pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                    
                    # Match by test_case_id or session_id
                    if test_data.get('test_case_id') == test_case_id or test_data.get('session_id') == test_case_id:
                        # Update the name
                        test_data['name'] = new_name
                        
                        # Write back to file
                        with open(filepath, 'w', encoding='utf-8') as f:
                            json.dump(test_data, f, indent=2, ensure_ascii=False)
                        
                        logging.info(f"[RENAME] ✓ Updated test name in {filepath}")
                        return jsonify({
                            'success': True,
                            'message': f'Test renamed to "{new_name}"',
                            'new_name': new_name
                        }), 200
                        
                except Exception as e:
                    logging.error(f"[RENAME] Error reading test file {filepath}: {e}")
                    continue
        
        # Not found anywhere
        logging.warning(f"[RENAME] Test case not found: {test_case_id}")
        return jsonify({'error': f'Test case {test_case_id} not found'}), 404
        
    except Exception as e:
        logging.error(f"[RENAME] Error renaming test: {e}", exc_info=True)
        return jsonify({'error': str(e)}), 500

def save_generated_test():
    """Save a generated test to the test suite."""
    global recorded_sessions
    
    logging.info("[SAVE-TEST] save_generated_test function called!")
    
    try:
        data = request.json
        logging.info(f"[SAVE-TEST] Received data: {data}")
        
        test_name = data.get('name', 'Generated_Test')
        module_name = data.get('module', 'SemanticAnalysis')
        code = data.get('code', '')
        language = data.get('language', 'python')
        description = data.get('description', '')
        test_type = data.get('type', 'test')
        priority = data.get('priority', 'medium')
        steps = data.get('steps', [])
        
        if not code:
            return jsonify({'success': False, 'error': 'Code is required'}), 400
        
        # Create a new session for this generated test
        session_id = f"generated_{int(time.time())}_{test_name}"
        
        recorded_sessions[session_id] = {
            'id': session_id,
            'name': test_name,
            'module': module_name,
            'url': 'Generated from Semantic Analysis',
            'actions': [],  # No actions since it's generated
            'generated_code': code,
            'edited_code': code,  # Store as edited code for execution
            'language': language,
            'description': description,
            'type': test_type,
            'priority': priority,
            'steps': steps,
            'timestamp': time.time(),
            'created_at': time.time(),
            'active': False,
            'stopped': True,
            'source': 'semantic_analysis'
        }
        
        logging.info(f"Saved generated test: {test_name} to module: {module_name}")
        
        return jsonify({
            'success': True,
            'session_id': session_id,
            'message': f'Test saved to {module_name} module'
        }), 200
        
    except Exception as e:
        logging.error(f"Error saving generated test: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def save_test_case_to_disk():
    """
    Save a recorded test session as a permanent test case.
    
    NEW: Supports test type organization (regression, smoke, integration, etc.)
    
    Workflow:
    1. Takes session from recorded_sessions (in-memory, temporary)
    2. Saves to test_suites/{test_type}/recorded/ (organized by test type)
    3. Deletes from recorded_sessions (cleanup)
    
    Request body:
    {
        "session_id": "abc123",
        "name": "Login Test",
        "username": "john",
        "test_type": "regression"  // NEW: regression, smoke, integration, etc.
    }
    """
    global recorded_sessions
    
    logging.info("[SAVE-TEST-CASE] save_test_case_to_disk function called!")
    
    try:
        data = request.json
        session_id = data.get('session_id')
        username = data.get('username', 'default_user')
        test_name = data.get('name', 'Recorded_Test')
        test_type = data.get('test_type', 'general')  # NEW: default to 'general'
        
        logging.info(f"[SAVE-TEST-CASE] Session ID: {session_id}, User: {username}, Name: {test_name}, Type: {test_type}")
        
        # Validate session exists
        if not session_id or session_id not in recorded_sessions:
            logging.error(f"[SAVE-TEST-CASE] Session not found: {session_id}")
            return jsonify({
                'success': False, 
                'error': f'Session not found: {session_id}'
            }), 404
        
        # Get session data
        session_data = recorded_sessions[session_id]
        
        # Generate Python test code BEFORE saving (so viewing is instant)
        generated_code = {}
        try:
            from generators.code_generator import generate_test_from_actions
            logging.info(f"[SAVE-TEST-CASE] Generating Python code for {len(session_data.get('actions', []))} actions...")
            
            python_code = generate_test_from_actions(
                actions=session_data.get('actions', []),
                test_name=test_name,
                url=session_data.get('url', ''),
                compact_mode=True  # Compact code for saved tests
            )
            
            generated_code['python'] = python_code
            logging.info(f"[SAVE-TEST-CASE] ✅ Generated Python code ({len(python_code)} chars)")
        except Exception as e:
            logging.error(f"[SAVE-TEST-CASE] Failed to generate code: {e}")
            generated_code['python'] = f"# Error generating code: {str(e)}\n# Test can still be executed using actions"
        
        # Save to test_suites/{test_type}/recorded/ (organized structure)
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        # New structure: test_suites/{test_type}/recorded/
        suite_dir = os.path.join(project_root, 'test_suites', test_type, 'recorded')
        os.makedirs(suite_dir, exist_ok=True)
        
        # Generate test case file (clean name without UUID)
        safe_name = test_name.replace(' ', '_').lower()
        test_case_id = safe_name  # Simple, clean name
        filename = f"{test_case_id}.json"
        filepath = os.path.join(suite_dir, filename)
        
        timestamp = int(time.time())  # Keep for metadata
        
        # Prepare test case data with FULL metadata (same as builder)
        test_case = {
            'test_case_id': test_case_id,
            'name': test_name,
            'description': session_data.get('description', ''),
            'url': session_data.get('url', ''),
            'module': session_data.get('module', ''),
            'test_type': test_type,  # NEW: regression, smoke, integration, etc.
            'source': 'recorded',    # Source: recorder
            'saved_to_suite_at': datetime.now().isoformat(),
            'actions': session_data.get('actions', []),
            'generated_code': generated_code,  # SAVED CODE - no need to regenerate!
            'edited_code': session_data.get('edited_code'),
            'language': session_data.get('language', 'python'),
            'priority': session_data.get('priority', 'medium'),
            'tags': session_data.get('tags', ['recorder', test_type]),
            'created_at': session_data.get('created_at', timestamp),
            'saved_at': timestamp,
            'username': username,
            'status': 'active'
        }
        
        # Write to disk
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(test_case, f, indent=2, ensure_ascii=False)
        
        logging.info(f"[SAVE-TEST-CASE] ✅ Saved to test_suites/{test_type}/recorded/{filename}")
        logging.info(f"[SAVE-TEST-CASE] 🎯 Test Type: {test_type}")
        logging.info(f"[SAVE-TEST-CASE] 📁 Structure: test_suites/{test_type}/recorded/")
        logging.info(f"[SAVE-TEST-CASE] 🤖 ML will learn from this test on next training cycle")
        logging.info(f"[SAVE-TEST-CASE] 👤 User: {username}")
        
        # Delete from in-memory sessions (cleanup)
        del recorded_sessions[session_id]
        logging.info(f"[SAVE-TEST-CASE] 🗑️  Deleted session from memory: {session_id}")
        
        return jsonify({
            'success': True,
            'test_case_id': test_case_id,
            'filepath': filepath,
            'test_type': test_type,
            'message': f'Test case saved successfully to test_suites/{test_type}/recorded/'
        }), 200
        
    except Exception as e:
        logging.error(f"[SAVE-TEST-CASE] ❌ Error: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def list_saved_recorder_tests():
    """
    List all saved recorder test cases.
    Scans test_suites/{test_type}/recorded/ directories for all test types.
    Also scans test_suites/semantic-generated/ for AI-generated test variants.
    """
    import glob
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        # Test types to scan
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general']
        
        test_cases = []
        
        # Scan all test type folders
        for test_type in test_types:
            recorder_pattern = os.path.join(project_root, 'test_suites', test_type, 'recorded', '*.json')
            
            for filepath in glob.glob(recorder_pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                        
                        # Get timestamp - handle both seconds and milliseconds
                        timestamp = test_data.get('saved_at', test_data.get('created_at', 0))
                        timestamp_ms = timestamp * 1000 if len(str(int(timestamp))) <= 10 else timestamp
                        
                        test_cases.append({
                            'test_case_id': test_data.get('test_case_id'),
                            'name': test_data.get('name'),
                            'url': test_data.get('url', ''),
                            'module': test_data.get('module', 'Test Recorder'),
                            'test_type': test_data.get('test_type', test_type),  # Include test_type
                            'action_count': len(test_data.get('actions', [])),
                            'actions': test_data.get('actions', []),  # Include full actions array
                            'created_at': timestamp_ms,
                            'timestamp': timestamp_ms,
                            'username': test_data.get('username', 'unknown'),
                            'source': 'recorder',
                            'status': test_data.get('status', 'active'),
                            'priority': test_data.get('priority', 'medium'),
                            'tags': test_data.get('tags', ['recorder']),
                            'steps': test_data.get('steps', []),  # Include AI suggestions for semantic tests
                            'generated_code': test_data.get('generated_code'),  # Include for code parsing fallback
                            'filepath': filepath
                        })
                except Exception as e:
                    logging.error(f"[RECORDER-TESTS] Error reading test case: {filepath}, {e}")
                    continue
        
        # ALSO scan semantic-generated folder for AI-generated test variants
        semantic_pattern = os.path.join(project_root, 'test_suites', 'semantic-generated', '*.json')
        for filepath in glob.glob(semantic_pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                    
                    # Get timestamp - handle both seconds and milliseconds
                    timestamp = test_data.get('saved_at', test_data.get('created_at', 0))
                    timestamp_ms = timestamp * 1000 if len(str(int(timestamp))) <= 10 else timestamp
                    
                    test_cases.append({
                        'test_case_id': test_data.get('test_case_id'),
                        'name': test_data.get('name'),
                        'url': test_data.get('url', ''),
                        'module': test_data.get('module', 'Semantic Analysis'),
                        'test_type': test_data.get('test_type', 'general'),
                        'action_count': len(test_data.get('actions', [])),
                        'actions': test_data.get('actions', []),
                        'created_at': timestamp_ms,
                        'timestamp': timestamp_ms,
                        'username': test_data.get('username', 'unknown'),
                        'source': test_data.get('source', 'semantic-generated'),
                        'variant_type': test_data.get('variant_type', 'generated'),
                        'source_test_id': test_data.get('source_test_id'),
                        'status': test_data.get('status', 'active'),
                        'priority': test_data.get('priority', 'medium'),
                        'tags': test_data.get('tags', ['semantic', 'ai-generated']),
                        'steps': test_data.get('steps', []),  # Include AI suggestions for semantic tests
                        'generated_code': test_data.get('generated_code'),  # Include for code parsing fallback
                        'filepath': filepath
                    })
            except Exception as e:
                logging.error(f"[RECORDER-TESTS] Error reading semantic test: {filepath}, {e}")
                continue
        
        # Sort by timestamp (newest first)
        test_cases.sort(key=lambda x: x['created_at'], reverse=True)
        
        logging.info(f"[RECORDER-TESTS] Found {len(test_cases)} saved recorder test cases")
        
        return jsonify({
            'success': True,
            'test_cases': test_cases,
            'count': len(test_cases)
        }), 200
        
    except Exception as e:
        logging.error(f"[RECORDER-TESTS] Error listing recorder tests: {e}", exc_info=True)
        return jsonify({'success': False, 'error': str(e)}), 500


def load_saved_test_from_disk(session_id):
    """
    Load a saved recorder test from disk by session_id or test_case_id.
    Returns session data structure compatible with recorded_sessions format.
    
    NEW: Scans test_suites/{test_type}/recorded/ directories
    
    Args:
        session_id: The test_case_id or session_id to load
        
    Returns:
        dict: Session data structure or None if not found
    """
    import glob
    
    try:
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        
        # NEW: Scan all test type folders
        test_types = ['regression', 'smoke', 'integration', 'performance', 'security', 'exploratory', 'general']
        
        for test_type in test_types:
            recorder_pattern = os.path.join(project_root, 'test_suites', test_type, 'recorded', '*.json')
            
            # Search for test file matching the session_id
            for filepath in glob.glob(recorder_pattern):
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        test_data = json.load(f)
                    
                    # Match by test_case_id or session_id
                    if test_data.get('test_case_id') == session_id or test_data.get('session_id') == session_id:
                        logging.info(f"[RECORDER] Loaded saved test from disk: {filepath}")
                        
                        # Return in the format expected by execute_test()
                        return {
                            'name': test_data.get('name', 'Untitled Test'),
                            'url': test_data.get('url', ''),
                            'module': test_data.get('module', 'Test Recorder'),
                            'actions': test_data.get('actions', []),
                            'generated_code': test_data.get('generated_code', {}),  # NEW: Include generated code
                            'created_at': test_data.get('saved_at', test_data.get('created_at', time.time())),
                            'active': False,
                            'stopped': True,
                            'edited_code': test_data.get('edited_code'),
                            'username': test_data.get('username', 'unknown'),
                            'status': test_data.get('status', 'active'),
                            'priority': test_data.get('priority', 'medium'),
                            'tags': test_data.get('tags', ['recorder'])
                        }
                except Exception as e:
                    logging.error(f"[RECORDER] Error reading test file {filepath}: {e}")
                    continue
        
        # ALSO check semantic-generated folder
        semantic_pattern = os.path.join(project_root, 'test_suites', 'semantic-generated', '*.json')
        for filepath in glob.glob(semantic_pattern):
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                
                # Match by test_case_id or session_id
                if test_data.get('test_case_id') == session_id or test_data.get('session_id') == session_id:
                    logging.info(f"[RECORDER] Loaded semantic test from disk: {filepath}")
                    
                    # Return in the format expected by execute_test()
                    return {
                        'name': test_data.get('name', 'Untitled Test'),
                        'url': test_data.get('url', ''),
                        'module': test_data.get('module', 'Semantic Analysis'),
                        'actions': test_data.get('actions', []),
                        'generated_code': test_data.get('generated_code', {}),
                        'created_at': test_data.get('saved_at', test_data.get('created_at', time.time())),
                        'active': False,
                        'stopped': True,
                        'edited_code': test_data.get('edited_code'),
                        'username': test_data.get('username', 'unknown'),
                        'status': test_data.get('status', 'active'),
                        'priority': test_data.get('priority', 'medium'),
                        'tags': test_data.get('tags', ['semantic', 'ai-generated']),
                        'variant_type': test_data.get('variant_type'),
                        'source_test_id': test_data.get('source_test_id')
                    }
            except Exception as e:
                logging.error(f"[RECORDER] Error reading semantic test file {filepath}: {e}")
                continue
        
        # Not found
        logging.info(f"[RECORDER] Saved test not found on disk: {session_id} (may exist in builder)")
        return None
        
    except Exception as e:
        logging.error(f"[RECORDER] Error loading saved test: {e}", exc_info=True)
        return None


def get_browser_status(session_id, browser_executor):
    """Get live browser status for recorder monitoring.
    
    Args:
        session_id: The session ID to check
        browser_executor: The global browser executor instance
    
    Returns:
        JSON response with browser status
    """
    try:
        # Verify session exists
        if session_id not in recorded_sessions:
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
        session = recorded_sessions[session_id]
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


def focus_browser(browser_executor):
    """Bring browser window to front.
    
    Args:
        browser_executor: The global browser executor instance
    
    Returns:
        JSON response confirming browser focused
    """
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
