"""
Test Suite Handler - Multi-Prompt Test Suite Endpoints (PHASE 0)
Handles test session management, prompt building, and test case operations.
"""
import logging
from flask import request, jsonify
from functools import lru_cache
import hashlib


# LRU cache for prompt inference results (speeds up test builder significantly)
_inference_cache = {}
_cache_max_size = 100


def _get_cached_inference(prompt: str, gen):
    """Get cached inference result for common prompts."""
    # Create cache key from prompt
    cache_key = prompt.strip().lower()
    
    # Check cache
    if cache_key in _inference_cache:
        logging.info(f"[CACHE HIT] Using cached result for: {prompt[:50]}")
        return _inference_cache[cache_key]
    
    # Not in cache - do inference
    logging.info(f"[CACHE MISS] Generating code for: {prompt[:50]}")
    infer_result = gen.infer(
        prompt, 
        return_alternatives=True,
        language='python',
        preserve_data_placeholder=True,
        comprehensive_mode=False,
        compact_mode=False,
        ignore_fallbacks=False
    )
    
    # Cache the result (limit cache size)
    if len(_inference_cache) >= _cache_max_size:
        # Remove oldest entry (FIFO)
        first_key = next(iter(_inference_cache))
        del _inference_cache[first_key]
    
    _inference_cache[cache_key] = infer_result
    return infer_result


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
        
        # Use CACHED inference for performance (test builder speed optimization)
        print(f"[TEST BUILDER] Generating Python code for: {prompt}", flush=True)
        gen = get_generator_func()
        
        # Use cached inference to speed up repeated/similar prompts
        infer_result = _get_cached_inference(prompt, gen)
        
        if infer_result and 'code' in infer_result:
            generated_code = infer_result['code']
            xpath_locator = infer_result.get('xpath', '')
            alternatives = infer_result.get('alternatives', [])
            print(f"[TEST BUILDER] ✅ Generated code for '{prompt}': {generated_code[:80]}...", flush=True)
        else:
            # Fallback
            print(f"[TEST BUILDER] ❌ AI failed to generate code for '{prompt}' - using placeholder", flush=True)
            generated_code = f"# TODO: Implement - {prompt}"
            xpath_locator = ''
            alternatives = []
        
        # Keep match info for UI display only
        confidence = match_result.get('confidence', 0.5)
        strategy = match_result.get('strategy', 'ml')
        explanation = match_result.get('explanation', 'Generated Python code')
        
        logging.info(f"[TEST BUILDER] Generated Python code successfully")
        
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
        name = data.get('name')
        tags = data.get('tags', [])
        priority = data.get('priority', 'medium')
        test_case_id = data.get('test_case_id')
        test_type = data.get('test_type', 'general')  # NEW: Test type classification
        
        # Get session
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        # Update session name if provided
        if name:
            session.name = name
        
        # Generate code for each step using inference engine
        generator = get_generator_func()
        session_dict = session.to_dict()
        
        for step in session_dict.get('prompts', []):
            prompt = step['prompt']
            logging.info(f"[SAVE] Generating Python code for step {step['step']}: {prompt}")
            
            try:
                # Generate Python code from prompt (for direct execution)
                # preserve_data_placeholder=True to keep {VALUE} for input fields
                # Use fallback selectors - prompts need multiple selector options
                result = generator.infer(
                    prompt, 
                    return_alternatives=False, 
                    language='python',
                    preserve_data_placeholder=True,  # Keep {VALUE} placeholder for UI substitution
                    comprehensive_mode=False,  # Simple code
                    compact_mode=False,  # Standard fallback mode
                    ignore_fallbacks=False  # USE fallback_selectors for robust prompt matching
                )
                if result and 'code' in result:
                    step['generated_code'] = result['code']
                    step['xpath'] = result.get('xpath', '')
                    logging.info(f"[SAVE] Python code generated for step {step['step']}")
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
            priority=priority,
            compact_mode=True  # Enable compact code generation (70% smaller)
        )
        
        # Save to file with test type classification
        filepath = builder.save_test_case(test_case, test_type=test_type)  # NEW: Pass test_type
        
        # Link test case to session
        session.test_case_id = test_case.test_case_id
        logging.info(f"[SAVE] Linked session {session_id} to test case {test_case.test_case_id}")
        logging.info(f"[SAVE] Test case saved: {test_case.test_case_id} to {filepath}")
        logging.info(f"[SAVE] 🎯 Test Type: {test_type}")  # NEW
        
        return jsonify({
            'success': True,
            'test_case': test_case.to_dict(),
            'filepath': filepath,
            'test_type': test_type  # NEW: Return test type
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


def rename_test_case(test_case_id, get_test_case_builder_func):
    """Rename a test case."""
    try:
        from pathlib import Path
        import json
        import os
        
        data = request.get_json() or {}
        new_name = data.get('new_name', '').strip()
        
        if not new_name:
            return jsonify({'error': 'new_name is required'}), 400
        
        logging.info(f"[RENAME] Renaming test {test_case_id} to '{new_name}'")
        
        builder = get_test_case_builder_func()
        test_case = builder.load_test_case(test_case_id)
        
        if not test_case:
            return jsonify({'error': f'Test case {test_case_id} not found'}), 404
        
        # Update the test case name
        test_case.name = new_name
        
        # Find the JSON file and update it - use project_root from builder instance
        project_root = builder.project_root
        
        # Search for test in all test type directories
        test_types = ['regression', 'smoke', 'integration', 'performance', 
                      'security', 'exploratory', 'general']
        
        file_found = False
        for test_type in test_types:
            builder_dir = project_root / "test_suites" / test_type / "builder"
            if not builder_dir.exists():
                continue
            
            # Look for the test file
            for file_path in builder_dir.glob(f"{test_case_id}*.json"):
                logging.info(f"[RENAME] Found test file: {file_path}")
                
                # Read existing JSON
                with open(file_path, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                
                # Update name
                test_data['name'] = new_name
                
                # Write back
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(test_data, f, indent=2, ensure_ascii=False)
                
                logging.info(f"[RENAME] ✓ Updated test name in {file_path}")
                file_found = True
                break
            
            if file_found:
                break
        
        if not file_found:
            return jsonify({'error': f'Test case file for {test_case_id} not found on disk'}), 404
        
        # Clear cache to reload updated test
        builder.test_cases.clear()
        
        return jsonify({
            'success': True,
            'message': f'Test renamed to "{new_name}"',
            'new_name': new_name
        }), 200
        
    except Exception as e:
        logging.error(f"[RENAME] Error renaming test case: {str(e)}")
        return jsonify({'error': str(e)}), 500


def execute_test_case(test_case_id, get_test_runner_func):
    """Execute a saved test case using step-by-step execution (with Angular wait)."""
    try:
        data = request.get_json() or {}
        headless = data.get('headless', False)
        browser = data.get('browser', 'chrome')
        data_overrides = data.get('data_overrides', {})
        execution_mode = data.get('execution_mode', 'json_steps')  # Default to step-by-step
        
        logging.info(f"[EXECUTE] Test: {test_case_id}, Browser: {browser}, Mode: {execution_mode}")
        
        runner = get_test_runner_func()
        result = runner.execute_test_case(
            test_case_id, 
            headless=headless, 
            browser_name=browser, 
            data_overrides=data_overrides,
            execution_mode=execution_mode  # Use step-by-step with Angular wait
        )
        
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


def execute_session_directly(session_id, get_session_manager_func, get_generator_func):
    """Execute a session's prompts directly without saving (Test Builder quick execution)."""
    try:
        from browser.browser_executor import BrowserExecutor
        import time
        
        data = request.get_json() or {}
        headless = data.get('headless', False)
        data_overrides = data.get('data_overrides', {})  # Get overrides from request
        
        # Get session
        session_manager = get_session_manager_func()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        if not session.prompts or len(session.prompts) == 0:
            return jsonify({'error': 'Session has no steps to execute'}), 400
        
        logging.info(f"[EXECUTE SESSION] Starting execution of session {session_id}")
        logging.info(f"[EXECUTE SESSION] Test: {session.name}")
        logging.info(f"[EXECUTE SESSION] Steps: {len(session.prompts)}")
        
        # Apply data overrides to prompts
        if data_overrides:
            logging.info(f"[EXECUTE SESSION] Applying data overrides: {data_overrides}")
            for prompt_index_str, new_value in data_overrides.items():
                prompt_index = int(prompt_index_str)
                if 0 <= prompt_index < len(session.prompts):
                    old_value = session.prompts[prompt_index].get('value', '')
                    session.prompts[prompt_index]['value'] = new_value
                    logging.info(f"[EXECUTE SESSION] Override prompt {prompt_index}: '{old_value}' -> '{new_value}'")
        
        # Initialize browser
        executor = BrowserExecutor()
        executor.initialize_driver('chrome', headless)
        
        # Navigate to base URL if available
        # FIX: session.url doesn't exist, use current_url or first prompt's URL
        base_url = session.current_url or (session.prompts[0].get('url') if session.prompts else None)
        if base_url:
            logging.info(f"[EXECUTE SESSION] Navigating to: {base_url}")
            executor.driver.get(base_url)
            time.sleep(2)
        else:
            logging.warning(f"[EXECUTE SESSION] No base URL found, using first prompt's URL")
        
        # Get generator for code generation
        generator = get_generator_func()
        
        # Execute each prompt/step
        steps_executed = 0
        for i, prompt_data in enumerate(session.prompts, 1):
            prompt_text = prompt_data.get('prompt', '')
            step_url = prompt_data.get('url')
            value = prompt_data.get('value')
            
            logging.info(f"[STEP {i}/{len(session.prompts)}] Prompt: {prompt_text}")
            
            # Navigate if step has different URL
            if step_url and step_url != executor.driver.current_url:
                logging.info(f"[STEP {i}] Navigating to: {step_url}")
                executor.driver.get(step_url)
                time.sleep(2)
            
            # Generate code for this step
            try:
                # Use infer() method which returns {'code': '...', 'xpath': '...'}
                code_result = generator.infer(
                    prompt_text,
                    language='python',  # Execute as Python
                    comprehensive_mode=True  # Use comprehensive mode for better code
                )
                
                generated_code = code_result.get('code', '')
                if not generated_code:
                    raise Exception("No code generated from inference engine")
                    
                logging.info(f"[STEP {i}] Generated code: {generated_code[:100]}...")
            except Exception as gen_error:
                logging.error(f"[STEP {i}] Code generation error: {gen_error}")
                raise Exception(f"Step {i} code generation failed: {str(gen_error)}")
            
            # Replace {VALUE} placeholder if value provided
            if value and '{VALUE}' in generated_code:
                generated_code = generated_code.replace('{VALUE}', value)
            
            # Execute the generated code
            exec_result = executor.execute_code(generated_code, None)  # Don't pass URL, already navigated
            
            if not exec_result['success']:
                error_msg = exec_result.get('error', 'Unknown execution error')
                logging.error(f"[STEP {i}] Execution failed: {error_msg}")
                
                # Close browser
                try:
                    executor.close()
                except:
                    pass
                
                return jsonify({
                    'success': False,
                    'error': f'Step {i} failed: {error_msg}',
                    'step': i,
                    'prompt': prompt_text,
                    'steps_executed': steps_executed
                }), 500
            
            logging.info(f"[STEP {i}] Completed successfully")
            steps_executed += 1
            time.sleep(1)  # Small delay between steps
        
        # Keep browser open for user to see results
        logging.info(f"[EXECUTE SESSION] All {steps_executed} steps completed successfully")
        logging.info("[EXECUTE SESSION] Browser kept open for inspection")
        
        return jsonify({
            'success': True,
            'message': f'Test executed successfully ({steps_executed} steps)',
            'steps_executed': steps_executed,
            'total_steps': len(session.prompts),
            'keep_browser_open': True
        }), 200
        
    except Exception as e:
        logging.error(f"[EXECUTE SESSION] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        
        # Try to close browser if it was initialized
        try:
            if 'executor' in locals():
                executor.close()
        except:
            pass
        
        return jsonify({
            'error': str(e),
            'success': False
        }), 500

def clear_inference_cache():
    """Clear the inference cache (useful for testing or memory management)."""
    global _inference_cache
    cache_size = len(_inference_cache)
    _inference_cache.clear()
    logging.info(f"[CACHE] Cleared {cache_size} cached inference results")
    return jsonify({
        'success': True,
        'cleared_entries': cache_size
    }), 200