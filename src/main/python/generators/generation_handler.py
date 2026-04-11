import sys
import logging
import os
import io
from contextlib import contextmanager
from flask import request, jsonify


@contextmanager
def suppress_print_output():
    """Suppress stdout/stderr to prevent Windows encoding errors in Flask API.
    
    On Windows, Flask has issues with certain print statements that contain
    special characters or use flush=True, causing [Errno 22] Invalid argument.
    This context manager redirects output to a null stream during API calls.
    """
    # Save original stdout/stderr
    original_stdout = sys.stdout
    original_stderr = sys.stderr
    
    try:
        # Redirect to null streams with UTF-8 encoding
        sys.stdout = io.StringIO()
        sys.stderr = io.StringIO()
        yield
    finally:
        # Restore original streams
        sys.stdout = original_stdout
        sys.stderr = original_stderr


def generate_code(get_generator_func, get_browser_executor_func, set_browser_executor_func, BrowserExecutor):
    try:
        import sys
        print(f"[DEBUG-GH] generate_code called", file=sys.stderr, flush=True)
        
        data = request.get_json()
        prompt = data.get('prompt', '')
        
        print(f"[DEBUG-GH] Prompt: {prompt}", file=sys.stderr, flush=True)
        language = data.get('language', 'java')
        max_tokens = data.get('max_tokens', 30)
        temperature = data.get('temperature', 0.3)
        execute = data.get('execute', False)
        url = data.get('url', '')
        with_fallbacks = data.get('with_fallbacks', True)
        max_fallbacks = data.get('max_fallbacks', 3)
        
        # Check if this is a verification/assertion prompt (should use simple dataset code)
        prompt_lower = prompt.lower()
        is_verification = any(verb in prompt_lower for verb in ['verify', 'assert', 'check', 'validate', 'confirm']) and \
                         any(target in prompt_lower for target in ['title', 'text', 'url', 'element', 'value', 'displayed', 'enabled'])
        
        # Use simple dataset mode for verifications, comprehensive mode for actions
        comprehensive_mode = data.get('comprehensive_mode', not is_verification)
        
        # For verification prompts, disable fallbacks to get clean dataset code  
        if is_verification and 'with_fallbacks' not in data:
            with_fallbacks = False
            # Log that we detected verification - this will appear in server logs
            import sys
            print(f"[DEBUG] Detected verification prompt: '{prompt}' - using simple mode", file=sys.stderr, flush=True)
        
        if not prompt:
            return jsonify({'error': 'Prompt is required'}), 400
        
        gen = get_generator_func()
        
        if with_fallbacks:
            from .fallback_code_generator import FallbackCodeGenerator
            from semantic_analysis.intelligent_prompt_matcher import get_matcher
            
            matcher = get_matcher()
            match_result = matcher.match_with_fallbacks(prompt, max_fallbacks=max_fallbacks)
            
            primary_match = match_result['primary']
            fallbacks = match_result['fallbacks']
            
            if match_result['has_fallbacks'] and primary_match.get('code'):
                fallback_gen = FallbackCodeGenerator()
                with suppress_print_output():
                    generated = fallback_gen.generate_with_fallbacks(
                        primary_match,
                        fallbacks,
                        language=language,
                        max_fallbacks=max_fallbacks
                    )
            else:
                with suppress_print_output():
                    generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature, language=language, comprehensive_mode=comprehensive_mode)
            
            alternatives = []
            for fb in fallbacks:
                fb_code = fb.get('code', '')
                if fb_code and language != 'java':
                    with suppress_print_output():
                        fb_code = gen._convert_code_to_language(fb_code, language)
                
                alternatives.append({
                    'prompt': fb.get('matched_prompt', ''),
                    'score': fb.get('confidence', 0.0),
                    'code': fb_code,
                    'strategy': fb.get('strategy', 'unknown')
                })
        else:
            with suppress_print_output():
                generated = gen.generate_clean(prompt, max_tokens=max_tokens, temperature=temperature, language=language, comprehensive_mode=comprehensive_mode)
            
            raw_alternatives = gen.get_last_alternatives()
            
            alternatives = []
            for alt in raw_alternatives:
                alt_code = alt.get('code', '')
                if alt_code and language != 'java':
                    with suppress_print_output():
                        alt_code = gen._convert_code_to_language(alt_code, language)
                
                alternatives.append({
                    'prompt': alt.get('prompt', ''),
                    'score': alt.get('score', 0.0),
                    'code': alt_code,
                    'strategy': alt.get('strategy', 'unknown')
                })
        
        response = {
            'prompt': prompt,
            'generated': generated,
            'code': generated,
            'alternatives': alternatives,
            'has_fallbacks': with_fallbacks and len(alternatives) > 0,
            'fallback_count': len(alternatives) if with_fallbacks else 0,
            'tokens_generated': len(generated.split())
        }
        
        if execute:
            browser_executor = get_browser_executor_func()
            if not browser_executor:
                browser_executor = BrowserExecutor()
                browser_executor.initialize_driver()
                set_browser_executor_func(browser_executor)
            
            execution_result = browser_executor.execute_code(generated, url if url else None)
            response['execution'] = execution_result
        
        return jsonify(response), 200
        
    except Exception as e:
        logging.error(f"Error generating code: {str(e)}")
        return jsonify({'error': str(e)}), 500
