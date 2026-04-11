"""
Context Analyzer - Dynamically analyze test context for intelligent suggestions.

Analyzes:
- Workflow type (authentication, registration, e-commerce, etc.)
- Business domain (insurance, finance, healthcare, etc.)
- Page type
- Field information
"""

import re
import logging
from typing import Dict, List, Any
from .field_analyzer import FieldAnalyzer


class ContextAnalyzer:
    """Analyzes test context to understand workflow and business domain."""
    
    @staticmethod
    def analyze_test_context(test_name: str, test_url: str, actions: List[Dict]) -> Dict[str, Any]:
        """Analyze test to understand context for intelligent data generation using AI.
        
        Dynamically extracts field information from the test case instead of hardcoding.
        
        Args:
            test_name: Test name/title
            test_url: Test URL
            actions: List of test actions
            
        Returns:
            Dict containing workflow, domain, fields, etc.
        """
        context = {
            'workflow': 'unknown',
            'page_type': 'unknown',
            'domain': 'unknown',
            'field_count': 0,
            'fields': []  # Store actual field information from test
        }
        
        # Analyze test name and URL to infer domain and workflow
        test_name_lower = test_name.lower()
        test_url_lower = test_url.lower()
        
        # Extract domain from URL (dynamic, not hardcoded)
        if test_url_lower:
            # Parse domain from URL
            domain_match = re.search(r'https?://(?:www\.)?([^/]+)', test_url_lower)
            if domain_match:
                domain = domain_match.group(1)
                context['domain'] = domain
                
                # Infer business domain from URL
                if 'sircon' in domain or 'insurance' in domain:
                    context['business_domain'] = 'insurance_licensing'
                elif 'bank' in domain or 'finance' in domain:
                    context['business_domain'] = 'financial_services'
                elif 'health' in domain or 'medical' in domain:
                    context['business_domain'] = 'healthcare'
                else:
                    context['business_domain'] = 'general'
        
        # Analyze workflow dynamically from test name, URL path, and actions
        workflow_indicators = ContextAnalyzer.extract_workflow_from_test(test_name, test_url, actions)
        context['workflow'] = workflow_indicators.get('workflow', 'unknown')
        context['page_type'] = workflow_indicators.get('page_type', 'unknown')
        
        # Extract actual field information from actions (NO HARDCODING)
        for action in actions:
            action_type = action.get('action_type', '')
            if action_type in ['input', 'click_and_input', 'select']:
                field_info = FieldAnalyzer.extract_field_info_from_action(action)
                if field_info:
                    context['fields'].append(field_info)
        
        context['field_count'] = len(context['fields'])
        
        return context
    
    @staticmethod
    def extract_workflow_from_test(test_name: str, test_url: str, actions: List[Dict]) -> Dict[str, str]:
        """Dynamically extract workflow information from test characteristics.
        
        Args:
            test_name: Test name/title
            test_url: Test URL
            actions: List of test actions
            
        Returns:
            Dict with workflow and page_type
        """
        # Combine all text for analysis
        all_text = f"{test_name} {test_url}".lower()
        
        # Add action text
        for action in actions:
            action_text = action.get('action', action.get('prompt', ''))
            all_text += f" {action_text.lower()}"
        
        # Pattern-based workflow detection (extensible, not exhaustive hardcoding)
        workflows = {
            'authentication': ['login', 'signin', 'sign in', 'log in', 'authenticate', 'credential'],
            'registration': ['register', 'signup', 'sign up', 'create account', 'new user', 'join'],
            'profile_management': ['profile', 'account', 'settings', 'preferences', 'update profile'],
            'application_form': ['apply', 'application', 'form', 'submit', 'request'],
            'search': ['search', 'find', 'filter', 'query', 'lookup'],
            'transaction': ['payment', 'checkout', 'purchase', 'order', 'cart'],
            'data_entry': ['enter', 'fill', 'input', 'add', 'create']
        }
        
        detected_workflow = 'unknown'
        detected_page_type = 'unknown'
        
        for workflow_name, keywords in workflows.items():
            if any(keyword in all_text for keyword in keywords):
                detected_workflow = workflow_name
                detected_page_type = f"{workflow_name}_page"
                break
        
        return {
            'workflow': detected_workflow,
            'page_type': detected_page_type
        }
