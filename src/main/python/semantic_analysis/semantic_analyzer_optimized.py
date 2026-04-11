"""
Optimized Semantic Code Analysis - High-performance test intent analysis
Improved efficiency through caching, lazy loading, and optimized algorithms.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional, Set, Tuple
from collections import defaultdict
from functools import lru_cache
import time

class OptimizedSemanticAnalyzer:
    """High-performance semantic analyzer with caching and lazy loading."""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """Initialize with lazy loading strategy."""
        self.dataset_path = dataset_path or self._get_default_dataset_path()
        
        # Lazy-loaded attributes
        self._workflow_patterns = None
        self._page_contexts = None
        self._action_sequences = None
        
        # Optimized data structures
        self._intent_keywords = self._build_intent_keywords()
        self._entity_pattern = re.compile(
            r'(?:(\w+)\s+(?:field|button|link|dropdown|checkbox|input))|'
            r'(?:enter\s+[\w@.]+\s+in\s+(\w+))|'
            r'(?:click\s+(\w+))|'
            r'(?:select\s+(\w+))',
            re.IGNORECASE
        )
        self._workflow_keywords = self._build_workflow_keywords()
        
        print(f"[SEMANTIC] Initialized with lazy loading (dataset: {os.path.basename(self.dataset_path)})")
    
    def _get_default_dataset_path(self) -> str:
        """Get default dataset path."""
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..', '..'))
        # Use combined dataset with generic patterns
        return os.path.join(project_root, 'resources', 'ml_data', 'datasets', 'combined-training-dataset-final.json')
    
    def _build_intent_keywords(self) -> Dict[str, Set[str]]:
        """Pre-compile intent detection keywords for O(1) lookup."""
        return {
            'login': {'login', 'sign in', 'signin', 'authenticate', 'credentials', 'log in'},
            'registration': {'register', 'sign up', 'signup', 'create account', 'new user'},
            'navigation': {'navigate', 'go to', 'goto', 'open', 'click link', 'visit'},
            'form_submission': {'submit', 'fill', 'enter', 'input', 'type', 'send'},
            'verification': {'verify', 'check', 'assert', 'validate', 'ensure', 'confirm'},
            'search': {'search', 'find', 'look for', 'query', 'filter'},
            'selection': {'select', 'choose', 'pick', 'dropdown', 'option'},
            'upload': {'upload', 'attach', 'file', 'document', 'browse'}
        }
    
    def _build_workflow_keywords(self) -> Dict[str, Set[str]]:
        """Pre-compile workflow keywords for O(1) lookup."""
        return {
            'user_authentication': {'email', 'password', 'login', 'sign in', 'signin'},
            'user_registration': {'email', 'password', 'confirm', 'register', 'sign up', 'signup'},
            'profile_management': {'profile', 'settings', 'account', 'update', 'edit'},
            'license_application': {'license', 'apply', 'application', 'permit'},
            'search_filter': {'search', 'filter', 'query', 'find', 'results'},
            'data_entry': {'form', 'fill', 'input', 'enter', 'data'},
            'file_upload': {'upload', 'file', 'attach', 'document', 'browse'}
        }
    
    @property
    def workflow_patterns(self) -> Dict:
        """Lazy load workflow patterns only when needed."""
        if self._workflow_patterns is None:
            self._load_domain_knowledge()
        return self._workflow_patterns
    
    @property
    def page_contexts(self) -> Dict:
        """Lazy load page contexts only when needed."""
        if self._page_contexts is None:
            self._load_domain_knowledge()
        return self._page_contexts
    
    @property
    def action_sequences(self) -> defaultdict:
        """Lazy load action sequences only when needed."""
        if self._action_sequences is None:
            self._load_domain_knowledge()
        return self._action_sequences
    
    def _load_domain_knowledge(self):
        """Load workflow patterns and page contexts from dataset (lazy)."""
        if self._workflow_patterns is not None:
            return  # Already loaded
        
        start_time = time.time()
        self._workflow_patterns = {}
        self._page_contexts = {}
        self._action_sequences = defaultdict(list)
        
        try:
            if not os.path.exists(self.dataset_path):
                print(f"[WARNING] Dataset not found: {self.dataset_path}")
                return
            
            with open(self.dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry in data:
                page_object = entry.get('page_object', '')
                method = entry.get('method', '')
                steps = entry.get('steps', [])
                
                # Store workflow patterns
                workflow_key = f"{page_object}.{method}"
                self._workflow_patterns[workflow_key] = {
                    'description': entry.get('description', ''),
                    'steps': steps,
                    'page': page_object
                }
                
                # Build action sequences for pattern detection
                if steps:
                    action_seq = tuple(s.get('action', '') for s in steps)
                    self._action_sequences[action_seq].append(workflow_key)
                
                # Store page context
                if page_object not in self._page_contexts:
                    self._page_contexts[page_object] = []
                self._page_contexts[page_object].append(method)
            
            load_time = (time.time() - start_time) * 1000
            print(f"[SEMANTIC] Loaded {len(self._workflow_patterns)} patterns in {load_time:.2f}ms")
        except Exception as e:
            print(f"[ERROR] Failed to load domain knowledge: {e}")
            self._workflow_patterns = {}
            self._page_contexts = {}
    
    @lru_cache(maxsize=256)
    def analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze user prompt to understand test intent (cached for performance).
        
        Uses LRU cache to avoid re-analyzing identical prompts.
        """
        prompt_lower = prompt.lower()
        
        # Fast intent detection using pre-compiled keywords
        detected_intent = 'unknown'
        max_matches = 0
        
        for intent, keywords in self._intent_keywords.items():
            # Count keyword matches using set intersection
            matches = sum(1 for keyword in keywords if keyword in prompt_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        # Fast entity extraction using compiled regex
        entities = self._extract_entities_fast(prompt_lower)
        
        # Determine workflow using optimized lookup
        workflow = self._identify_workflow_fast(detected_intent, entities, prompt_lower)
        
        # Calculate confidence - improved formula for better accuracy
        # Base confidence from keyword matches (more generous)
        keyword_confidence = min(max_matches * 0.3, 0.7)  # Up to 70% from keywords
        
        # Entity confidence (up to 20% from entities)
        entity_confidence = min(len(entities) * 0.1, 0.2)
        
        # Bonus if we have both keywords and entities
        synergy_bonus = 0.1 if max_matches > 0 and len(entities) > 0 else 0
        
        # Final confidence (minimum 0.5 if we detected anything)
        confidence = max(keyword_confidence + entity_confidence + synergy_bonus, 0.5 if max_matches > 0 else 0.2)
        confidence = min(confidence, 0.95)  # Cap at 95%
        
        return {
            'intent': detected_intent,
            'entities': entities,
            'workflow': workflow,
            'confidence': confidence,
            'prompt': prompt
        }
    
    def _extract_entities_fast(self, prompt_lower: str) -> List[str]:
        """Fast entity extraction using compiled regex pattern."""
        matches = self._entity_pattern.findall(prompt_lower)
        # Flatten tuple results and filter empty strings
        entities = [item for match in matches for item in match if item]
        return list(set(entities))  # Remove duplicates
    
    def _identify_workflow_fast(self, intent: str, entities: List[str], prompt: str) -> str:
        """Fast workflow identification using pre-compiled keyword sets."""
        for workflow, keywords in self._workflow_keywords.items():
            # Use set intersection for O(1) average case
            if any(keyword in prompt for keyword in keywords):
                return workflow
        return 'general_interaction'
    
    def suggest_scenarios(self, recorded_actions: List[Dict], current_page: str = '', context: Dict = None) -> List[Dict[str, Any]]:
        """
        Suggest test scenarios based on recorded actions (optimized).
        
        Args:
            recorded_actions: List of action dictionaries
            current_page: Current page context (optional)
            context: Enhanced context with test name, code, etc (optional)
        
        Returns prioritized list of test scenarios without redundant processing.
        """
        suggestions = []
        
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
            
            # If new format with embedded actions, use those
            if 'actions' in context and context['actions']:
                recorded_actions = context['actions']
        
        # Pre-analyze action types once
        action_types = set()
        action_texts = []
        
        for a in recorded_actions:
            action_type = a.get('action_type', a.get('type', ''))
            action_text = a.get('action', a.get('prompt', ''))
            
            if action_type:
                action_types.add(action_type.lower())
            if action_text:
                action_texts.append(action_text.lower())
        
        # Analyze code patterns if available
        code_patterns = self._analyze_code_patterns(generated_code) if generated_code else {}
        
        # Detect what types of actions are in the test
        has_input = any(t in action_types for t in ['input', 'fill', 'enter', 'type'])
        has_input = has_input or any('enter' in t or 'type' in t or 'fill' in t for t in action_texts)
        
        has_click = any(t in action_types for t in ['click', 'button'])
        has_click = has_click or any('click' in t or 'button' in t for t in action_texts)
        
        has_submit = has_click and any('submit' in str(a).lower() for a in recorded_actions)
        has_submit = has_submit or any('submit' in t for t in action_texts)
        
        has_select = any(t in action_types for t in ['select', 'dropdown'])
        has_select = has_select or any('select' in t or 'dropdown' in t for t in action_texts)
        
        has_navigation = any('navigate' in t or 'go to' in t or 'open' in t for t in action_texts)
        
        # Generate comprehensive suggestions based on test patterns
        if has_input:
            suggestions.extend(self._get_enhanced_input_scenarios(recorded_actions, test_name, code_patterns))
        
        if has_submit:
            suggestions.extend(self._get_submit_scenarios(recorded_actions))
        
        if has_select:
            suggestions.extend(self._get_selection_scenarios(recorded_actions))
        
        if has_navigation:
            suggestions.append({
                'type': 'negative',
                'title': 'Test Direct URL Access',
                'scenario': 'Test accessing protected pages without proper navigation',
                'description': 'Verify that protected pages redirect or show error when accessed directly',
                'priority': 'high',
                'steps': ['Copy target page URL', 'Open in new browser session', 'Verify access is denied or redirected']
            })
        
        # Workflow-based suggestions
        if len(suggestions) < 8:
            workflow_suggestions = self._get_workflow_based_scenarios(test_name, test_description, recorded_actions)
            suggestions.extend(workflow_suggestions)
        
        # Add more test-specific scenarios based on actual actions
        test_specific = self._get_test_specific_scenarios(recorded_actions, test_name, action_texts)
        suggestions.extend(test_specific)
        
        # Essential edge cases
        suggestions.extend(self._get_comprehensive_edge_cases(has_submit, has_input))
        
        # Add data variation scenarios
        suggestions.extend(self._get_data_variation_scenarios(has_input))
        
        # Cross-browser and compatibility
        suggestions.append({
            'type': 'compatibility',
            'title': 'Cross-Browser Compatibility',
            'scenario': 'Test across different browsers',
            'description': 'Verify functionality works consistently across Chrome, Firefox, Safari, and Edge',
            'priority': 'medium',
            'steps': ['Execute test on Chrome', 'Execute test on Firefox', 'Execute test on Edge', 'Compare results and verify consistency']
        })
        
        # Mobile responsiveness
        suggestions.append({
            'type': 'compatibility',
            'title': 'Mobile Responsiveness',
            'scenario': 'Test on mobile devices and screen sizes',
            'description': 'Verify functionality works correctly on mobile browsers and different screen sizes',
            'priority': 'low',
            'steps': ['Execute test on mobile viewport (375x667)', 'Test on tablet viewport (768x1024)', 'Verify all elements are accessible and clickable', 'Test landscape and portrait orientations']
        })
        
        # Add titles if missing (backward compatibility)
        for s in suggestions:
            if 'title' not in s:
                s['title'] = s.get('scenario', 'Test Scenario')
        
        return suggestions
    
    def _analyze_code_patterns(self, code: str) -> Dict[str, Any]:
        """Analyze generated code to extract patterns for better suggestions."""
        patterns = {
            'has_wait': 'wait' in code.lower() or 'until' in code.lower(),
            'has_validation': 'assert' in code.lower() or 'verify' in code.lower(),
            'has_loops': 'for ' in code or 'while ' in code,
            'has_error_handling': 'try:' in code or 'except' in code,
            'field_types': set()
        }
        
        # Extract field types from code
        if 'email' in code.lower():
            patterns['field_types'].add('email')
        if 'password' in code.lower():
            patterns['field_types'].add('password')
        if 'phone' in code.lower():
            patterns['field_types'].add('phone')
        if 'date' in code.lower():
            patterns['field_types'].add('date')
        
        return patterns
    
    def _get_enhanced_input_scenarios(self, actions: List[Dict], test_name: str, code_patterns: Dict) -> List[Dict]:
        """Generate enhanced input-related test scenarios."""
        scenarios = []
        
        # Negative input test
        scenarios.append({
            'type': 'negative',
            'title': 'Invalid Input Testing',
            'scenario': 'Test with invalid and malicious inputs',
            'description': 'Verify proper validation and error messages for invalid inputs including SQL injection, XSS attacks, and malformed data',
            'priority': 'high',
            'steps': self._generate_enhanced_negative_test(actions, code_patterns),
            'expected_result': 'Application should reject invalid inputs, display appropriate error messages, and prevent security vulnerabilities'
        })
        
        # Boundary test
        scenarios.append({
            'type': 'boundary',
            'title': 'Boundary Value Testing',
            'scenario': 'Test input limits and boundaries',
            'description': 'Verify behavior at minimum, maximum, and edge values for all input fields',
            'priority': 'high',
            'steps': [
                'Enter minimum valid length (1 character)',
                'Enter maximum allowed length (e.g., 255 characters)',
                'Attempt to exceed maximum length',
                'Test with zero/empty values',
                'Test with exactly at boundary values (e.g., max-1, max, max+1)',
                'Verify appropriate handling at each boundary'
            ],
            'expected_result': 'Application should handle boundary values gracefully and enforce length restrictions'
        })
        
        return scenarios
    
    def _generate_enhanced_negative_test(self, actions: List[Dict], code_patterns: Dict) -> List[str]:
        """Generate comprehensive negative test steps."""
        steps = [
            'Test with empty/null inputs in required fields',
            'Test with whitespace-only inputs',
            'Test with special characters: !@#$%^&*()[]{}|\\:;"\'<>?,./~`'
        ]
        
        # Add field-specific tests based on code patterns
        if 'email' in code_patterns.get('field_types', set()):
            steps.extend([
                'Test email field with invalid formats: "notanemail", "user@", "@domain.com"',
                'Test email with SQL injection: "admin\'--", "1\' OR \'1\'=\'1"'
            ])
        
        if 'password' in code_patterns.get('field_types', set()):
            steps.extend([
                'Test password with too few characters',
                'Test password without required character types'
            ])
        
        steps.extend([
            'Test with Unicode characters: 你好, مرحبا, Здравствуй',
            'Test with XSS payloads: <script>alert(1)</script>, <img src=x onerror=alert(1)>',
            'Verify all validation errors are displayed correctly'
        ])
        
        return steps
    
    def _get_submit_scenarios(self, actions: List[Dict]) -> List[Dict]:
        """Generate form submission related scenarios."""
        return [{
            'type': 'negative',
            'title': 'Empty Form Submission',
            'scenario': 'Test form submission without required fields',
            'description': 'Verify that validation prevents submission and displays appropriate messages',
            'priority': 'high',
            'steps': [
                'Leave all required fields empty',
                'Click submit button',
                'Verify form is not submitted',
                'Verify error messages are displayed for each required field',
                'Verify page remains on form with errors highlighted'
            ],
            'expected_result': 'Form submission blocked with clear validation messages'
        }, {
            'type': 'edge_case',
            'title': 'Rapid Form Submission',
            'scenario': 'Test rapid/double submission',
            'description': 'Verify form cannot be submitted multiple times rapidly (duplicate submission prevention)',
            'priority': 'medium',
            'steps': [
                'Fill form with valid data',
                'Click submit button multiple times rapidly',
                'Verify only one submission is processed',
                'Verify no duplicate records created'
            ],
            'expected_result': 'Only one submission processed, button disabled after first click'
        }]
    
    def _get_selection_scenarios(self, actions: List[Dict]) -> List[Dict]:
        """Generate dropdown/selection related scenarios."""
        return [{
            'type': 'boundary',
            'title': 'Dropdown Selection Testing',
            'scenario': 'Test all dropdown options',
            'description': 'Verify all dropdown values can be selected and trigger correct behavior',
            'priority': 'medium',
            'steps': [
                'Verify dropdown displays all expected options',
                'Test selecting first option',
                'Test selecting last option',
                'Test selecting middle options',
                'Verify dependent fields update correctly',
                'Test with no selection (if optional)'
            ],
            'expected_result': 'All options selectable, dependent fields update correctly'
        }]
    
    def _get_workflow_based_scenarios(self, test_name: str, description: str, actions: List[Dict]) -> List[Dict]:
        """Generate scenarios based on workflow understanding."""
        scenarios = []
        
        workflow_text = f"{test_name} {description}".lower()
        
        # Login workflow variations
        if any(word in workflow_text for word in ['login', 'signin', 'sign in', 'authenticate']):
            scenarios.append({
                'type': 'negative',
                'title': 'Invalid Login Credentials',
                'scenario': 'Test login with various invalid credentials',
                'description': 'Verify proper handling of wrong username, wrong password, and locked accounts',
                'priority': 'high',
                'steps': [
                    'Test with invalid username',
                    'Test with invalid password',
                    'Test with both invalid',
                    'Test with SQL injection attempts',
                    'Verify error messages do not reveal if username exists',
                    'Test account lockout after multiple failed attempts'
                ],
                'expected_result': 'Secure error handling without revealing sensitive information'
            })
        
        # Registration workflow variations
        if any(word in workflow_text for word in ['register', 'signup', 'sign up', 'create account']):
            scenarios.append({
                'type': 'negative',
                'title': 'Duplicate Registration',
                'scenario': 'Test registration with existing credentials',
                'description': 'Verify system prevents duplicate registrations',
                'priority': 'high',
                'steps': [
                    'Register with new email',
                    'Attempt to register again with same email',
                    'Verify appropriate error message',
                    'Test with existing username but different email',
                    'Verify username uniqueness is enforced'
                ],
                'expected_result': 'Duplicate prevention with clear error messages'
            })
        
        return scenarios
    
    def _get_comprehensive_edge_cases(self, has_submit: bool, has_input: bool) -> List[Dict]:
        """Generate comprehensive edge case scenarios."""
        edge_cases = [
            {
                'type': 'edge_case',
                'title': 'Session Timeout Handling',
                'scenario': 'Test behavior after session expires',
                'description': 'Verify application handles expired sessions gracefully',
                'priority': 'medium',
                'steps': [
                    'Start test workflow',
                    'Wait for session to expire (or manually clear session)',
                    'Attempt to continue operation',
                    'Verify redirect to login',
                    'Verify appropriate session timeout message'
                ],
                'expected_result': 'Graceful handling with redirect and preserved data where appropriate'
            },
            {
                'type': 'edge_case',
                'title': 'Network Interruption',
                'scenario': 'Test with simulated network issues',
                'description': 'Verify application handles network failures gracefully',
                'priority': 'medium',
                'steps': [
                    'Start operation',
                    'Simulate network interruption',
                    'Verify appropriate error message',
                    'Restore network',
                    'Verify recovery or retry mechanism'
                ],
                'expected_result': 'Clear error messages and recovery options provided'
            }
        ]
        
        if has_submit:
            edge_cases.append({
                'type': 'edge_case',
                'title': 'Concurrent Updates',
                'scenario': 'Test simultaneous form submissions',
                'description': 'Verify data integrity with concurrent operations',
                'priority': 'medium',
                'steps': [
                    'Open same form in multiple tabs/browsers',
                    'Submit from multiple sources simultaneously',
                    'Verify data integrity',
                    'Verify no race conditions or conflicts'
                ],
                'expected_result': 'Proper conflict resolution or locking mechanism'
            })
        
        if has_input:
            edge_cases.append({
                'type': 'variation',
                'title': 'Copy-Paste Input',
                'scenario': 'Test with copy-pasted data',
                'description': 'Verify handling of pasted content including formatting',
                'priority': 'low',
                'steps': [
                    'Copy data from external source (with formatting)',
                    'Paste into input fields',
                    'Verify formatting is handled correctly',
                    'Verify no hidden characters cause issues'
                ],
                'expected_result': 'Clean data processing regardless of paste source'
            })
        
        return edge_cases
    
    def _get_test_specific_scenarios(self, actions: List[Dict], test_name: str, action_texts: List[str]) -> List[Dict]:
        """Generate test-specific scenarios based on actual test steps."""
        scenarios = []
        
        # Analyze what the test is actually doing
        action_descriptions = []
        for action in actions:
            action_text = action.get('action', action.get('prompt', ''))
            action_descriptions.append(action_text)
        
        # If test has multiple steps, create a scenario that tests them in reverse order
        if len(actions) > 2:
            scenarios.append({
                'type': 'variation',
                'title': 'Alternative Workflow Sequence',
                'scenario': 'Test workflow steps in different order',
                'description': f'Verify if steps can be executed in alternative sequences (where logically possible)',
                'priority': 'low',
                'steps': self._generate_alternative_steps(action_descriptions),
                'expected_result': 'System handles valid alternative sequences or prevents invalid ones with clear messages'
            })
        
        # Test with incomplete workflow
        if len(actions) > 1:
            scenarios.append({
                'type': 'negative',
                'title': 'Incomplete Workflow Completion',
                'scenario': 'Test stopping midway through the workflow',
                'description': 'Verify proper handling when user doesn\'t complete all steps',
                'priority': 'medium',
                'steps': [
                    f'Execute first {len(actions)//2} steps only',
                    'Close browser or navigate away',
                    'Return to application',
                    'Verify state is handled correctly',
                    'Verify can resume or restart workflow'
                ],
                'expected_result': 'Partial completion handled gracefully with ability to resume or clear state'
            })
        
        # Test performance with repeated execution
        scenarios.append({
            'type': 'variation',
            'title': 'Repeated Execution',
            'scenario': 'Execute the same workflow multiple times in succession',
            'description': 'Verify consistency and performance with repeated executions',
            'priority': 'low',
            'steps': [
                'Execute complete workflow',
                'Execute again immediately',
                'Execute 5-10 times',
                'Verify performance remains consistent',
                'Verify no data or state conflicts'
            ],
            'expected_result': 'Consistent behavior across multiple executions'
        })
        
        return scenarios
    
    def _generate_alternative_steps(self, action_descriptions: List[str]) -> List[str]:
        """Generate alternative step sequences."""
        return [
            f'Review original sequence: {", ".join(action_descriptions[:3] + ["..."] if len(action_descriptions) > 3 else action_descriptions)}',
            'Identify steps that could be executed in different order',
            'Test alternative sequence (skip to last step first if independent)',
            'Test with middle steps first then initial steps',
            'Verify either success or appropriate error messages'
        ]
    
    def _get_data_variation_scenarios(self, has_input: bool) -> List[Dict]:
        """Generate data variation scenarios."""
        scenarios = []
        
        if has_input:
            scenarios.extend([
                {
                    'type': 'variation',
                    'title': 'Alternative Valid Data Sets',
                    'scenario': 'Test with multiple sets of valid data',
                    'description': 'Verify consistency across different valid data inputs',
                    'priority': 'medium',
                    'steps': [
                        'Execute with Data Set 1 (e.g., user1@test.com, name: John Doe)',
                        'Execute with Data Set 2 (e.g., user2@test.com, name: Jane Smith)',
                        'Execute with Data Set 3 (different format variations)',
                        'Verify all executions succeed with same expected outcome',
                        'Verify data isolation (no cross-contamination)'
                    ],
                    'expected_result': 'Consistent behavior regardless of specific valid data used'
                },
                {
                    'type': 'boundary',
                    'title': 'International Character Sets',
                    'scenario': 'Test with international and special characters',
                    'description': 'Verify support for UTF-8 characters including accents, Asian characters, Arabic, etc.',
                    'priority': 'medium',
                    'steps': [
                        'Test with French accents: François, José, Müller',
                        'Test with Asian characters: 田中太郎, 김민준',
                        'Test with Arabic: محمد أحمد',
                        'Test with emojis: John 😀 Doe',
                        'Verify proper storage, retrieval, and display'
                    ],
                    'expected_result': 'Full UTF-8 support with proper rendering'
                },
                {
                    'type': 'boundary',
                    'title': 'Extremely Long Input Values',
                    'scenario': 'Test with very long text inputs',
                    'description': 'Verify system handles or restricts exceptionally long inputs',
                    'priority': 'high',
                    'steps': [
                        'Enter text with 500 characters',
                        'Enter text with 1000 characters',
                        'Enter text with 5000+ characters',
                        'Verify either acceptance with proper storage or appropriate length restriction',
                        'Verify UI doesn\'t break with long values'
                    ],
                    'expected_result': 'Proper length validation or truncation with user notification'
                }
            ])
        
        return scenarios
    
    def _get_input_scenarios(self, recorded_actions: List[Dict]) -> List[Dict]:
        """Generate input-related test scenarios efficiently."""
        scenarios = []
        
        # Negative input test
        scenarios.append({
            'type': 'negative',
            'scenario': 'Test with invalid input',
            'description': 'Verify error messages for invalid/empty inputs',
            'priority': 'high',
            'steps': self._generate_negative_input_test(recorded_actions)
        })
        
        # Boundary test
        scenarios.append({
            'type': 'boundary',
            'scenario': 'Test input length limits',
            'description': 'Test minimum, maximum, and over-limit inputs',
            'priority': 'medium',
            'steps': ['Enter 1 character', 'Enter maximum characters', 'Enter over limit']
        })
        
        return scenarios
    
    def _generate_negative_input_test(self, recorded_actions: List[Dict]) -> List[str]:
        """Generate negative test steps (optimized)."""
        steps = []
        input_fields = [a.get('element', {}).get('name', 'field') 
                       for a in recorded_actions 
                       if a.get('action_type') == 'input']
        
        # Generate once per unique field
        unique_fields = set(input_fields)
        for field in unique_fields:
            steps.extend([
                f"Enter invalid data in {field}",
                f"Leave {field} empty"
            ])
        
        steps.append("Attempt to submit and verify error messages")
        return steps
    
    def _detect_workflow_from_actions_fast(self, actions: List[Dict]) -> str:
        """Fast workflow detection (only loads data if needed)."""
        if not actions:
            return ''
        
        action_seq = tuple(a.get('action_type', '') for a in actions)
        
        # Check if we need to load domain knowledge
        if action_seq in self.action_sequences:
            workflows = self.action_sequences[action_seq]
            return workflows[0] if workflows else ''
        
        return ''
    
    def _get_workflow_variations(self, workflow: str, limit: int = 2) -> List[Dict]:
        """Get workflow variations (limited to save resources)."""
        if workflow not in self.workflow_patterns:
            return []
        
        suggestions = []
        current_page = self.workflow_patterns[workflow]['page']
        
        # Find similar workflows on same page (limited)
        count = 0
        for wf_key, wf_data in self.workflow_patterns.items():
            if count >= limit:
                break
            if wf_data['page'] == current_page and wf_key != workflow:
                suggestions.append({
                    'type': 'variation',
                    'scenario': f'Test related workflow: {wf_key}',
                    'description': wf_data['description'],
                    'priority': 'low',
                    'steps': [s.get('prompt', '') for s in wf_data['steps'][:3]]  # Limit steps
                })
                count += 1
        
        return suggestions
    
    def _get_essential_edge_cases(self, has_submit: bool) -> List[Dict]:
        """Generate essential edge case scenarios only."""
        edge_cases = []
        
        # Session timeout (always relevant)
        edge_cases.append({
            'type': 'edge_case',
            'scenario': 'Test session timeout',
            'description': 'Verify behavior after session expires',
            'priority': 'low',
            'steps': ['Start workflow', 'Wait for session timeout', 'Try to continue']
        })
        
        # Concurrent submissions (only if has submit)
        if has_submit:
            edge_cases.append({
                'type': 'edge_case',
                'scenario': 'Test concurrent submissions',
                'description': 'Verify handling of simultaneous form submissions',
                'priority': 'medium',
                'steps': ['Open multiple tabs', 'Submit same form', 'Verify data integrity']
            })
        
        return edge_cases
    
    def generate_test_report(self, intent_analysis: Dict, suggestions: List[Dict]) -> str:
        """Generate compact test scenario report."""
        entities_str = ', '.join(intent_analysis['entities']) if intent_analysis['entities'] else 'None'
        
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    SEMANTIC TEST ANALYSIS REPORT                     ║
╚══════════════════════════════════════════════════════════════════════╝

📋 TEST INTENT ANALYSIS
───────────────────────────────────────────────────────────────────────
Intent:      {intent_analysis['intent'].upper()}
Workflow:    {intent_analysis['workflow'].replace('_', ' ').title()}
Confidence:  {intent_analysis['confidence']:.0%}
Entities:    {entities_str}

🎯 SUGGESTED TEST SCENARIOS ({len(suggestions)} scenarios)
───────────────────────────────────────────────────────────────────────
"""
        
        # Group by priority efficiently
        priority_groups = {'high': [], 'medium': [], 'low': []}
        for s in suggestions:
            priority_groups[s['priority']].append(s)
        
        for priority in ['high', 'medium', 'low']:
            scenarios = priority_groups[priority]
            if scenarios:
                priority_label = '🔴' if priority == 'high' else '🟡' if priority == 'medium' else '🟢'
                report += f"\n{priority_label} {priority.upper()} PRIORITY ({len(scenarios)} scenarios)\n"
                for i, scenario in enumerate(scenarios, 1):
                    report += f"\n  {i}. {scenario['scenario']}\n"
                    report += f"     Type: {scenario['type'].upper()}\n"
                    report += f"     {scenario['description']}\n"
                    if scenario.get('steps'):
                        report += f"     Steps: {len(scenario['steps'])} total\n"
                        # Show only first 2 steps for brevity
                        for step in scenario['steps'][:2]:
                            report += f"       • {step}\n"
        
        report += "\n" + "═" * 72 + "\n"
        return report
    
    def clear_cache(self):
        """Clear the LRU cache for analyze_intent."""
        self.analyze_intent.cache_clear()
        print("[SEMANTIC] Cache cleared")
    
    def get_cache_info(self) -> Dict:
        """Get cache statistics."""
        cache_info = self.analyze_intent.cache_info()
        return {
            'hits': cache_info.hits,
            'misses': cache_info.misses,
            'size': cache_info.currsize,
            'max_size': cache_info.maxsize,
            'hit_rate': f"{(cache_info.hits / (cache_info.hits + cache_info.misses) * 100):.1f}%" 
                       if (cache_info.hits + cache_info.misses) > 0 else '0%'
        }


# Global instance
_semantic_analyzer = None

def get_analyzer() -> OptimizedSemanticAnalyzer:
    """Get global semantic analyzer instance."""
    global _semantic_analyzer
    if _semantic_analyzer is None:
        _semantic_analyzer = OptimizedSemanticAnalyzer()
    return _semantic_analyzer

def reset_analyzer():
    """Reset global instance (useful for testing)."""
    global _semantic_analyzer
    _semantic_analyzer = None
