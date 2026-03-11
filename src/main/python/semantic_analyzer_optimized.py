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
        project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
        return os.path.join(project_root, 'src', 'resources', 'sircon_ui_dataset.json')
    
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
        
        # Calculate confidence
        confidence = min(max_matches * 0.2 + len(entities) * 0.1, 0.95)
        
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
    
    def suggest_scenarios(self, recorded_actions: List[Dict], current_page: str = '') -> List[Dict[str, Any]]:
        """
        Suggest test scenarios based on recorded actions (optimized).
        
        Returns prioritized list of test scenarios without redundant processing.
        """
        suggestions = []
        
        # Pre-analyze action types once
        action_types = set(a.get('action_type', '') for a in recorded_actions)
        has_input = 'input' in action_types
        has_click = 'click' in action_types
        has_submit = has_click and any('submit' in str(a).lower() for a in recorded_actions)
        
        # Generate suggestions based on action analysis
        if has_input:
            suggestions.extend(self._get_input_scenarios(recorded_actions))
        
        if has_submit:
            suggestions.append({
                'type': 'negative',
                'scenario': 'Test form submission without required fields',
                'description': 'Verify validation messages appear',
                'priority': 'high',
                'steps': ['Leave required fields empty', 'Click submit', 'Verify error messages']
            })
        
        # Workflow variations (only if needed)
        if len(suggestions) < 5:
            workflow = self._detect_workflow_from_actions_fast(recorded_actions)
            if workflow:
                suggestions.extend(self._get_workflow_variations(workflow, limit=2))
        
        # Edge cases (lightweight scenarios)
        suggestions.extend(self._get_essential_edge_cases(has_submit))
        
        # Cross-browser test (single scenario)
        suggestions.append({
            'type': 'compatibility',
            'scenario': 'Cross-browser testing',
            'description': 'Test on Chrome, Firefox, Edge',
            'priority': 'medium',
            'steps': ['Run same test on different browsers']
        })
        
        return suggestions
    
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
