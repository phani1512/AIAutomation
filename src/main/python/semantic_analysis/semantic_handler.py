"""
Semantic analysis endpoint handlers.
Extracted from api_server_modular.py for better modularity.
"""
import logging
from flask import request, jsonify


def analyze_intent(get_analyzer_func):
    """Analyze user prompt to understand test intent.
    
    Args:
        get_analyzer_func: Function that returns semantic analyzer instance
    
    Returns:
        JSON response with analysis results
    """
    try:
        data = request.json
        prompt = data.get('prompt', '')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        analyzer = get_analyzer_func()
        analysis = analyzer.analyze_intent(prompt)
        
        return jsonify({
            'success': True,
            'analysis': analysis
        }), 200
    except Exception as e:
        logging.error(f"[SEMANTIC-INTENT] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def suggest_scenarios(get_analyzer_func, get_test_case_builder_func):
    """Suggest test scenarios based on saved test case.
    
    Args:
        get_analyzer_func: Function that returns semantic analyzer instance
        get_test_case_builder_func: Function that returns test case builder instance
    
    Returns:
        JSON response with scenario suggestions and report
    """
    try:
        data = request.json
        test_case_id = data.get('test_case_id', '')
        
        if not test_case_id:
            return jsonify({'success': False, 'error': 'Test case ID is required'}), 400
        
        # Get test case from test suite
        test_case_builder = get_test_case_builder_func()
        test_case = test_case_builder.get_test_case(test_case_id)
        
        if not test_case:
            return jsonify({'success': False, 'error': 'Test case not found'}), 404
        
        # Extract actions from test case (could be from recorder or builder)
        actions = []
        if 'actions' in test_case:
            # Recorder format
            actions = test_case['actions']
        elif 'prompts' in test_case:
            # Builder format - convert prompts to action-like structure
            actions = [{'action': p.get('prompt', ''), 'type': p.get('type', 'action')} 
                       for p in test_case.get('prompts', [])]
        elif 'steps' in test_case:
            # Generic steps format
            actions = [{'action': step, 'type': 'step'} for step in test_case.get('steps', [])]
        
        analyzer = get_analyzer_func()
        suggestions = analyzer.suggest_scenarios(actions, test_case.get('name', ''))
        
        # Generate report
        intent_analysis = analyzer.analyze_intent(test_case.get('name', ''))
        report = analyzer.generate_test_report(intent_analysis, suggestions)
        
        return jsonify({
            'success': True,
            'suggestions': suggestions,
            'report': report,
            'intent': intent_analysis
        }), 200
    except Exception as e:
        logging.error(f"[SEMANTIC-SCENARIOS] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def get_cache_stats(get_analyzer_func):
    """Get semantic analyzer cache statistics.
    
    Args:
        get_analyzer_func: Function that returns semantic analyzer instance
    
    Returns:
        JSON response with cache statistics
    """
    try:
        analyzer = get_analyzer_func()
        cache_info = analyzer.get_cache_info()
        return jsonify({
            'success': True,
            'cache': cache_info
        })
    except Exception as e:
        logging.error(f"[SEMANTIC-CACHE-STATS] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500


def clear_cache(get_analyzer_func):
    """Clear semantic analyzer cache.
    
    Args:
        get_analyzer_func: Function that returns semantic analyzer instance
    
    Returns:
        JSON response confirming cache cleared
    """
    try:
        analyzer = get_analyzer_func()
        analyzer.clear_cache()
        return jsonify({
            'success': True,
            'message': 'Cache cleared successfully'
        })
    except Exception as e:
        logging.error(f"[SEMANTIC-CLEAR-CACHE] Error: {e}")
        return jsonify({'success': False, 'error': str(e)}), 500
