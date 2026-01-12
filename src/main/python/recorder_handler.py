"""
Recording session management and action recording handlers.
"""
import time
import uuid
import logging
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
    """Record a user action."""
    global active_session_id, recorded_sessions
    
    logging.info(f"[DEBUG] Received record-action request. Active session: {active_session_id}")
    
    if not active_session_id or active_session_id not in recorded_sessions:
        logging.warning(f"[WARNING] No active recording session. Session ID: {active_session_id}")
        return jsonify({'success': False, 'error': 'No active recording session'}), 400
    
    data = request.json
    action_type = data.get('action_type')
    element_info = data.get('element', {})
    value = data.get('value')
    message_type = data.get('message_type')  # For verify_message actions
    
    # Skip React Select option clicks - they should be recorded as select actions
    element_id = element_info.get('id', '')
    if action_type == 'click' and element_id and 'react-select' in element_id and '-option-' in element_id:
        logging.info(f"[SKIP] Ignoring React Select option click: {element_id}")
        return jsonify({
            'success': True,
            'skipped': True,
            'reason': 'React Select option - use select action instead',
            'total_actions': len(recorded_sessions[active_session_id]['actions'])
        }), 200
    
    # Skip clicks on elements with react-select menu classes
    element_class = element_info.get('className', '') or ''
    if action_type == 'click' and ('select__option' in element_class or 'select__menu' in element_class):
        logging.info(f"[SKIP] Ignoring React Select menu click: {element_class}")
        return jsonify({
            'success': True,
            'skipped': True,
            'reason': 'React Select menu',
            'total_actions': len(recorded_sessions[active_session_id]['actions'])
        }), 200
    
    # For input actions (including click_and_input), keep only the last value for each element
    if action_type in ['input', 'click_and_input']:
        element_id = element_info.get('xpath') or element_info.get('id') or element_info.get('name')
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
        
        recorded_sessions[active_session_id]['actions'] = [
            a for a in actions_list 
            if not is_same_element(a.get('element', {}), element_info)
        ]
        
        logging.info(f"[REPLACE] Removed previous actions for element {element_id}, adding new input with value '{value}'")
    
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
    
    # Get AI-suggested locator (skip for verify_message as they don't need locators)
    if action_type != 'verify_message':
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
        
        # For buttons, prioritize text-based locators
        elif tag_name == 'button' and (element_text or inner_text):
            button_text = inner_text or element_text
            suggested_locators.append(f'By.xpath("//button[contains(normalize-space(.), \\"{button_text}\\")]")')
            if element_info.get('type'):
                suggested_locators.append(f'By.xpath("//button[@type=\\"{element_info.get("type")}\\"]")')
        
        # For clickable elements with text
        elif action_type == 'click' and (element_text or inner_text) and tag_name not in ['input', 'select', 'textarea']:
            click_text = inner_text or element_text
            suggested_locators.append(f'By.xpath("//{tag_name}[contains(normalize-space(.), \\"{click_text}\\")]")')
        
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
        
        # Fall back to AI-suggested locators
        if not suggested_locators or len(suggested_locators) < 3:
            ai_locators = generator.suggest_locator(
                element_type=tag_name,
                action=data.get('action_type', 'click'),
                attributes=element_info
            )
            for loc in ai_locators:
                if loc not in suggested_locators:
                    suggested_locators.append(loc)
        
        action['suggested_locator'] = suggested_locators[0] if suggested_locators else None
        action['alternative_locators'] = suggested_locators[1:4] if len(suggested_locators) > 1 else []
        
        logging.info(f"[LOCATOR] Step {action['step']} ({action_type}): {action['suggested_locator']}")
    
    recorded_sessions[active_session_id]['actions'].append(action)
    
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
    """Get all recorded sessions."""
    import time
    sessions_list = []
    for session_id, session in recorded_sessions.items():
        sessions_list.append({
            'id': session_id,
            'name': session['name'],
            'url': session['url'],
            'module': session.get('module', ''),
            'action_count': len(session['actions']),
            'created_at': session['created_at'],
            'actions': session['actions']
        })
    
    return jsonify({
        'success': True,
        'sessions': sessions_list,
        'server_timestamp': int(time.time()),  # Cache-busting timestamp
        'cache_version': 'v2.0'  # Increment this to force frontend cache clear
    }), 200

def get_session_details(session_id):
    """Get details of a specific session."""
    logging.info(f"[SESSION] Getting details for session: {session_id}")
    logging.info(f"[SESSION] Available sessions: {list(recorded_sessions.keys())}")
    
    if session_id not in recorded_sessions:
        logging.warning(f"[SESSION] Session {session_id} not found")
        return jsonify({'success': False, 'error': 'Session not found'}), 404
    
    session_data = recorded_sessions[session_id]
    logging.info(f"[SESSION] Returning session with {len(session_data.get('actions', []))} actions")
    
    return jsonify({
        'success': True,
        'session': session_data
    }), 200

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
    """Delete a specific recorded session."""
    global recorded_sessions
    
    data = request.json
    session_id = data.get('session_id')
    
    if not session_id:
        return jsonify({'success': False, 'error': 'Session ID required'}), 400
    
    if session_id in recorded_sessions:
        del recorded_sessions[session_id]
        logging.info(f"Deleted session: {session_id}")
        return jsonify({'success': True, 'message': 'Session deleted'}), 200
    else:
        return jsonify({'success': False, 'error': 'Session not found'}), 404

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
