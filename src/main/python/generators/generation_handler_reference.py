"""
Test Suite Handler - Multi-Prompt Test Suite Endpoints (PHASE 0)
Handles test session management, prompt building, and test case operations.
"""
import logging
from flask import request, jsonify


def start_test_session(get_session_manager_func):
    """Start a new test creation session."""
    try:
        data = request.get_json()
        name = data.get('name', '')
        description = data.get('description', '')
        
        if not name:
            return jsonify({'error': 'Test name is required'}), 400
        
        session_manager = get_session_manager_func()
        session = session_manager.create_session(name, description)
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error starting session: {str(e)}")
        return jsonify({'error': str(e)}), 500


def add_prompt_to_session(session_id, get_session_manager_func, get_generator_func):
    """Add a prompt to an existing test session - generates code WITHOUT opening browser.
    
    Supports configurable comprehensive mode via 'use_comprehensive_mode' parameter.
    - Default: False (simple, fast code for prototyping)
    - True: Comprehensive code with WebDriverWait and error handling (production-ready)
    """
    try:
        data = request.get_json()
        prompt = data.get('prompt', '')
        url = data.get('url')
        value = data.get('value')  # Get data value from user
        language = data.get('language', 'python')
        # Configurable comprehensive mode (default=False for backward compatibility)
        use_comprehensive_mode = data.get('use_comprehensive_mode', False)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        # Get session
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        # Multi-strategy intelligent matching
        # Try: 1) Exact match, 2) Template match, 3) Fuzzy match, 4) ML inference
        from semantic_analysis.intelligent_prompt_matcher import get_matcher
        matcher = get_matcher()
        match_result = matcher.match(prompt)
        
        # Generate code based on match strategy
        if match_result['strategy'] in ['exact', 'template', 'fuzzy']:
            # High-confidence match from dataset
            generated_code = match_result['code']
            xpath_locator = match_result['xpath']
            confidence = match_result['confidence']
            strategy = match_result['strategy']
            explanation = match_result['explanation']
            
            logging.info(f"[TEST BUILDER] {strategy.upper()} MATCH ({confidence:.1%}): {prompt}")
            logging.info(f"[TEST BUILDER] {explanation}")
            
            # Get alternative suggestions for UI
            alternatives = matcher.get_match_suggestions(prompt, limit=3)
        else:
            # ML inference fallback for novel prompts
            logging.info(f"[TEST BUILDER] ML INFERENCE (no high-confidence match): {prompt}")
            gen = get_generator_func()
            generated_code = gen.generate_clean(
                prompt, 
                max_tokens=50, 
                temperature=0.3, 
                language=language, 
                comprehensive_mode=use_comprehensive_mode
            )
            xpath_locator = ''
            confidence = 0.5
            strategy = 'ml'
            explanation = 'No dataset match found, using ML inference'
            alternatives = gen.get_last_alternatives()
        
        # Create result object with match information
        result = {
            'code': generated_code,
            'xpath': xpath_locator,
            'alternatives': alternatives,
            'match_strategy': strategy,  # Show which strategy was used
            'match_confidence': confidence,  # Show confidence score
            'match_explanation': explanation,  # Human-readable explanation
            'parameters': match_result.get('parameters', {}),  # Extracted parameters
            'parsed': {
                'action': 'unknown',
                'element': 'element',
                'confidence': confidence,
                'original_prompt': prompt,
                'match_strategy': strategy  # Include in parsed for reference
            },
            'resolved_element': None,
            'success': True,
            'message': f'{explanation}'
        }
        
        # Add to session
        step_number = session.add_prompt(
            prompt=prompt,
            url=url,
            value=value,  # Pass data value
            parsed=result.get('parsed'),
            resolved_element=result.get('resolved_element'),
            generated_code=result.get('code')
        )
        
        logging.info(f"[TEST BUILDER] Added step {step_number} to session {session_id} - Code generated, browser NOT opened")
        
        return jsonify({
            'success': True,
            'step_number': step_number,
            'step_result': result,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error adding prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500


def remove_prompt_from_session(session_id, get_session_manager_func):
    """Remove a prompt step from the session."""
    try:
        data = request.get_json()
        step_number = data.get('step_number')
        
        if not step_number:
            return jsonify({'error': 'step_number is required'}), 400
        
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        success = session.remove_prompt(int(step_number))
        
        if not success:
            return jsonify({'error': f'Invalid step number: {step_number}'}), 400
        
        logging.info(f"[TEST BUILDER] Removed step {step_number} from session {session_id}")
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error removing prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500


def update_prompt_in_session(session_id, get_session_manager_func, get_generator_func):
    """Update an existing prompt step."""
    try:
        data = request.get_json()
        step_number = data.get('step_number')
        prompt = data.get('prompt', '')
        url = data.get('url')
        use_comprehensive_mode = data.get('use_comprehensive_mode', False)
        language = data.get('language', 'python')
        
        if not step_number or not prompt:
            return jsonify({'error': 'step_number and prompt are required'}), 400
        
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        # Regenerate code for updated prompt
        gen = get_generator_func()
        generated_code = gen.generate_clean(
            prompt,
            max_tokens=50,
            temperature=0.3,
            language=language,
            comprehensive_mode=use_comprehensive_mode
        )
        
        # Get alternatives
        alternatives = gen.get_last_alternatives()
        
        # Update the step
        if 0 < int(step_number) <= len(session.prompts):
            session.prompts[int(step_number) - 1]['prompt'] = prompt
            session.prompts[int(step_number) - 1]['generated_code'] = generated_code
            if url:
                session.prompts[int(step_number) - 1]['url'] = url
            
            logging.info(f"[TEST BUILDER] Updated step {step_number} in session {session_id}")
            
            return jsonify({
                'success': True,
                'session': session.to_dict(),
                'alternatives': alternatives
            }), 200
        else:
            return jsonify({'error': f'Invalid step number: {step_number}'}), 400
        
    except Exception as e:
        logging.error(f"Error updating prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500


def reorder_prompt_in_session(session_id, get_session_manager_func):
    """Reorder a prompt step (move up or down)."""
    try:
        data = request.get_json()
        from_step = data.get('from_step')
        to_step = data.get('to_step')
        
        if not from_step or not to_step:
            return jsonify({'error': 'from_step and to_step are required'}), 400
        
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        success = session.reorder_prompt(int(from_step), int(to_step))
        
        if not success:
            return jsonify({'error': f'Invalid step numbers: {from_step} -> {to_step}'}), 400
        
        logging.info(f"[TEST BUILDER] Reordered step {from_step} to {to_step} in session {session_id}")
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error reordering prompt: {str(e)}")
        return jsonify({'error': str(e)}), 500


def get_test_session(session_id, get_session_manager_func):
    """Get test session details."""
    try:
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'success': False, 'error': f'Session {session_id} not found'}), 404
        
        return jsonify({
            'success': True,
            'session': session.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting session: {str(e)}")
        return jsonify({'success': False, 'error': str(e)}), 500


def delete_test_session(session_id, get_session_manager_func):
    """Delete a test session."""
    try:
        session_manager = get_session_manager_func()
        success = session_manager.delete_session(session_id)
        
        if not success:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logging.error(f"Error deleting session: {str(e)}")
        return jsonify({'error': str(e)}), 500


def preview_test_code(session_id, get_session_manager_func):
    """Preview generated code for entire test session."""
    try:
        language = request.args.get('language', 'python')
        
        session_manager = get_session_manager_func()
        code = session_manager.preview_code(session_id, language)
        
        if code is None:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        return jsonify({
            'success': True,
            'language': language,
            'code': code
        }), 200
        
    except Exception as e:
        logging.error(f"Error previewing code: {str(e)}")
        return jsonify({'error': str(e)}), 500


def save_test_case(session_id, get_session_manager_func, get_test_case_builder_func, get_generator_func):
    """Save test session as executable test case."""
    try:
        data = request.get_json() or {}
        tags = data.get('tags', [])
        priority = data.get('priority', 'medium')
        test_case_id = data.get('test_case_id')
        
        # Get session
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        # Generate code for each step using inference engine
        generator = get_generator_func()
        session_dict = session.to_dict()
        
        for step in session_dict.get('prompts', []):
            prompt = step['prompt']
            logging.info(f"[SAVE] Generating code for step {step['step']}: {prompt}")
            
            try:
                # Generate code from prompt
                result = generator.infer(prompt, return_alternatives=False)
                if result and 'code' in result:
                    step['generated_code'] = result['code']
                    step['xpath'] = result.get('xpath', '')
                    logging.info(f"[SAVE] Code generated for step {step['step']}")
                else:
                    logging.warning(f"[SAVE] No code generated for step {step['step']}")
                    step['generated_code'] = f"# TODO: Implement - {prompt}"
            except Exception as e:
                logging.error(f"[SAVE] Error generating code for step {step['step']}: {e}")
                step['generated_code'] = f"# ERROR: {str(e)}"
        
        # Build test case
        builder = get_test_case_builder_func()
        test_case = builder.build_from_session(
            session_dict,
            test_case_id=test_case_id,
            tags=tags,
            priority=priority
        )
        
        # Save to file
        filepath = builder.save_test_case(test_case)
        
        # Link test case to session
        session.test_case_id = test_case.test_case_id
        logging.info(f"[SAVE] Linked session {session_id} to test case {test_case.test_case_id}")
        
        logging.info(f"[SAVE] Test case saved: {test_case.test_case_id} to {filepath}")
        
        return jsonify({
            'success': True,
            'test_case': test_case.to_dict(),
            'filepath': filepath
        }), 200
        
    except Exception as e:
        logging.error(f"Error saving test case: {str(e)}")
        import traceback
        traceback.print_exc()
        return jsonify({'error': str(e)}), 500


def list_test_sessions(get_session_manager_func):
    """List all active test sessions."""
    try:
        session_manager = get_session_manager_func()
        sessions = session_manager.list_active_sessions()
        
        return jsonify({
            'success': True,
            'sessions': sessions,
            'count': len(sessions)
        }), 200
        
    except Exception as e:
        logging.error(f"Error listing sessions: {str(e)}")
        return jsonify({'error': str(e)}), 500


def list_test_cases(get_test_case_builder_func):
    """List all saved test cases."""
    try:
        tags = request.args.getlist('tags')
        priority = request.args.get('priority')
        status = request.args.get('status', 'active')
        
        builder = get_test_case_builder_func()
        test_cases = builder.list_test_cases(tags=tags, priority=priority, status=status)
        
        return jsonify({
            'success': True,
            'test_cases': test_cases,
            'count': len(test_cases)
        }), 200
        
    except Exception as e:
        logging.error(f"Error listing test cases: {str(e)}")
        return jsonify({'error': str(e)}), 500


def get_test_case(test_case_id, get_test_case_builder_func):
    """Get test case details."""
    try:
        builder = get_test_case_builder_func()
        test_case = builder.load_test_case(test_case_id)
        
        if not test_case:
            return jsonify({'error': f'Test case {test_case_id} not found'}), 404
        
        return jsonify({
            'success': True,
            'test_case': test_case.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error getting test case: {str(e)}")
        return jsonify({'error': str(e)}), 500


def delete_test_case_endpoint(test_case_id, get_test_case_builder_func):
    """Delete a test case."""
    try:
        builder = get_test_case_builder_func()
        success = builder.delete_test_case(test_case_id)
        
        if not success:
            return jsonify({'error': f'Test case {test_case_id} not found'}), 404
        
        return jsonify({'success': True}), 200
        
    except Exception as e:
        logging.error(f"Error deleting test case: {str(e)}")
        return jsonify({'error': str(e)}), 500


def execute_test_case(test_case_id, get_test_runner_func):
    """Execute a saved test case."""
    try:
        data = request.get_json() or {}
        headless = data.get('headless', False)
        data_overrides = data.get('data_overrides', {})
        
        runner = get_test_runner_func()
        result = runner.execute_test_case(test_case_id, headless=headless, data_overrides=data_overrides)
        
        return jsonify({
            'success': True,
            'result': result.to_dict()
        }), 200
        
    except Exception as e:
        logging.error(f"Error executing test case: {str(e)}")
        return jsonify({'error': str(e)}), 500


def execute_test_suite(get_test_runner_func):
    """Execute multiple test cases."""
    try:
        data = request.get_json()
        test_case_ids = data.get('test_case_ids', [])
        parallel = data.get('parallel', False)
        max_workers = data.get('max_workers', 3)
        
        if not test_case_ids:
            return jsonify({'error': 'test_case_ids is required'}), 400
        
        runner = get_test_runner_func()
        results = runner.execute_suite(test_case_ids, parallel=parallel, max_workers=max_workers)
        
        # Generate report
        report_path = runner.generate_report(results)
        
        return jsonify({
            'success': True,
            'results': [r.to_dict() for r in results],
            'report_path': report_path,
            'summary': {
                'total': len(results),
                'passed': sum(1 for r in results if r.status == 'passed'),
                'failed': sum(1 for r in results if r.status == 'failed'),
                'errors': sum(1 for r in results if r.status == 'error')
            }
        }), 200
        
    except Exception as e:
        logging.error(f"Error executing test suite: {str(e)}")
        return jsonify({'error': str(e)}), 500
