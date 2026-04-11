"""
Feedback Collection System for ML Model Improvement

Collects user feedback on suggested scenarios:
- Which scenarios were useful
- Which were not relevant
- New scenarios users created
- Test execution results

Uses feedback to continuously improve ML model accuracy.
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class FeedbackCollector:
    """Collect and store user feedback for model improvement."""
    
    def __init__(self, project_root: Path = None):
        """Initialize feedback collector."""
        if project_root is None:
            # Go up 5 levels: ml_models → python → main → src → project_root
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.feedback_path = project_root / "resources" / "ml_data" / "datasets" / "ml_feedback.json"
        self.feedback_path.parent.mkdir(parents=True, exist_ok=True)
        
        self.feedback_data = self._load_feedback()
    
    def _load_feedback(self) -> Dict[str, List]:
        """Load existing feedback."""
        if self.feedback_path.exists():
            try:
                with open(self.feedback_path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            except Exception as e:
                logger.error(f"[FEEDBACK]Error loading feedback: {e}")
        
        return {
            'scenario_ratings': [],
            'test_results': [],
            'user_suggestions': [],
            'field_suggestion_usage': [],  # NEW: Track which field suggestions were used
            'metadata': {
                'total_feedback': 0,
                'last_updated': None
            }
        }
    
    def _save_feedback(self):
        """Save feedback to disk."""
        self.feedback_data['metadata']['last_updated'] = datetime.now().isoformat()
        self.feedback_data['metadata']['total_feedback'] = (
            len(self.feedback_data['scenario_ratings']) +
            len(self.feedback_data['test_results']) +
            len(self.feedback_data['user_suggestions']) +
            len(self.feedback_data.get('field_suggestion_usage', []))
        )
        
        with open(self.feedback_path, 'w', encoding='utf-8') as f:
            json.dump(self.feedback_data, f, indent=2)
        
        logger.info(f"[FEEDBACK] Saved feedback: {self.feedback_data['metadata']['total_feedback']} entries")
    
    def record_scenario_rating(self, test_case_id: str, scenario_key: str, 
                              rating: str, features: Dict = None):
        """
        Record user rating for a suggested scenario.
        
        Args:
            test_case_id: ID of test case
            scenario_key: Scenario identifier
            rating: 'useful', 'not_relevant', 'already_exists'
            features: Test features (for retraining)
        """
        feedback_entry = {
            'id': f"{test_case_id}_{scenario_key}_{datetime.now().timestamp()}",
            'test_case_id': test_case_id,
            'scenario_key': scenario_key,
            'rating': rating,
            'features': features or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_data['scenario_ratings'].append(feedback_entry)
        self._save_feedback()
        
        logger.info(f"[FEEDBACK] Recorded rating: {scenario_key} = {rating}")
    
    def record_test_result(self, test_case_id: str, scenarios_used: List[str],
                          found_bugs: bool, bug_types: List[str] = None):
        """
        Record test execution results.
        
        Args:
            test_case_id: ID of test case
            scenarios_used: Which scenarios were executed
            found_bugs: Whether bugs were found
            bug_types: Types of bugs found
        """
        result_entry = {
            'id': f"result_{test_case_id}_{datetime.now().timestamp()}",
            'test_case_id': test_case_id,
            'scenarios_used': scenarios_used,
            'found_bugs': found_bugs,
            'bug_types': bug_types or [],
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_data['test_results'].append(result_entry)
        self._save_feedback()
        
        logger.info(f"[FEEDBACK] Recorded test result: bugs={found_bugs}, scenarios={len(scenarios_used)}")
    
    def record_user_suggestion(self, test_case_id: str, scenario_title: str,
                              scenario_description: str, features: Dict = None):
        """
        Record user-created scenario that wasn't suggested.
        
        Args:
            test_case_id: ID of test case
            scenario_title: Title of scenario
            scenario_description: Description
            features: Test features
        """
        suggestion_entry = {
            'id': f"suggestion_{test_case_id}_{datetime.now().timestamp()}",
            'test_case_id': test_case_id,
            'scenario_title': scenario_title,
            'scenario_description': scenario_description,
            'features': features or {},
            'timestamp': datetime.now().isoformat()
        }
        
        self.feedback_data['user_suggestions'].append(suggestion_entry)
        self._save_feedback()
        
        logger.info(f"[FEEDBACK] Recorded user suggestion: {scenario_title}")
    
    def record_field_suggestion_usage(self, test_case_id: str, field_index: int,
                                     field_type: str, suggestion_category: str,
                                     suggestion_value: str, suggestion_description: str):
        """
        Record when user applies a field-aware suggestion.
        
        Args:
            test_case_id: ID of test case
            field_index: Index of field (0-based)
            field_type: Detected field type (email, password, etc.)
            suggestion_category: Category of suggestion (boundary, security, etc.)
            suggestion_value: The actual value that was suggested
            suggestion_description: Description of the suggestion
        """
        usage_entry = {
            'id': f"field_{test_case_id}_{field_index}_{datetime.now().timestamp()}",
            'test_case_id': test_case_id,
            'field_index': field_index,
            'field_type': field_type,
            'suggestion_category': suggestion_category,
            'suggestion_value': suggestion_value,
            'suggestion_description': suggestion_description,
            'timestamp': datetime.now().isoformat()
        }
        
        # Initialize field_suggestion_usage if it doesn't exist (backward compatibility)
        if 'field_suggestion_usage' not in self.feedback_data:
            self.feedback_data['field_suggestion_usage'] = []
        
        self.feedback_data['field_suggestion_usage'].append(usage_entry)
        self._save_feedback()
        
        logger.info(f"[FEEDBACK] Recorded field suggestion usage: {field_type} → {suggestion_category} = {suggestion_description}")
    
    def get_feedback_summary(self) -> Dict[str, Any]:
        """Get summary of collected feedback."""
        ratings = self.feedback_data['scenario_ratings']
        
        rating_counts = {
            'useful': 0,
            'not_relevant': 0,
            'already_exists': 0
        }
        
        for entry in ratings:
            rating = entry.get('rating', 'unknown')
            if rating in rating_counts:
                rating_counts[rating] += 1
        
        # Field suggestion usage stats
        field_usage = self.feedback_data.get('field_suggestion_usage', [])
        field_category_counts = {}
        for usage in field_usage:
            category = usage.get('suggestion_category', 'unknown')
            field_category_counts[category] = field_category_counts.get(category, 0) + 1
        
        summary = {
            'total_ratings': len(ratings),
            'rating_distribution': rating_counts,
            'useful_percentage': (rating_counts['useful'] / len(ratings) * 100) if len(ratings) > 0 else 0,
            'total_test_results': len(self.feedback_data['test_results']),
            'total_user_suggestions': len(self.feedback_data['user_suggestions']),
            'total_field_suggestions_used': len(field_usage),
            'field_suggestion_categories': field_category_counts,
            'last_updated': self.feedback_data['metadata']['last_updated']
        }
        
        return summary
    
    def export_training_samples(self) -> List[Dict[str, Any]]:
        """
        Export feedback as training samples for model retraining.
        
        Returns samples in format compatible with training data extractor.
        """
        training_samples = []
        
        # Convert rated scenarios to training samples
        for entry in self.feedback_data['scenario_ratings']:
            if entry.get('rating') == 'useful' and entry.get('features'):
                sample = {
                    'id': entry['id'],
                    'source': 'feedback',
                    'features': entry['features'],
                    'labels': {
                        'applicable_scenarios': [entry['scenario_key']],
                        'confidence': 1.0  # User-validated
                    }
                }
                training_samples.append(sample)
        
        logger.info(f"[FEEDBACK] Exported {len(training_samples)} training samples from feedback")
        
        return training_samples


# Add feedback endpoints to API
def create_feedback_routes(app, feedback_collector):
    """Add feedback collection routes to Flask app."""
    
    @app.route('/semantic/feedback/rate-scenario', methods=['POST'])
    def rate_scenario():
        """Rate a suggested scenario."""
        from flask import request, jsonify
        
        try:
            data = request.json
            test_case_id = data.get('test_case_id')
            scenario_key = data.get('scenario_key')
            rating = data.get('rating')  # 'useful', 'not_relevant', 'already_exists'
            features = data.get('features', {})
            
            if not all([test_case_id, scenario_key, rating]):
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields'
                }), 400
            
            feedback_collector.record_scenario_rating(test_case_id, scenario_key, rating, features)
            
            return jsonify({
                'success': True,
                'message': 'Feedback recorded'
            })
        
        except Exception as e:
            logger.error(f"[FEEDBACK] Error recording rating: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/semantic/feedback/test-result', methods=['POST'])
    def record_test_result():
        """Record test execution result."""
        from flask import request, jsonify
        
        try:
            data = request.json
            test_case_id = data.get('test_case_id')
            scenarios_used = data.get('scenarios_used', [])
            found_bugs = data.get('found_bugs', False)
            bug_types = data.get('bug_types', [])
            
            feedback_collector.record_test_result(test_case_id, scenarios_used, found_bugs, bug_types)
            
            return jsonify({
                'success': True,
                'message': 'Test result recorded'
            })
        
        except Exception as e:
            logger.error(f"[FEEDBACK] Error recording test result: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/semantic/feedback/suggest-scenario', methods=['POST'])
    def suggest_scenario():
        """Record user-created scenario."""
        from flask import request, jsonify
        
        try:
            data = request.json
            test_case_id = data.get('test_case_id')
            scenario_title = data.get('title')
            scenario_description = data.get('description')
            features = data.get('features', {})
            
            feedback_collector.record_user_suggestion(
                test_case_id, scenario_title, scenario_description, features
            )
            
            return jsonify({
                'success': True,
                'message': 'Suggestion recorded'
            })
        
        except Exception as e:
            logger.error(f"[FEEDBACK] Error recording suggestion: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/ml/feedback/field-suggestion-used', methods=['POST'])
    def record_field_suggestion_used():
        """Record when user applies a field-aware suggestion."""
        from flask import request, jsonify
        
        try:
            data = request.json
            test_case_id = data.get('test_case_id')
            field_index = data.get('field_index')
            field_type = data.get('field_type')
            suggestion_category = data.get('category')
            suggestion_value = data.get('value')
            suggestion_description = data.get('description')
            
            if not all([test_case_id is not None, field_index is not None, field_type, suggestion_category]):
                return jsonify({
                    'success': False,
                    'error': 'Missing required fields'
                }), 400
            
            feedback_collector.record_field_suggestion_usage(
                test_case_id, field_index, field_type, suggestion_category,
                suggestion_value, suggestion_description
            )
            
            return jsonify({
                'success': True,
                'message': 'Field suggestion usage recorded'
            })
        
        except Exception as e:
            logger.error(f"[FEEDBACK] Error recording field suggestion: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
    
    @app.route('/semantic/feedback/summary', methods=['GET'])
    def get_feedback_summary():
        """Get feedback summary and statistics."""
        from flask import jsonify
        
        try:
            summary = feedback_collector.get_feedback_summary()
            return jsonify({
                'success': True,
                'summary': summary
            })
        
        except Exception as e:
            logger.error(f"[FEEDBACK] Error getting summary: {e}")
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
