"""
Test Case Expander - Generate multiple test variants from a single test case.

Moved from frontend (semantic-analysis.js) to proper backend location.
This module generates negative, boundary, edge case, variation, and compatibility tests.
"""
import logging
import json
from typing import Dict, List, Any, Optional
from recorder.recorder_handler import get_test_case


class TestCaseExpander:
    """Generates multiple test variants from a single recorded test case."""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        
    def expand_test_case(self, test_case_id: str, generation_types: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Generate multiple test variants from a single test case.
        
        Args:
            test_case_id: ID of the source test case to expand
            generation_types: Optional list of test types to generate
                            ['negative', 'boundary', 'edge_case', 'variation', 'compatibility']
                            If None, generates all types
            
        Returns:
            Dict containing:
                - success: bool
                - source_test: Source test case info
                - generated_tests: List of complete test variant dicts
                - total_generated: int
                - error: Optional error message
        """
        try:
            # Load the source test case
            test_case = get_test_case(test_case_id)
            if not test_case:
                return {
                    'success': False,
                    'error': f'Test case {test_case_id} not found'
                }
            
            self.logger.info(f"[EXPANDER] Expanding test case: {test_case_id}")
            
            # Determine which test types to generate
            if generation_types is None:
                generation_types = ['negative', 'boundary', 'edge_case', 'variation', 'compatibility']
            
            # Generate variants for requested test types
            generated_tests = []
            
            for test_type in generation_types:
                if test_type == 'negative':
                    generated_tests.append(self._generate_negative_test(test_case))
                elif test_type == 'boundary':
                    generated_tests.append(self._generate_boundary_test(test_case))
                elif test_type == 'edge_case':
                    generated_tests.append(self._generate_edge_case_test(test_case))
                elif test_type == 'variation':
                    generated_tests.append(self._generate_variation_test(test_case))
                elif test_type == 'compatibility':
                    generated_tests.append(self._generate_compatibility_test(test_case))
                else:
                    self.logger.warning(f"[EXPANDER] Unknown test type: {test_type}")
            
            self.logger.info(f"[EXPANDER] Generated {len(generated_tests)} test variants")
            
            return {
                'success': True,
                'source_test': {
                    'id': test_case.get('id'),
                    'name': test_case.get('name', 'Unknown'),
                    'actions_count': len(test_case.get('actions', test_case.get('prompts', [])))
                },
                'generated_tests': generated_tests,
                'total_generated': len(generated_tests)
            }
            
        except Exception as e:
            self.logger.error(f"[EXPANDER] Error expanding test case: {e}", exc_info=True)
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_action_description(self, test_case: Dict) -> str:
        """Extract action description from test case."""
        actions = test_case.get('actions', test_case.get('prompts', test_case.get('steps', [])))
        
        if not isinstance(actions, list) or len(actions) == 0:
            return 'test actions'
        
        if actions[0].get('action'):
            # Recorder format: {action, selector, value}
            return ', '.join(a.get('action', 'action') for a in actions)
        elif actions[0].get('prompt'):
            # Builder format: {prompt, type}
            return ', '.join(a.get('type', 'action') for a in actions)
        else:
            return f'{len(actions)} steps'
    
    def _generate_negative_test(self, test_case: Dict) -> Dict[str, Any]:
        """Generate a negative test variant."""
        action_desc = self._get_action_description(test_case)
        
        description = f"""Negative Test - Test failure scenarios

ORIGINAL TEST ACTIONS: {action_desc}

This is a NEGATIVE TEST - Test failure scenarios:
REQUIRED CHANGES:
- Replace all valid inputs with INVALID data:
  * Email fields: "not-an-email", "user@", "@domain.com", "plaintext"
  * Text fields: "", "   " (spaces only), null
  * Numbers: -1, "abc", special characters
  * Required fields: Leave empty or missing
- Change all success assertions to failure assertions:
  * Instead of assert success_message: assert error_message
  * Verify error messages appear: assert "Invalid" in page or "Required"
  * Check validation warnings are displayed
- Expected outcome: Operation should FAIL with proper error messages

REMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!"""
        
        return {
            'type': 'negative',
            'priority': 'high',
            'title': 'Test with invalid inputs',
            'description': description,
            'steps': [
                'Use invalid email format: "not-an-email"',
                'Leave required fields empty',
                'Enter negative numbers where positive expected',
                'Verify error messages are displayed',
                'Confirm operation fails gracefully'
            ],
            'expected_result': 'System rejects invalid input with clear error messages',
            'test_case_id': test_case.get('id'),
            'test_name': test_case.get('name', 'Unknown')
        }
    
    def _generate_boundary_test(self, test_case: Dict) -> Dict[str, Any]:
        """Generate a boundary test variant."""
        action_desc = self._get_action_description(test_case)
        
        description = f"""Boundary Test - Test at limits

ORIGINAL TEST ACTIONS: {action_desc}

This is a BOUNDARY TEST - Test at limits:
REQUIRED CHANGES:
- Test MINIMUM values:
  * Single character: "a"
  * Zero: 0
  * Empty array: []
- Test MAXIMUM values:
  * Very long string: "a" * 1000 or "a" * 255
  * Max integer: 2147483647
  * Large files: Upload max size
- Test exact boundaries:
  * If max is 100, test with 99, 100, 101
  * Test min-1, min, min+1
- Verify proper handling at limits

REMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!"""
        
        return {
            'type': 'boundary',
            'priority': 'high',
            'title': 'Test with boundary values',
            'description': description,
            'steps': [
                'Test with single character input: "a"',
                'Test with very long input: 1000 characters',
                'Test with zero/empty values',
                'Test at exact maximum limits',
                'Verify system handles boundaries correctly'
            ],
            'expected_result': 'System handles minimum and maximum values correctly',
            'test_case_id': test_case.get('id'),
            'test_name': test_case.get('name', 'Unknown')
        }
    
    def _generate_edge_case_test(self, test_case: Dict) -> Dict[str, Any]:
        """Generate an edge case test variant."""
        action_desc = self._get_action_description(test_case)
        
        description = f"""Edge Case Test - Test unusual inputs

ORIGINAL TEST ACTIONS: {action_desc}

This is an EDGE CASE TEST - Test unusual inputs:
REQUIRED CHANGES:
- Use special characters:
  * !@#$%^&*()_+-={{}}[]|\\:";'<>?,./
  * Unicode: 你好, مرحبا, Здравствуй
  * Emojis: 😀🎉✨
- Test security vulnerabilities:
  * SQL injection: ' OR '1'='1' --, admin'--
  * XSS: <script>alert('xss')</script>, <img src=x onerror=alert(1)>
  * Path traversal: ../../../etc/passwd
- Test whitespace variations:
  * Leading/trailing spaces: "  text  "
  * Multiple spaces: "text    text"
  * Tabs and newlines
- Verify input sanitization and security

REMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!"""
        
        return {
            'type': 'edge_case',
            'priority': 'high',
            'title': 'Test with special characters and unusual inputs',
            'description': description,
            'steps': [
                'Enter special characters: !@#$%^&*()',
                'Test with Unicode characters: 你好',
                'Try SQL injection patterns',
                'Test XSS attack patterns',
                'Verify input is properly sanitized'
            ],
            'expected_result': 'System sanitizes and handles special characters safely',
            'test_case_id': test_case.get('id'),
            'test_name': test_case.get('name', 'Unknown')
        }
    
    def _generate_variation_test(self, test_case: Dict) -> Dict[str, Any]:
        """Generate a test variation."""
        action_desc = self._get_action_description(test_case)
        
        description = f"""Test Variation - Same goal, different approach

ORIGINAL TEST ACTIONS: {action_desc}

This is a TEST VARIATION - Same goal, different approach:
REQUIRED CHANGES:
- Use DIFFERENT valid data:
  * Different email: user2@example.com instead of user1@example.com
  * Different names: Jane Doe instead of John Doe
  * Alternative valid formats
- Test alternative workflows:
  * Use keyboard shortcuts instead of mouse clicks
  * Navigate via direct URL instead of clicking links
  * Use different but valid paths to same goal
- Verify same end result with different data/approach

REMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!"""
        
        return {
            'type': 'variation',
            'priority': 'medium',
            'title': 'Test with alternative data and workflow',
            'description': description,
            'steps': [
                'Use different valid email: user2@example.com',
                'Use different name: Jane Doe',
                'Navigate using keyboard shortcuts',
                'Try alternative valid workflow',
                'Verify same successful outcome'
            ],
            'expected_result': 'Alternative approach achieves same successful result',
            'test_case_id': test_case.get('id'),
            'test_name': test_case.get('name', 'Unknown')
        }
    
    def _generate_compatibility_test(self, test_case: Dict) -> Dict[str, Any]:
        """Generate a compatibility test variant."""
        action_desc = self._get_action_description(test_case)
        
        description = f"""Compatibility Test - Test across platforms

ORIGINAL TEST ACTIONS: {action_desc}

This is a COMPATIBILITY TEST - Test across platforms:
REQUIRED CHANGES:
- Add browser-specific checks:
  * Test in Chrome, Firefox, Safari, Edge
  * Verify responsive design (mobile, tablet, desktop)
- Test different screen sizes:
  * Mobile: 375x667
  * Tablet: 768x1024
  * Desktop: 1920x1080
- Verify cross-platform behavior consistency

REMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!"""
        
        return {
            'type': 'compatibility',
            'priority': 'medium',
            'title': 'Test across different browsers and screen sizes',
            'description': description,
            'steps': [
                'Test in Chrome browser',
                'Test in Firefox browser',
                'Test on mobile viewport: 375x667',
                'Test on tablet viewport: 768x1024',
                'Verify consistent behavior across platforms'
            ],
            'expected_result': 'Test works consistently across all browsers and screen sizes',
            'test_case_id': test_case.get('id'),
            'test_name': test_case.get('name', 'Unknown')
        }


# Singleton instance
_expander_instance = None


def get_test_case_expander() -> TestCaseExpander:
    """Get or create the singleton TestCaseExpander instance."""
    global _expander_instance
    if _expander_instance is None:
        _expander_instance = TestCaseExpander()
        logging.info("[EXPANDER] TestCaseExpander initialized")
    return _expander_instance
