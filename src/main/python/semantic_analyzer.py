"""
Semantic Code Analysis - Understand test intent and suggest test scenarios
Analyzes user actions, page context, and workflow patterns to suggest comprehensive test scenarios.
"""

import json
import os
import re
from typing import List, Dict, Any, Optional
from collections import defaultdict

class SemanticAnalyzer:
    """Analyzes test intent and suggests comprehensive test scenarios."""
    
    def __init__(self, dataset_path: Optional[str] = None):
        """Initialize semantic analyzer with domain knowledge."""
        self.workflow_patterns = {}
        self.page_contexts = {}
        self.action_sequences = defaultdict(list)
        
        if dataset_path is None:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            project_root = os.path.abspath(os.path.join(script_dir, '..', '..', '..'))
            dataset_path = os.path.join(project_root, 'src', 'resources', 'sircon_ui_dataset.json')
        
        self._load_domain_knowledge(dataset_path)
    
    def _load_domain_knowledge(self, dataset_path: str):
        """Load workflow patterns and page contexts from dataset."""
        try:
            with open(dataset_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            for entry in data:
                page_object = entry.get('page_object', '')
                method = entry.get('method', '')
                steps = entry.get('steps', [])
                
                # Store workflow patterns
                workflow_key = f"{page_object}.{method}"
                self.workflow_patterns[workflow_key] = {
                    'description': entry.get('description', ''),
                    'steps': steps,
                    'page': page_object
                }
                
                # Build action sequences for pattern detection
                if steps:
                    action_seq = [s.get('action', '') for s in steps]
                    self.action_sequences[tuple(action_seq)].append(workflow_key)
                
                # Store page context
                if page_object not in self.page_contexts:
                    self.page_contexts[page_object] = []
                self.page_contexts[page_object].append(method)
            
            print(f"[SEMANTIC] Loaded {len(self.workflow_patterns)} workflow patterns")
            print(f"[SEMANTIC] Identified {len(self.page_contexts)} page contexts")
        except Exception as e:
            print(f"[WARNING] Could not load domain knowledge: {e}")
    
    def analyze_intent(self, prompt: str) -> Dict[str, Any]:
        """
        Analyze user prompt to understand test intent.
        
        Returns:
            {
                'intent': 'login' | 'registration' | 'navigation' | 'form_submission' | 'verification',
                'entities': ['email', 'password', 'button'],
                'workflow': 'user_authentication',
                'confidence': 0.85
            }
        """
        prompt_lower = prompt.lower()
        
        # Intent detection patterns
        intent_patterns = {
            'login': ['login', 'sign in', 'authenticate', 'credentials'],
            'registration': ['register', 'sign up', 'create account', 'new user'],
            'navigation': ['navigate', 'go to', 'open', 'click link'],
            'form_submission': ['submit', 'fill', 'enter', 'input'],
            'verification': ['verify', 'check', 'assert', 'validate'],
            'search': ['search', 'find', 'look for', 'query'],
            'selection': ['select', 'choose', 'pick'],
            'upload': ['upload', 'attach', 'file']
        }
        
        # Detect intent
        detected_intent = 'unknown'
        max_matches = 0
        
        for intent, keywords in intent_patterns.items():
            matches = sum(1 for keyword in keywords if keyword in prompt_lower)
            if matches > max_matches:
                max_matches = matches
                detected_intent = intent
        
        # Extract entities (fields, elements)
        entities = []
        entity_patterns = [
            r'(\w+)\s+field',
            r'(\w+)\s+button',
            r'(\w+)\s+link',
            r'enter\s+[\w@.]+\s+in\s+(\w+)',
            r'click\s+(\w+)',
            r'select\s+(\w+)'
        ]
        
        for pattern in entity_patterns:
            matches = re.findall(pattern, prompt_lower)
            entities.extend(matches)
        
        # Determine workflow
        workflow = self._identify_workflow(detected_intent, entities, prompt_lower)
        
        # Calculate confidence
        confidence = min(max_matches * 0.2 + len(entities) * 0.1, 0.95)
        
        return {
            'intent': detected_intent,
            'entities': list(set(entities)),
            'workflow': workflow,
            'confidence': confidence,
            'prompt': prompt
        }
    
    def _identify_workflow(self, intent: str, entities: List[str], prompt: str) -> str:
        """Identify which workflow the test belongs to."""
        # Workflow keywords
        workflows = {
            'user_authentication': ['email', 'password', 'login', 'sign in'],
            'user_registration': ['email', 'password', 'confirm', 'register', 'sign up'],
            'profile_management': ['profile', 'settings', 'account', 'update'],
            'license_application': ['license', 'apply', 'application'],
            'search_filter': ['search', 'filter', 'query', 'find'],
            'data_entry': ['form', 'fill', 'input', 'enter'],
            'file_upload': ['upload', 'file', 'attach', 'document']
        }
        
        for workflow, keywords in workflows.items():
            if any(keyword in prompt for keyword in keywords):
                return workflow
        
        return 'general_interaction'
    
    def suggest_scenarios(self, recorded_actions: List[Dict], current_page: str = '') -> List[Dict[str, Any]]:
        """
        Suggest additional test scenarios based on recorded actions.
        
        Args:
            recorded_actions: List of recorded user actions
            current_page: Current page context
            
        Returns:
            List of suggested test scenarios
        """
        suggestions = []
        
        # Analyze recorded pattern
        action_types = [a.get('action_type', '') for a in recorded_actions]
        
        # Suggest negative test scenarios
        if 'input' in action_types:
            suggestions.append({
                'type': 'negative',
                'scenario': 'Test with invalid input',
                'description': 'Verify error messages for invalid/empty inputs',
                'priority': 'high',
                'steps': self._generate_negative_input_test(recorded_actions)
            })
        
        if 'click' in action_types and 'submit' in str(recorded_actions).lower():
            suggestions.append({
                'type': 'negative',
                'scenario': 'Test form submission without required fields',
                'description': 'Verify validation messages appear',
                'priority': 'high',
                'steps': ['Leave required fields empty', 'Click submit', 'Verify error messages']
            })
        
        # Suggest boundary test scenarios
        if 'input' in action_types:
            suggestions.append({
                'type': 'boundary',
                'scenario': 'Test input length limits',
                'description': 'Test minimum, maximum, and over-limit inputs',
                'priority': 'medium',
                'steps': ['Enter 1 character', 'Enter maximum characters', 'Enter over limit']
            })
        
        # Suggest workflow variations
        workflow = self._detect_workflow_from_actions(recorded_actions)
        if workflow in self.workflow_patterns:
            similar_workflows = self._find_similar_workflows(workflow)
            for similar in similar_workflows[:3]:
                suggestions.append({
                    'type': 'variation',
                    'scenario': f'Test related workflow: {similar}',
                    'description': self.workflow_patterns[similar]['description'],
                    'priority': 'low',
                    'steps': [s.get('prompt', '') for s in self.workflow_patterns[similar]['steps']]
                })
        
        # Suggest edge cases
        suggestions.extend(self._suggest_edge_cases(recorded_actions))
        
        # Suggest cross-browser/device tests
        suggestions.append({
            'type': 'compatibility',
            'scenario': 'Cross-browser testing',
            'description': 'Test on Chrome, Firefox, Edge',
            'priority': 'medium',
            'steps': ['Run same test on different browsers']
        })
        
        return suggestions
    
    def _generate_negative_input_test(self, recorded_actions: List[Dict]) -> List[str]:
        """Generate negative test steps based on recorded inputs."""
        steps = []
        for action in recorded_actions:
            if action.get('action_type') == 'input':
                field = action.get('element', {}).get('name', 'field')
                steps.append(f"Enter invalid data in {field}")
                steps.append(f"Enter special characters in {field}")
                steps.append(f"Leave {field} empty")
        steps.append("Attempt to submit and verify error messages")
        return steps
    
    def _detect_workflow_from_actions(self, actions: List[Dict]) -> str:
        """Detect workflow pattern from action sequence."""
        action_seq = tuple(a.get('action_type', '') for a in actions)
        
        # Find matching workflow
        if action_seq in self.action_sequences:
            workflows = self.action_sequences[action_seq]
            if workflows:
                return workflows[0]
        
        return ''
    
    def _find_similar_workflows(self, workflow: str, limit: int = 5) -> List[str]:
        """Find similar workflows based on page and action patterns."""
        if workflow not in self.workflow_patterns:
            return []
        
        current_page = self.workflow_patterns[workflow]['page']
        similar = []
        
        # Find workflows on same page
        for wf_key, wf_data in self.workflow_patterns.items():
            if wf_data['page'] == current_page and wf_key != workflow:
                similar.append(wf_key)
                if len(similar) >= limit:
                    break
        
        return similar
    
    def _suggest_edge_cases(self, recorded_actions: List[Dict]) -> List[Dict[str, Any]]:
        """Suggest edge case test scenarios."""
        edge_cases = []
        
        # Session timeout test
        edge_cases.append({
            'type': 'edge_case',
            'scenario': 'Test session timeout',
            'description': 'Verify behavior after session expires',
            'priority': 'low',
            'steps': ['Start workflow', 'Wait for session timeout', 'Try to continue']
        })
        
        # Concurrent user test
        if any('submit' in str(a).lower() for a in recorded_actions):
            edge_cases.append({
                'type': 'edge_case',
                'scenario': 'Test concurrent submissions',
                'description': 'Verify handling of simultaneous form submissions',
                'priority': 'medium',
                'steps': ['Open multiple tabs', 'Submit same form', 'Verify data integrity']
            })
        
        # Network interruption
        edge_cases.append({
            'type': 'edge_case',
            'scenario': 'Test network interruption',
            'description': 'Verify error handling when network fails',
            'priority': 'low',
            'steps': ['Start action', 'Disable network', 'Verify error message']
        })
        
        return edge_cases
    
    def generate_test_report(self, intent_analysis: Dict, suggestions: List[Dict]) -> str:
        """Generate human-readable test scenario report."""
        report = f"""
╔══════════════════════════════════════════════════════════════════════╗
║                    SEMANTIC TEST ANALYSIS REPORT                     ║
╚══════════════════════════════════════════════════════════════════════╝

📋 TEST INTENT ANALYSIS
───────────────────────────────────────────────────────────────────────
Intent:      {intent_analysis['intent'].upper()}
Workflow:    {intent_analysis['workflow'].replace('_', ' ').title()}
Confidence:  {intent_analysis['confidence']:.0%}
Entities:    {', '.join(intent_analysis['entities']) if intent_analysis['entities'] else 'None detected'}

🎯 SUGGESTED TEST SCENARIOS ({len(suggestions)} scenarios)
───────────────────────────────────────────────────────────────────────
"""
        
        # Group by priority
        by_priority = {'high': [], 'medium': [], 'low': []}
        for suggestion in suggestions:
            by_priority[suggestion['priority']].append(suggestion)
        
        for priority in ['high', 'medium', 'low']:
            scenarios = by_priority[priority]
            if scenarios:
                report += f"\n🔴 {priority.upper()} PRIORITY ({len(scenarios)} scenarios)\n"
                for i, scenario in enumerate(scenarios, 1):
                    report += f"\n  {i}. {scenario['scenario']}\n"
                    report += f"     Type: {scenario['type'].upper()}\n"
                    report += f"     {scenario['description']}\n"
                    if scenario.get('steps'):
                        report += f"     Steps:\n"
                        for step in scenario['steps'][:3]:  # Show first 3 steps
                            report += f"       • {step}\n"
        
        report += "\n" + "═" * 72 + "\n"
        return report


# Global instance
_semantic_analyzer = None

def get_analyzer() -> SemanticAnalyzer:
    """Get global semantic analyzer instance."""
    global _semantic_analyzer
    if _semantic_analyzer is None:
        _semantic_analyzer = SemanticAnalyzer()
    return _semantic_analyzer
