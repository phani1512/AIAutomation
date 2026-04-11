"""
ML-Based Semantic Analyzer

Replaces rule-based semantic analysis with ML predictions.
Uses trained models to predict 30-50 relevant test scenarios per test.

Features:
- Loads trained ML models
- Extracts features from test cases
- Predicts applicable scenarios with confidence scores
- Generates detailed scenario descriptions
- Prioritizes by bug-finding probability
"""

import json
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import Counter
import joblib

logger = logging.getLogger(__name__)


class MLSemanticAnalyzer:
    """ML-powered semantic analysis for test generation."""
    
    def __init__(self, project_root: Path = None):
        """Initialize ML analyzer."""
        if project_root is None:
            # Go up 5 levels: ml_models → python → main → src → project_root
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.models_dir = project_root / "resources" / "ml_data" / "models" / "ml_models"
        
        # ML components
        self.model = None
        self.label_encoder = None
        self.feature_scaler = None
        self.metadata = None
        
        # Scenario templates for generating detailed descriptions
        self.scenario_templates = self._load_scenario_templates()
        
        # Load models
        self._load_ml_models()
    
    def _load_ml_models(self):
        """Load trained ML models and preprocessing objects."""
        try:
            # Load metadata
            metadata_path = self.models_dir / "model_metadata.json"
            if not metadata_path.exists():
                logger.warning("[ML-SEMANTIC] Model metadata not found - ML mode disabled")
                return
            
            with open(metadata_path, 'r') as f:
                self.metadata = json.load(f)
            
            best_model_name = self.metadata['best_model']
            
            # Load model
            model_path = self.models_dir / f"semantic_model_{best_model_name}.pkl"
            self.model = joblib.load(model_path)
            
            # Load preprocessing
            self.label_encoder = joblib.load(self.models_dir / "label_encoder.pkl")
            self.feature_scaler = joblib.load(self.models_dir / "feature_scaler.pkl")
            
            logger.info(f"[ML-SEMANTIC] ✓ Loaded ML model: {best_model_name}")
            logger.info(f"[ML-SEMANTIC] Can predict {len(self.label_encoder.classes_)} scenario types")
        
        except Exception as e:
            logger.warning(f"[ML-SEMANTIC] Could not load ML models: {e}")
            logger.info("[ML-SEMANTIC] Falling back to rule-based analysis")
    
    def _load_scenario_templates(self) -> Dict[str, Dict]:
        """Load scenario description templates."""
        return {
            # Negative Testing
            'negative_empty_form': {
                'type': 'negative',
                'title': 'Empty Form Submission Test',
                'priority': 'high',
                'description': 'Test form submission with all required fields empty to verify validation',
                'steps': [
                    'Leave all required fields empty',
                    'Attempt to submit form',
                    'Verify validation errors appear',
                    'Verify form is not submitted'
                ]
            },
            'negative_invalid_input': {
                'type': 'negative',
                'title': 'Invalid Input Testing',
                'priority': 'high',
                'description': 'Test with invalid, malicious, and malformed inputs including SQL injection and XSS',
                'steps': [
                    'Enter SQL injection patterns: \' OR \'1\'=\'1',
                    'Enter XSS payloads: <script>alert(1)</script>',
                    'Enter invalid formats for email/phone fields',
                    'Verify all inputs are properly validated and sanitized'
                ]
            },
            'negative_invalid_email': {
                'type': 'negative',
                'title': 'Invalid Email Format Testing',
                'priority': 'high',
                'description': 'Test email field with various invalid formats',
                'steps': [
                    'Test with: "notanemail", "user@", "@domain.com", "user @domain.com"',
                    'Test with special characters',
                    'Test with very long email addresses',
                    'Verify proper validation messages'
                ]
            },
            'negative_weak_password': {
                'type': 'negative',
                'title': 'Weak Password Testing',
                'priority': 'medium',
                'description': 'Test password field with weak passwords',
                'steps': [
                    'Try too short passwords (< 8 chars)',
                    'Try passwords without special characters',
                    'Try common passwords (password123)',
                    'Verify password strength requirements enforced'
                ]
            },
            'negative_direct_access': {
                'type': 'negative',
                'title': 'Direct URL Access Test',
                'priority': 'high',
                'description': 'Test accessing protected pages directly without proper navigation',
                'steps': [
                    'Copy target page URL',
                    'Logout or open incognito browser',
                    'Navigate directly to URL',
                    'Verify access is denied or redirected to login'
                ]
            },
            'negative_disabled_button': {
                'type': 'negative',
                'title': 'Disabled Button Test',
                'priority': 'medium',
                'description': 'Test that disabled buttons cannot be activated',
                'steps': [
                    'Identify conditions that disable button',
                    'Trigger those conditions',
                    'Verify button is visually disabled',
                    'Verify button cannot be clicked'
                ]
            },
            
            # Boundary Testing
            'boundary_length': {
                'type': 'boundary',
                'title': 'Field Length Boundary Testing',
                'priority': 'high',
                'description': 'Test input fields at minimum, maximum, and beyond boundaries',
                'steps': [
                    'Test with 0 characters (empty)',
                    'Test with 1 character (minimum)',
                    'Test with maximum allowed length',
                    'Test with maximum + 1 characters',
                    'Verify length restrictions enforced'
                ]
            },
            'boundary_min_max_length': {
                'type': 'boundary',
                'title': 'Comprehensive Length Boundary Test',
                'priority': 'high',
                'description': 'Test all input fields for boundary values',
                'steps': [
                    'For each field, test: empty, 1 char, max, max+1',
                    'Test with exactly at boundary (max-1, max, max+1)',
                    'Verify appropriate handling at each boundary',
                    'Verify error messages for out-of-bound values'
                ]
            },
            'boundary_all_options': {
                'type': 'boundary',
                'title': 'Test All Dropdown Options',
                'priority': 'medium',
                'description': 'Iterate through all dropdown/selection options',
                'steps': [
                    'Get list of all dropdown options',
                    'For each option, select it',
                    'Verify option is selected',
                    'Verify dependent fields update correctly',
                    'Test form submission with each option'
                ]
            },
            'boundary_search_length': {
                'type': 'boundary',
                'title': 'Search Query Length Testing',
                'priority': 'medium',
                'description': 'Test search functionality with various query lengths',
                'steps': [
                    'Search with 1 character',
                    'Search with very long query (500+ chars)',
                    'Search with query at max length',
                    'Verify search handles all lengths appropriately'
                ]
            },
            
            # Edge Cases
            'edge_case_special_chars': {
                'type': 'edge_case',
                'title': 'Special Characters Testing',
                'priority': 'high',
                'description': 'Test with special characters and symbols',
                'steps': [
                    'Enter: !@#$%^&*()[]{}|\\:;"\'<>?,./~`',
                    'Enter emojis: 😀🎉👍',
                    'Enter mathematical symbols: ∑∏∫',
                    'Verify proper handling of special characters'
                ]
            },
            'edge_case_unicode': {
                'type': 'edge_case',
                'title': 'Unicode and International Characters',
                'priority': 'medium',
                'description': 'Test with various Unicode characters',
                'steps': [
                    'Enter Chinese: 你好世界',
                    'Enter Arabic: مرحبا بالعالم',
                    'Enter Russian: Привет мир',
                    'Enter Japanese: こんにちは',
                    'Verify all Unicode properly handled'
                ]
            },
            'edge_case_rapid_submission': {
                'type': 'edge_case',
                'title': 'Rapid/Double Submission Test',
                'priority': 'high',
                'description': 'Test rapid clicking to prevent duplicate submissions',
                'steps': [
                    'Fill form with valid data',
                    'Click submit button multiple times rapidly',
                    'Verify only one submission processed',
                    'Verify button disabled after first click',
                    'Verify no duplicate records created'
                ]
            },
            'edge_case_rapid_click': {
                'type': 'edge_case',
                'title': 'Rapid Button Click Test',
                'priority': 'medium',
                'description': 'Test rapid clicking on action buttons',
                'steps': [
                    'Click target button 10+ times rapidly',
                    'Verify action triggered only once',
                    'Verify no errors occur',
                    'Verify UI remains stable'
                ]
            },
            'edge_case_back_button': {
                'type': 'edge_case',
                'title': 'Browser Back Button Test',
                'priority': 'medium',
                'description': 'Test using browser back button during workflow',
                'steps': [
                    'Complete first step of workflow',
                    'Click browser back button',
                    'Verify data is preserved or cleared appropriately',
                    'Continue workflow',
                    'Verify workflow completes successfully'
                ]
            },
            'edge_case_special_search': {
                'type': 'edge_case',
                'title': 'Special Character Search Test',
                'priority': 'low',
                'description': 'Test search with special characters',
                'steps': [
                    'Search with: "*", "?", "%", "_"',
                    'Search with boolean operators: AND, OR, NOT',
                    'Search with escape characters',
                    'Verify search handles special chars correctly'
                ]
            },
            
            # Variations
            'variation_different_data': {
                'type': 'variation',
                'title': 'Different Valid Data Test',
                'priority': 'medium',
                'description': 'Test with various sets of valid data',
                'steps': [
                    'Create 5 different valid data sets',
                    'Execute test with each data set',
                    'Verify all succeed',
                    'Verify no data-specific issues'
                ]
            },
            'variation_form_data': {
                'type': 'variation',
                'title': 'Form Data Variations',
                'priority': 'medium',
                'description': 'Test form with different combinations of valid data',
                'steps': [
                    'Test with different name formats',
                    'Test with different email domains',
                    'Test with different phone formats',
                    'Verify all variations accepted'
                ]
            },
            'variation_search_terms': {
                'type': 'variation',
                'title': 'Search Term Variations',
                'priority': 'low',
                'description': 'Test search with various query types',
                'steps': [
                    'Search with single word',
                    'Search with multiple words',
                    'Search with exact phrase',
                    'Search with partial matches',
                    'Verify relevant results returned'
                ]
            },
            'variation_selections': {
                'type': 'variation',
                'title': 'Selection Combinations',
                'priority': 'low',
                'description': 'Test different dropdown/checkbox combinations',
                'steps': [
                    'Test with different selection combinations',
                    'Verify each combination works',
                    'Test dependent field updates'
                ]
            },
            
            # Compatibility
            'compatibility_cross_browser': {
                'type': 'compatibility',
                'title': 'Cross-Browser Compatibility',
                'priority': 'medium',
                'description': 'Test across different browsers',
                'steps': [
                    'Execute on Chrome',
                    'Execute on Firefox',
                    'Execute on Edge',
                    'Execute on Safari (if available)',
                    'Verify consistent behavior across all'
                ]
            },
            'compatibility_mobile': {
                'type': 'compatibility',
                'title': 'Mobile Responsiveness',
                'priority': 'medium',
                'description': 'Test on mobile viewports and devices',
                'steps': [
                    'Test on mobile viewport (375x667)',
                    'Test on tablet viewport (768x1024)',
                    'Test portrait and landscape',
                    'Verify all elements accessible',
                    'Verify touch interactions work'
                ]
            },
            
            # Performance
            'performance_load_time': {
                'type': 'performance',
                'title': 'Page Load Performance',
                'priority': 'low',
                'description': 'Measure and verify page load times',
                'steps': [
                    'Navigate to page cold (cleared cache)',
                    'Measure load time',
                    'Navigate again warm (with cache)',
                    'Measure load time',
                    'Verify both within acceptable limits'
                ]
            },
            'performance_response_time': {
                'type': 'performance',
                'title': 'Action Response Time',
                'priority': 'low',
                'description': 'Measure response times for actions',
                'steps': [
                    'Perform each action',
                    'Measure time to complete',
                    'Verify all complete within 3 seconds',
                    'Identify any slow operations'
                ]
            },
            
            # Workflow
            'workflow_state_management': {
                'type': 'workflow',
                'title': 'State Management Test',
                'priority': 'high',
                'description': 'Test application state is properly maintained',
                'steps': [
                    'Complete workflow partway',
                    'Refresh page',
                    'Verify state preserved or cleared appropriately',
                    'Continue or restart workflow',
                    'Verify successful completion'
                ]
            },
            'edge_case_back_navigation': {
                'type': 'workflow',
                'title': 'Back Navigation in Workflow',
                'priority': 'medium',
                'description': 'Test navigating backwards in multi-step workflow',
                'steps': [
                    'Complete step 1',
                    'Complete step 2',
                    'Navigate back to step 1',
                    'Change data',
                    'Navigate forward',
                    'Verify updated data propagates correctly'
                ]
            },
            
            # Generic fallbacks for any unmapped scenarios
            'default': {
                'type': 'general',
                'title': 'Test Scenario',
                'priority': 'medium',
                'description': 'Additional test scenario suggested by ML model',
                'steps': ['Execute test with varied conditions', 'Verify expected behavior']
            }
        }
    
    def suggest_scenarios(self, recorded_actions: List[Dict], current_page: str = '', context: Dict = None) -> List[Dict[str, Any]]:
        """
        Generate COMPREHENSIVE test scenarios using ML model.
        
        Returns 20-40 test scenarios covering ALL variation types:
        - Multiple negative test scenarios
        - Multiple boundary test scenarios
        - Multiple edge case scenarios
        - Multiple compatibility scenarios
        - Multiple performance scenarios
        
        Args:
            recorded_actions: List of recorded actions
            current_page: Current page URL
            context: Additional context (test_name, code, etc.)
        
        Returns:
            List of comprehensive test scenarios (20-40 scenarios)
        """
        if self.model is None:
            logger.warning("[ML-SEMANTIC] ML model not loaded, using comprehensive fallback")
            return self._comprehensive_fallback_scenarios(recorded_actions, context)
        
        # Extract features
        features = self._extract_features(recorded_actions, context)
        
        # Get ML predictions for ALL scenario types
        scenario_predictions = self._predict_scenarios(features)
        
        # Generate COMPREHENSIVE detailed scenarios (multiple per type)
        scenarios = self._generate_comprehensive_scenarios(scenario_predictions, features, context)
        
        logger.info(f"[ML-SEMANTIC] Generated {len(scenarios)} comprehensive scenarios using ML")
        
        return scenarios
    
    def _extract_features(self, actions: List[Dict], context: Dict = None) -> Dict[str, Any]:
        """Extract features for ML prediction."""
        # Extract enhanced context if provided
        test_name = ''
        test_description = ''
        generated_code = ''
        test_url = ''
        
        if context and isinstance(context, dict):
            test_name = context.get('test_name', '')
            test_description = context.get('description', '')
            generated_code = context.get('generated_code', '')
            test_url = context.get('url', '')
            
            if 'actions' in context and context['actions']:
                actions = context['actions']
        
        # Analyze actions
        action_types = []
        element_types = []
        
        for idx, action in enumerate(actions):
            try:
                # SAFETY: Handle multiple formats (recorder vs builder vs prompt)
                # Recorder format: {'action_type': 'click', ...}
                # Builder format: {'action': 'click button', ...}
                # Prompt format: {'prompt': 'click the login button', ...}
                action_text = (
                    action.get('action') or 
                    action.get('prompt') or 
                    action.get('action_type') or 
                    ''
                )
                
                if not action_text:
                    action_text = ''
                elif not isinstance(action_text, str):
                    action_text = str(action_text)
                
                action_types.append(self._infer_action_type(action_text))
                element_types.append(action.get('element_type', self._infer_element_type(action_text)))
            except Exception as e:
                logger.error(f"[ML-SEMANTIC] Error processing action {idx}: {e}")
                logger.error(f"[ML-SEMANTIC] Action data: {action}")
                action_types.append('other')
                element_types.append('unknown')
        
        # Detect patterns - use safe string conversion
        try:
            has_navigation = any('navigate' in str(a.get('action', a.get('action_type', ''))).lower() or 
                               'go to' in str(a.get('action', a.get('action_type', ''))).lower() 
                               for a in actions if isinstance(a, dict))
            has_form = any('enter' in str(a.get('action', a.get('action_type', ''))).lower() or 
                          'fill' in str(a.get('action', a.get('action_type', ''))).lower() 
                          for a in actions if isinstance(a, dict))
            has_submission = any('submit' in str(a.get('action', a.get('action_type', ''))).lower() or 
                                'sign in' in str(a.get('action', a.get('action_type', ''))).lower() 
                                for a in actions if isinstance(a, dict))
        except Exception as e:
            logger.error(f"[ML-SEMANTIC] Error detecting patterns: {e}")
            has_navigation = False
            has_form = False
            has_submission = False
        
        workflow = self._classify_workflow(action_types, has_form, has_submission)
        
        features = {
            'action_sequence': action_types,
            'element_sequence': element_types,
            'action_count': len(actions),
            'unique_actions': len(set(action_types)),
            'unique_elements': len(set(element_types)),
            'has_navigation': has_navigation,
            'has_form': has_form,
            'has_submission': has_submission,
            'workflow_type': workflow,
            'input_field_count': sum(1 for a in action_types if a == 'input'),
            'button_count': sum(1 for e in element_types if e == 'button'),
            'test_name': test_name,
            'priority': 'medium'
        }
        
        return features
    
    def _infer_action_type(self, text: str) -> str:
        """Infer action type from text."""
        # SAFETY: Handle None or empty text
        if not text:
            return 'other'
        
        text = str(text).lower()
        if any(word in text for word in ['click', 'press']):
            return 'click'
        elif any(word in text for word in ['enter', 'type', 'fill', 'input']):
            return 'input'
        elif any(word in text for word in ['select', 'choose', 'dropdown']):
            return 'select'
        elif any(word in text for word in ['navigate', 'go to', 'open', 'visit']):
            return 'navigate'
        elif any(word in text for word in ['check', 'uncheck', 'toggle']):
            return 'checkbox'
        else:
            return 'other'
    
    def _infer_element_type(self, text: str) -> str:
        """Infer element type from text."""
        # SAFETY: Handle None or empty text
        if not text:
            return 'unknown'
            
        text = str(text).lower()
        if 'button' in text:
            return 'button'
        elif any(word in text for word in ['input', 'field', 'textbox']):
            return 'input'
        elif any(word in text for word in ['dropdown', 'select']):
            return 'dropdown'
        elif 'link' in text:
            return 'link'
        else:
            return 'unknown'
    
    def _classify_workflow(self, actions: List[str], has_form: bool, has_submission: bool) -> str:
        """Classify workflow type."""
        if has_form and has_submission:
            return 'form_submission'
        elif 'navigate' in actions and len(actions) > 1:
            return 'multi_page_workflow'
        elif 'input' in actions and 'click' in actions:
            return 'search_workflow'
        elif has_form:
            return 'form_filling'
        else:
            return 'general_interaction'
    
    def _predict_scenarios(self, features: Dict) -> List[Tuple[str, float]]:
        """Use ML model to predict applicable scenarios."""
        from .semantic_model_trainer import SemanticModelTrainer
        
        trainer = SemanticModelTrainer(self.project_root)
        trainer.model = self.model
        trainer.best_model = self.model
        trainer.mlb = self.label_encoder
        trainer.scaler = self.feature_scaler
        
        scenario_scores = trainer.predict_scenarios(features)
        return scenario_scores
    
    def _generate_comprehensive_scenarios(self, predictions: List[Tuple[str, float]], 
                                          features: Dict, context: Dict = None) -> List[Dict[str, Any]]:
        """
        Generate COMPREHENSIVE scenarios from ML predictions.
        Returns multiple scenarios per type for complete test coverage.
        """
        scenarios = []
        seen_scenarios = set()
        
        # Organize predictions by type
        scenarios_by_type = {}
        for scenario_key, confidence in predictions:
            template = self.scenario_templates.get(scenario_key, self.scenario_templates['default'])
            scenario_type = template['type']
            
            if scenario_type not in scenarios_by_type:
                scenarios_by_type[scenario_type] = []
            scenarios_by_type[scenario_type].append((scenario_key, confidence, template))
        
        # Generate multiple scenarios per type (aim for 3-5 per type)
        for scenario_type, type_scenarios in scenarios_by_type.items():
            # Sort by confidence for this type
            type_scenarios.sort(key=lambda x: x[1], reverse=True)
            
            # Take top scenarios for this type (at least 3, up to 5)
            count = 0
            for scenario_key, confidence, template in type_scenarios:
                if count >= 5:  # Max 5 per type
                    break
                    
                if scenario_key not in seen_scenarios:
                    scenario = {
                        'type': template['type'],
                        'title': template['title'],
                        'scenario': template['title'],
                        'description': template['description'],
                        'priority': template['priority'],
                        'steps': template['steps'],
                        'confidence': round(confidence, 3),
                        'ml_predicted': True,
                        'scenario_key': scenario_key
                    }
                    scenarios.append(scenario)
                    seen_scenarios.add(scenario_key)
                    count += 1
        
        # If we don't have enough variety, add generic scenarios for missing types
        expected_types = ['negative', 'boundary', 'edge_case', 'performance', 'compatibility', 
                         'security', 'data_validation']
        
        for exp_type in expected_types:
            if exp_type not in scenarios_by_type or len(scenarios_by_type[exp_type]) < 2:
                # Add generic scenarios for this type
                generic_scenarios = self._get_generic_scenarios_for_type(exp_type)
                for scenario_key in generic_scenarios:
                    if scenario_key not in seen_scenarios and len([s for s in scenarios if s['type'] == exp_type]) < 5:
                        template = self.scenario_templates.get(scenario_key, self.scenario_templates['default'])
                        scenario = {
                            'type': template['type'],
                            'title': template['title'],
                            'scenario': template['title'],
                            'description': template['description'],
                            'priority': template['priority'],
                            'steps': template['steps'],
                            'confidence': 0.7,  # Generic scenarios have decent confidence
                            'ml_predicted': False,
                            'scenario_key': scenario_key
                        }
                        scenarios.append(scenario)
                        seen_scenarios.add(scenario_key)
        
        # Sort by priority and confidence
        priority_order = {'critical': 4, 'high': 3, 'medium': 2, 'low': 1}
        scenarios.sort(key=lambda x: (priority_order.get(x['priority'], 2), x['confidence']), reverse=True)
        
        logger.info(f"[ML-SEMANTIC] Generated {len(scenarios)} comprehensive scenarios across {len(scenarios_by_type)} types")
        
        return scenarios
    
    def _get_generic_scenarios_for_type(self, scenario_type: str) -> List[str]:
        """Get generic scenario keys for a specific type."""
        type_mapping = {
            'negative': ['negative_invalid_input', 'negative_empty_form', 'negative_partial_form', 
                        'negative_invalid_email', 'negative_weak_password'],
            'boundary': ['boundary_length', 'boundary_min_max_length', 'boundary_all_options',
 'boundary_field_length'],
            'edge_case': ['edge_case_special_chars', 'edge_case_unicode', 'edge_case_rapid_submission'],
            'performance': ['performance_load_time'],
            'compatibility': ['compatibility_cross_browser', 'compatibility_mobile'],
            'security': ['negative_direct_url'],
            'data_validation': ['variation_form_data', 'variation_different_data']
        }
        return type_mapping.get(scenario_type, [])
    
    def _generate_detailed_scenarios(self, predictions: List[Tuple[str, float]], 
                                    features: Dict, context: Dict = None) -> List[Dict[str, Any]]:
        """Generate detailed scenarios from ML predictions (legacy method)."""
        # Use comprehensive generation instead
        return self._generate_comprehensive_scenarios(predictions, features, context)
    
    def _comprehensive_fallback_scenarios(self, actions: List[Dict], context: Dict = None) -> List[Dict[str, Any]]:
        """
        Comprehensive fallback to return ALL universal scenarios if ML model unavailable.
        Returns 20-30+ scenarios covering all test types.
        """
        logger.info("[ML-SEMANTIC] Using comprehensive fallback rule-based scenarios")
        
        # Return a COMPREHENSIVE set of universal scenarios (multiple per type)
        comprehensive_scenarios = [
            # Negative Testing (5+ scenarios)
            'negative_invalid_input',
            'negative_empty_form',
            'negative_partial_form',
            'negative_invalid_email',
            'negative_weak_password',
            'negative_direct_url',
            
            # Boundary Testing (4+ scenarios)
            'boundary_min_max_length',
            'boundary_length',
            'boundary_all_options',
            'boundary_field_length',
            
            # Edge Case Testing (3+ scenarios)
            'edge_case_special_chars',
            'edge_case_unicode',
            'edge_case_rapid_submission',
            
            # Compatibility Testing (2+ scenarios)
            'compatibility_cross_browser',
            'compatibility_mobile',
            
            # Performance Testing (1+ scenarios)
            'performance_load_time',
            
            # Data Variation Testing (2+ scenarios)
            'variation_form_data',
            'variation_different_data',
            'variation_different_selection',
        ]
        
        scenarios = []
        for key in comprehensive_scenarios:
            template = self.scenario_templates.get(key)
            if template:
                scenarios.append({
                    'type': template['type'],
                    'title': template['title'],
                    'scenario': template['title'],
                    'description': template['description'],
                    'priority': template['priority'],
                    'steps': template['steps'],
                    'confidence': 0.8,  # Fallback scenarios have good confidence
                    'ml_predicted': False,
                    'scenario_key': key
                })
        
        logger.info(f"[ML-SEMANTIC] Generated {len(scenarios)} comprehensive fallback scenarios")
        return scenarios
    
    def _fallback_scenarios(self, actions: List[Dict], context: Dict = None) -> List[Dict[str, Any]]:
        """Fallback to basic scenarios if ML model unavailable (legacy method)."""
        # Use comprehensive fallback instead
        return self._comprehensive_fallback_scenarios(actions, context)


if __name__ == "__main__":
    # Test the analyzer
    logging.basicConfig(level=logging.INFO)
    
    analyzer = MLSemanticAnalyzer()
    
    # Test with sample actions
    test_actions = [
        {'action': 'navigate to login page'},
        {'action': 'enter username'},
        {'action': 'enter password'},
        {'action': 'click login button'}
    ]
    
    scenarios = analyzer.suggest_scenarios(test_actions, context={'test_name': 'Login Test'})
    
    print(f"\n✓ Generated {len(scenarios)} scenarios:")
    for i, s in enumerate(scenarios[:10], 1):
        print(f"{i}. [{s['type']}] {s['title']} (confidence: {s.get('confidence', 'N/A')})")
