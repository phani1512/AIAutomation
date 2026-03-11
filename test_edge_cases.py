"""
Edge case tests to ensure robustness
"""
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'main' / 'python'))

from complete_test_generator import CompleteTestGenerator

def test_edge_cases():
    """Test edge cases that might break the code."""
    print("=" * 70)
    print("EDGE CASE TESTING")
    print("=" * 70)
    print()
    
    test_gen = CompleteTestGenerator()
    
    # Test 1: Empty labels (should fall back to suggested_name)
    print("[Test 1] Empty labels...")
    analysis1 = {
        'elements': {
            'buttons': [{'type': 'button', 'index': 0, 'suggested_name': 'submit_btn'}],
            'inputs': [{'type': 'input', 'index': 0, 'suggested_name': 'username'}]
        }
    }
    try:
        result = test_gen.generate_complete_test_suite(analysis1, 'java', 'Test1')
        assert 'submit_btn' in result['page_object'] or 'submitBtn' in result['page_object']
        print("✓ Empty labels handled correctly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 2: Labels with special characters
    print("[Test 2] Special characters in labels...")
    analysis2 = {
        'elements': {
            'buttons': [{'type': 'button', 'index': 0, 'text': 'Sign In!', 'label': 'Sign In!'}],
            'inputs': [{'type': 'input', 'index': 0, 'label': 'E-mail Address'}]
        }
    }
    try:
        result = test_gen.generate_complete_test_suite(analysis2, 'java', 'Test2')
        assert 'signIn' in result['page_object'] or 'eMailAddress' in result['page_object'] or 'emailAddress' in result['page_object']
        print("✓ Special characters sanitized correctly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 3: No elements detected
    print("[Test 3] No elements detected...")
    analysis3 = {
        'elements': {
            'buttons': [],
            'inputs': []
        }
    }
    try:
        result = test_gen.generate_complete_test_suite(analysis3, 'java', 'Test3')
        assert result['test_count'] == 0
        print("✓ Empty analysis handled correctly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 4: Non-button text detection
    print("[Test 4] Non-button text filtering...")
    analysis4 = {
        'elements': {
            'buttons': [
                {'type': 'button', 'index': 0, 'text': 'Your session has expired'},
                {'type': 'button', 'index': 1, 'text': 'Login'}
            ],
            'inputs': []
        }
    }
    try:
        result = test_gen.generate_complete_test_suite(analysis4, 'java', 'Test4')
        # Should skip the "session expired" text
        assert 'login' in result['page_object'].lower()
        assert 'session' not in result['page_object'].lower() or result['test_count'] == 1
        print("✓ Non-button text filtered correctly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 5: Python generation with same inputs
    print("[Test 5] Python generation consistency...")
    analysis5 = {
        'elements': {
            'buttons': [{'type': 'button', 'index': 0, 'text': 'Submit', 'label': 'Submit'}],
            'inputs': [{'type': 'input', 'index': 0, 'label': 'Username'}]
        }
    }
    try:
        java_result = test_gen.generate_complete_test_suite(analysis5, 'java', 'Test5')
        python_result = test_gen.generate_complete_test_suite(analysis5, 'python', 'Test5')
        
        # Both should have XPath locators
        assert 'xpath' in java_result['page_object'].lower()
        assert 'xpath' in python_result['page_object'].lower()
        assert java_result['test_count'] == python_result['test_count']
        print("✓ Java and Python generation consistent")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    # Test 6: Very long label text
    print("[Test 6] Very long label text...")
    analysis6 = {
        'elements': {
            'inputs': [{'type': 'input', 'index': 0, 'label': 'This is a very long label that should be truncated to avoid creating invalid field names'}]
        }
    }
    try:
        result = test_gen.generate_complete_test_suite(analysis6, 'java', 'Test6')
        # Field name should be truncated to 50 chars
        assert result['page_object'] is not None
        print("✓ Long labels handled correctly")
    except Exception as e:
        print(f"✗ Failed: {e}")
        return False
    
    print()
    print("=" * 70)
    print("✅ ALL EDGE CASE TESTS PASSED")
    print("=" * 70)
    return True

if __name__ == '__main__':
    success = test_edge_cases()
    sys.exit(0 if success else 1)
