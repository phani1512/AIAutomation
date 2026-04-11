"""
Training Data Extractor for Semantic Analysis ML Model

Extracts features from:
1. Combined training dataset (638 patterns)
2. Saved test cases (Builder + Recorder)
3. Execution history
4. User feedback (if available)

Generates training dataset in format:
{
    'features': {
        'action_sequence': [...],
        'action_types': [...],
        'element_types': [...],
        'workflow_type': str,
        'has_navigation': bool,
        'has_form': bool,
        'has_validation': bool,
        'input_field_count': int,
        'button_count': int,
        'action_count': int
    },
    'labels': {
        'suggested_scenarios': [...],
        'priority_scores': {...}
    }
}
"""

import json
import re
import logging
from pathlib import Path
from typing import Dict, List, Any, Tuple
from collections import defaultdict
import hashlib

logger = logging.getLogger(__name__)


class TrainingDataExtractor:
    """Extract and prepare training data for ML model."""
    
    def __init__(self, project_root: Path = None):
        """Initialize extractor with paths."""
        if project_root is None:
            # Go up from ml_models/ to project root (5 levels: ml_models → python → main → src → project_root)
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.dataset_path = project_root / "resources" / "ml_data" / "datasets" / "combined-training-dataset-final.json"
        self.test_suites_dir = project_root / "test_suites"
        self.feedback_path = project_root / "resources" / "ml_data" / "datasets" / "ml_feedback.json"
        
        # Scenario categories from current system
        self.scenario_types = {
            'negative': ['invalid_input', 'empty_form', 'sql_injection', 'xss', 'security'],
            'boundary': ['min_max', 'length_limit', 'edge_values', 'overflow'],
            'edge_case': ['special_chars', 'unicode', 'rapid_submission', 'timeout'],
            'variation': ['different_data', 'alternative_path', 'permutation'],
            'compatibility': ['cross_browser', 'mobile', 'screen_size', 'accessibility'],
            'performance': ['load_time', 'concurrent_users', 'large_dataset'],
            'integration': ['api_interaction', 'database', 'third_party'],
            'workflow': ['multi_step', 'state_management', 'session']
        }
        
    def extract_all_training_data(self) -> Dict[str, Any]:
        """Extract training data from all sources."""
        logger.info("[EXTRACTOR] Starting training data extraction...")
        
        training_data = {
            'samples': [],
            'metadata': {
                'total_samples': 0,
                'source_breakdown': {},
                'scenario_distribution': defaultdict(int),
                'feature_statistics': {}
            }
        }
        
        # 1. Extract from combined dataset
        dataset_samples = self._extract_from_dataset()
        training_data['samples'].extend(dataset_samples)
        training_data['metadata']['source_breakdown']['dataset'] = len(dataset_samples)
        logger.info(f"[EXTRACTOR] Extracted {len(dataset_samples)} samples from dataset")
        
        # 2. Extract from test_suites/ (unified storage - PRIMARY SOURCE)
        suite_samples = self._extract_from_test_suites()
        training_data['samples'].extend(suite_samples)
        training_data['metadata']['source_breakdown']['test_suites'] = len(suite_samples)
        logger.info(f"[EXTRACTOR] Extracted {len(suite_samples)} samples from test_suites/")
        
        # 3. Load user feedback if available
        feedback_samples = self._load_feedback()
        if feedback_samples:
            training_data['samples'].extend(feedback_samples)
            training_data['metadata']['source_breakdown']['feedback'] = len(feedback_samples)
            logger.info(f"[EXTRACTOR] Loaded {len(feedback_samples)} samples from user feedback")
        
        # Calculate statistics
        training_data['metadata']['total_samples'] = len(training_data['samples'])
        training_data['metadata'] = self._calculate_statistics(training_data['samples'])
        
        logger.info(f"[EXTRACTOR] ✓ Total training samples: {training_data['metadata']['total_samples']}")
        
        return training_data
    
    def _extract_from_dataset(self) -> List[Dict[str, Any]]:
        """Extract training samples from combined dataset."""
        samples = []
        
        try:
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                dataset = json.load(f)
            
            for entry in dataset:
                prompt = entry.get('prompt', '').strip()
                code = entry.get('code', '')
                
                # Extract features from prompt and code
                features = self._extract_features_from_prompt(prompt, code)
                
                # Infer scenario types this pattern could generate
                scenarios = self._infer_scenarios_from_pattern(prompt, code)
                
                sample = {
                    'id': hashlib.md5(prompt.encode()).hexdigest()[:16],
                    'source': 'dataset',
                    'features': features,
                    'labels': {
                        'applicable_scenarios': scenarios,
                        'confidence': 0.8  # Base confidence for dataset
                    }
                }
                
                samples.append(sample)
        
        except Exception as e:
            logger.error(f"[EXTRACTOR] Error reading dataset: {e}")
        
        return samples
    
    def _extract_from_test_suites(self) -> List[Dict[str, Any]]:
        """Extract training samples from test_suites/ (unified storage)."""
        samples = []
        
        if not self.test_suites_dir.exists():
            logger.warning(f"[EXTRACTOR] Test suites directory not found: {self.test_suites_dir}")
            return samples
        
        # Scan all suites
        for suite_dir in self.test_suites_dir.iterdir():
            if not suite_dir.is_dir():
                continue
            
            suite_name = suite_dir.name
            
            # Scan all test cases in suite
            for test_file in suite_dir.glob("*.json"):
                try:
                    with open(test_file, 'r', encoding='utf-8') as f:
                        test_case = json.load(f)
                    
                    # Extract features from test case
                    features = self._extract_features_from_test_case(test_case)
                    
                    # Generate comprehensive scenario labels
                    scenarios = self._generate_scenario_labels(test_case, features)
                    
                    sample = {
                        'id': test_case.get('test_case_id', test_file.stem),
                        'source': 'test_suite',
                        'suite_name': suite_name,
                        'test_name': test_case.get('name', ''),
                        'features': features,
                        'labels': {
                            'applicable_scenarios': scenarios,
                            'confidence': 1.0  # High confidence - real test
                        }
                    }
                    
                    samples.append(sample)
                
                except Exception as e:
                    logger.error(f"[EXTRACTOR] Error reading test suite {test_file}: {e}")
        
        return samples
    
    def _extract_features_from_prompt(self, prompt: str, code: str) -> Dict[str, Any]:
        """Extract features from a single prompt-code pair."""
        features = {
            'prompt_text': prompt,
            'prompt_length': len(prompt),
            'has_action_verb': any(verb in prompt.lower() for verb in ['click', 'enter', 'type', 'select', 'navigate', 'fill']),
            'has_element_ref': any(elem in prompt.lower() for elem in ['button', 'input', 'field', 'dropdown', 'link', 'checkbox']),
            'action_type': self._infer_action_type(prompt),
            'element_type': self._infer_element_type(prompt),
            'has_validation': 'assert' in code.lower() or 'verify' in code.lower(),
            'has_wait': 'wait' in code.lower() or 'until' in code.lower(),
            'code_complexity': len(code.split('\n'))
        }
        
        return features
    
    def _extract_features_from_test_case(self, test_case: Dict) -> Dict[str, Any]:
        """Extract detailed features from Builder test case."""
        steps = test_case.get('steps', [])
        
        # Action analysis
        action_types = []
        element_types = []
        
        for step in steps:
            prompt = step.get('prompt', '').lower()
            action_types.append(self._infer_action_type(prompt))
            element_types.append(self._infer_element_type(prompt))
        
        # Workflow detection
        has_navigation = any('navigate' in str(s).lower() or 'go to' in str(s).lower() for s in steps)
        has_form = any('enter' in str(s).lower() or 'fill' in str(s).lower() for s in steps)
        has_submission = any('submit' in str(s).lower() or 'sign in' in str(s).lower() for s in steps)
        
        features = {
            'action_sequence': action_types,
            'element_sequence': element_types,
            'action_count': len(steps),
            'unique_actions': len(set(action_types)),
            'unique_elements': len(set(element_types)),
            'has_navigation': has_navigation,
            'has_form': has_form,
            'has_submission': has_submission,
            'workflow_type': self._classify_workflow(action_types, has_form, has_submission),
            'input_field_count': sum(1 for a in action_types if a == 'input'),
            'button_count': sum(1 for e in element_types if e == 'button'),
            'test_name': test_case.get('name', ''),
            'priority': test_case.get('priority', 'medium'),
            'tags': test_case.get('tags', [])
        }
        
        return features
    
    def _extract_features_from_actions(self, actions: List[Dict]) -> Dict[str, Any]:
        """Extract features from recorded actions."""
        action_types = []
        element_types = []
        
        for action in actions:
            action_text = action.get('action', action.get('prompt', '')).lower()
            action_types.append(self._infer_action_type(action_text))
            element_types.append(action.get('element_type', 'unknown'))
        
        has_navigation = any('navigate' in str(a).lower() for a in actions)
        has_form = any('input' in str(a).lower() or 'fill' in str(a).lower() for a in actions)
        has_submission = any('submit' in str(a).lower() or 'click' in str(a).lower() for a in actions)
        
        features = {
            'action_sequence': action_types,
            'element_sequence': element_types,
            'action_count': len(actions),
            'unique_actions': len(set(action_types)),
            'unique_elements': len(set(element_types)),
            'has_navigation': has_navigation,
            'has_form': has_form,
            'has_submission': has_submission,
            'workflow_type': self._classify_workflow(action_types, has_form, has_submission),
            'input_field_count': sum(1 for a in action_types if a == 'input'),
            'button_count': sum(1 for e in element_types if e == 'button')
        }
        
        return features
    
    def _infer_action_type(self, text: str) -> str:
        """Infer action type from text."""
        text = text.lower()
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
        elif any(word in text for word in ['wait', 'pause']):
            return 'wait'
        else:
            return 'other'
    
    def _infer_element_type(self, text: str) -> str:
        """Infer element type from text."""
        text = text.lower()
        if 'button' in text:
            return 'button'
        elif any(word in text for word in ['input', 'field', 'textbox']):
            return 'input'
        elif any(word in text for word in ['dropdown', 'select', 'combobox']):
            return 'dropdown'
        elif 'link' in text:
            return 'link'
        elif any(word in text for word in ['checkbox', 'check box']):
            return 'checkbox'
        elif 'radio' in text:
            return 'radio'
        else:
            return 'unknown'
    
    def _classify_workflow(self, actions: List[str], has_form: bool, has_submission: bool) -> str:
        """Classify the workflow type."""
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
    
    def _infer_scenarios_from_pattern(self, prompt: str, code: str) -> List[str]:
        """Infer which scenarios this pattern could generate."""
        scenarios = []
        prompt_lower = prompt.lower()
        code_lower = code.lower()
        
        # Input-related scenarios
        if any(word in prompt_lower for word in ['enter', 'type', 'input', 'fill']):
            scenarios.extend(['negative_invalid_input', 'boundary_length', 'edge_case_special_chars'])
            
            if 'email' in prompt_lower or 'email' in code_lower:
                scenarios.append('negative_invalid_email')
            if 'password' in prompt_lower or 'password' in code_lower:
                scenarios.append('negative_weak_password')
        
        # Form submission
        if 'submit' in prompt_lower or 'sign in' in prompt_lower:
            scenarios.extend(['negative_empty_form', 'edge_case_rapid_submission'])
        
        # Selection/dropdown
        if 'select' in prompt_lower or 'dropdown' in prompt_lower:
            scenarios.extend(['boundary_all_options', 'variation_different_selection'])
        
        # Navigation
        if 'navigate' in prompt_lower or 'go to' in prompt_lower:
            scenarios.extend(['negative_direct_url', 'compatibility_mobile'])
        
        # All patterns can suggest these
        scenarios.extend([
            'compatibility_cross_browser',
            'performance_load_time'
        ])
        
        return list(set(scenarios))  # Remove duplicates
    
    def _generate_scenario_labels(self, test_case: Dict, features: Dict) -> List[str]:
        """Generate comprehensive scenario labels based on test case features."""
        scenarios = []
        
        workflow = features.get('workflow_type', '')
        has_input = features.get('input_field_count', 0) > 0
        has_form = features.get('has_form', False)
        has_submission = features.get('has_submission', False)
        
        # Workflow-specific scenarios
        if workflow == 'form_submission':
            scenarios.extend([
                'negative_empty_form',
                'negative_invalid_input',
                'boundary_field_length',
                'edge_case_rapid_submission',
                'variation_different_data'
            ])
        elif workflow == 'search_workflow':
            scenarios.extend([
                'negative_empty_search',
                'boundary_search_length',
                'variation_search_terms',
                'edge_case_special_search'
            ])
        elif workflow == 'multi_page_workflow':
            scenarios.extend([
                'negative_skip_steps',
                'edge_case_back_navigation',
                'workflow_state_management'
            ])
        
        # Input-specific
        if has_input:
            scenarios.extend([
                'negative_invalid_input',
                'boundary_min_max_length',
                'edge_case_special_chars',
                'edge_case_unicode'
            ])
        
        # Form-specific
        if has_form:
            scenarios.extend([
                'negative_partial_form',
                'variation_form_data'
            ])
        
        # Universal scenarios
        scenarios.extend([
            'compatibility_cross_browser',
            'compatibility_mobile',
            'performance_load_time'
        ])
        
        return list(set(scenarios))
    
    def _generate_scenario_labels_from_actions(self, actions: List[Dict]) -> List[str]:
        """Generate scenario labels from recorded actions."""
        scenarios = []
        
        action_types = [self._infer_action_type(a.get('action', '')) for a in actions]
        
        has_input = 'input' in action_types
        has_click = 'click' in action_types
        has_navigate = 'navigate' in action_types
        has_select = 'select' in action_types
        
        if has_input:
            scenarios.extend([
                'negative_invalid_input',
                'boundary_length',
                'edge_case_special_chars'
            ])
        
        if has_click:
            scenarios.extend([
                'edge_case_rapid_click',
                'negative_disabled_button'
            ])
        
        if has_navigate:
            scenarios.extend([
                'negative_direct_access',
                'edge_case_back_button'
            ])
        
        if has_select:
            scenarios.extend([
                'boundary_all_options',
                'variation_selections'
            ])
        
        scenarios.extend([
            'compatibility_cross_browser',
            'performance_response_time'
        ])
        
        return list(set(scenarios))
    
    def _load_feedback(self) -> List[Dict[str, Any]]:
        """Load user feedback to improve training."""
        if not self.feedback_path.exists():
            return []
        
        try:
            with open(self.feedback_path, 'r', encoding='utf-8') as f:
                feedback = json.load(f)
            
            # Convert feedback to training samples
            samples = []
            for entry in feedback:
                sample = {
                    'id': entry.get('id'),
                    'source': 'feedback',
                    'features': entry.get('features', {}),
                    'labels': {
                        'applicable_scenarios': entry.get('useful_scenarios', []),
                        'rejected_scenarios': entry.get('rejected_scenarios', []),
                        'confidence': 1.0  # User-validated
                    }
                }
                samples.append(sample)
            
            return samples
        
        except Exception as e:
            logger.error(f"[EXTRACTOR] Error loading feedback: {e}")
            return []
    
    def _calculate_statistics(self, samples: List[Dict]) -> Dict[str, Any]:
        """Calculate statistics about training data."""
        stats = {
            'total_samples': len(samples),
            'source_breakdown': defaultdict(int),
            'scenario_distribution': defaultdict(int),
            'workflow_distribution': defaultdict(int),
            'avg_action_count': 0,
            'avg_scenarios_per_test': 0
        }
        
        total_actions = 0
        total_scenarios = 0
        
        for sample in samples:
            # Source breakdown
            stats['source_breakdown'][sample['source']] += 1
            
            # Scenario distribution
            scenarios = sample['labels'].get('applicable_scenarios', [])
            for scenario in scenarios:
                stats['scenario_distribution'][scenario] += 1
            total_scenarios += len(scenarios)
            
            # Workflow distribution
            workflow = sample['features'].get('workflow_type', 'unknown')
            stats['workflow_distribution'][workflow] += 1
            
            # Action count
            action_count = sample['features'].get('action_count', 0)
            total_actions += action_count
        
        if len(samples) > 0:
            stats['avg_action_count'] = total_actions / len(samples)
            stats['avg_scenarios_per_test'] = total_scenarios / len(samples)
        
        # Convert defaultdicts to regular dicts
        stats['source_breakdown'] = dict(stats['source_breakdown'])
        stats['scenario_distribution'] = dict(stats['scenario_distribution'])
        stats['workflow_distribution'] = dict(stats['workflow_distribution'])
        
        return stats
    
    def save_training_data(self, training_data: Dict, output_path: Path = None):
        """Save extracted training data to file."""
        if output_path is None:
            output_path = self.project_root / "resources" / "ml_data" / "datasets" / "ml_training_data.json"
        
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(training_data, f, indent=2)
        
        logger.info(f"[EXTRACTOR] ✓ Saved training data to {output_path}")
        logger.info(f"[EXTRACTOR] Total samples: {training_data['metadata']['total_samples']}")
        logger.info(f"[EXTRACTOR] Average scenarios per test: {training_data['metadata']['avg_scenarios_per_test']:.1f}")


if __name__ == "__main__":
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='[%(levelname)s] %(message)s'
    )
    
    # Extract training data
    extractor = TrainingDataExtractor()
    training_data = extractor.extract_all_training_data()
    extractor.save_training_data(training_data)
    
    print(f"\n✓ Training data extraction complete!")
    print(f"  Total samples: {training_data['metadata']['total_samples']}")
    print(f"  Sources: {training_data['metadata']['source_breakdown']}")
    print(f"  Average actions per test: {training_data['metadata']['avg_action_count']:.1f}")
    print(f"  Average scenarios per test: {training_data['metadata']['avg_scenarios_per_test']:.1f}")
