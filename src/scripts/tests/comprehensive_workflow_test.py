"""
Comprehensive Workflow Test - Test entire code generation pipeline
Tests all critical paths that were refactored
"""
import sys
import os

# Add src/main/python to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from core.inference_improved import ImprovedSeleniumGenerator
from test_management.test_session_manager import TestSession, TestSessionManager
from test_management.test_case_builder import TestCaseBuilder

def test_placeholder_preservation():
    """Test that preserve_data_placeholder actually works"""
    print("=" * 70)
    print("TEST 1: Placeholder Preservation")
    print("=" * 70)
    
    gen = ImprovedSeleniumGenerator(silent=True)
    
    # Test with preserve_data_placeholder=True
    result1 = gen.infer('enter username in username field', 
                       language='python', 
                       preserve_data_placeholder=True)
    
    code1 = result1.get('code', '')
    print(f"\n📋 Prompt: 'enter username in username field'")
    print(f"🔒 preserve_data_placeholder=True")
    print(f"✅ Generated code:\n{code1}\n")
    
    if '{VALUE}' in code1:
        print("✅ PASS: Placeholder preserved")
    else:
        print("❌ FAIL: Placeholder not preserved!")
        print(f"   Expected: {{VALUE}} anywhere in code")
        print(f"   Got: {code1}")
        return False
    
    # Test with preserve_data_placeholder=False
    result2 = gen.infer('enter john123 in username field',
                       language='python',
                       preserve_data_placeholder=False)
    
    code2 = result2.get('code', '')
    print(f"\n📋 Prompt: 'enter john123 in username field'")
    print(f"🔓 preserve_data_placeholder=False")
    print(f"✅ Generated code:\n{code2}\n")
    
    if 'john123' in code2 and '{VALUE}' not in code2:
        print("✅ PASS: Value extracted and used")
    else:
        print("❌ FAIL: Value not extracted properly!")
        return False
    
    return True


def test_quote_handling():
    """Test that all languages generate proper quotes"""
    print("\n" + "=" * 70)
    print("TEST 2: Quote Handling Across Languages")
    print("=" * 70)
    
    gen = ImprovedSeleniumGenerator(silent=True)
    
    tests = [
        ('enter test123 in username', 'python', 'send_keys', '"test123"'),
        ('enter test456 in email', 'java', 'sendKeys', '"test456"'),
        ('type hello in message',  'javascript', 'fill', '"hello"'),
        ('input data in field', 'csharp', 'SendKeys', '"data"'),
    ]
    
    all_passed = True
    for prompt, lang, method, expected in tests:
        result = gen.infer(prompt, language=lang, preserve_data_placeholder=False)
        code = result.get('code', '')
        
        print(f"\n📋 {lang.upper()}: '{prompt}'")
        print(f"   Looking for: {method}({expected})")
        print(f"   Generated:\n{code[:200]}...\n")
        
        if expected in code or '{VALUE}' in code:
            print(f"   ✅ PASS")
        else:
            print(f"   ❌ FAIL: Missing proper quotes")
            all_passed = False
    
    return all_passed


def test_test_case_builder():
    """Test that test_case_builder properly replaces placeholders"""
    print("\n" + "=" * 70)
    print("TEST 3: Test Case Builder Placeholder Replacement")
    print("=" * 70)
    
    # Create a test session
    manager = TestSessionManager()
    session = manager.create_session("Test Builder Test", "Testing placeholder replacement")
    
    # Add some steps with placeholders
    session.add_prompt(
        prompt='enter username in username field',
        value='john_doe',
        generated_code='element.send_keys("{VALUE}")'
    )
    
    session.add_prompt(
        prompt='enter password in password field',
        value='secret123',
        generated_code='element.send_keys("{VALUE}")'
    )
    
    session.add_prompt(
        prompt='click login button',
        value=None,
        generated_code='element.click()'
    )
    
    print(f"\n📋 Created session with {len(session.prompts)} steps")
    for i, p in enumerate(session.prompts, 1):
        print(f"   {i}. {p['prompt']} | value={p.get('value')} | code={p.get('generated_code', '')[:50]}")
    
    # Build the test case
    builder = TestCaseBuilder()
    test_code = builder.build_test_case(session, language='python')
    
    print(f"\n✅ Generated test code:\n")
    print(test_code)
    print("\n")
    
    # Check for proper replacement
    checks = [
        ('john_doe', 'Username value'),
        ('secret123', 'Password value'),
        ('send_keys', 'Send keys method'),
    ]
    
    all_passed = True
    for check_str, description in checks:
        if check_str in test_code:
            print(f"   ✅ {description}: Found '{check_str}'")
        else:
            print(f"   ❌ {description}: NOT FOUND '{check_str}'")
            all_passed = False
    
    # Check that placeholders are gone
    if '{VALUE}' in test_code:
        print(f"   ❌ FAIL: {{VALUE}} placeholder still present!")
        all_passed = False
    else:
        print(f"   ✅ All placeholders replaced")
    
    return all_passed


def test_fallback_strategy():
    """Test fallback strategy quote handling"""
    print("\n" + "=" * 70)
    print("TEST 4: Fallback Strategy Quote Handling")
    print("=" * 70)
    
    from fallback_strategy import FallbackStrategyGenerator
    
    gen = FallbackStrategyGenerator()
    
    selectors = [
        "#username",
        "[name='username']",
        "input[type='text']"
    ]
    
    languages = ['python', 'java', 'javascript', 'csharp']
    all_passed = True
    
    for lang in languages:
        code = gen.generate_with_fallbacks(
            selectors=selectors,
            action='enter',
            element_type='input',
            prompt='enter testvalue in username',
            language=lang,
            value_extractor_func=lambda p: 'testvalue'
        )
        
        print(f"\n📋 {lang.upper()}:")
        print(code[:300])
        
        # Check for proper quotes
        if lang == 'python':
            check = 'send_keys("testvalue")'
        elif lang == 'java':
            check = 'sendKeys("testvalue")'
        elif lang == 'javascript':
            check = 'sendKeys("testvalue")'
        elif lang == 'csharp':
            check = 'SendKeys("testvalue")'
        
        if check in code or '"testvalue"' in code:
            print(f"   ✅ PASS: Proper quotes")
        else:
            print(f"   ❌ FAIL: Missing quotes or wrong format")
            print(f"      Looking for: {check}")
            all_passed = False
    
    return all_passed


def test_comprehensive_mode():
    """Test comprehensive vs simple mode"""
    print("\n" + "=" * 70)
    print("TEST 5: Comprehensive vs Simple Mode")
    print("=" * 70)
    
    gen = ImprovedSeleniumGenerator(silent=True)
    
    prompt = 'click submit button'
    
    # Simple mode
    result_simple = gen.infer(prompt, language='python', comprehensive_mode=False)
    code_simple = result_simple.get('code', '')
    
    print(f"\n📋 Simple Mode:")
    print(code_simple)
    
    # Comprehensive mode
    result_comp = gen.infer(prompt, language='python', comprehensive_mode=True)
    code_comp = result_comp.get('code', '')
    
    print(f"\n📋 Comprehensive Mode:")
    print(code_comp)
    
    # Comprehensive should have waits
    if 'WebDriverWait' in code_comp or 'wait' in code_comp.lower():
        print(f"\n✅ PASS: Comprehensive mode includes waits")
        return True
    else:
        print(f"\n❌ FAIL: Comprehensive mode missing waits")
        return False


def run_all_tests():
    """Run all workflow tests"""
    print("\n")
    print("=" * 70)
    print("COMPREHENSIVE WORKFLOW TEST SUITE")
    print("Testing all critical paths after refactoring")
    print("=" * 70)
    
    tests = [
        ("Placeholder Preservation", test_placeholder_preservation),
        ("Quote Handling", test_quote_handling),
        ("Test Case Builder", test_test_case_builder),
        ("Fallback Strategy", test_fallback_strategy),
        ("Comprehensive Mode", test_comprehensive_mode),
    ]
    
    results = []
    for name, test_func in tests:
        try:
            passed = test_func()
            results.append((name, passed))
        except Exception as e:
            print(f"\n❌ TEST FAILED WITH EXCEPTION: {name}")
            print(f"   Error: {str(e)}")
            import traceback
            traceback.print_exc()
            results.append((name, False))
    
    # Summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed_count = sum(1 for _, passed in results if passed)
    total_count = len(results)
    
    for name, passed in results:
        status = "✅ PASS" if passed else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\n{'=' * 70}")
    print(f"Results: {passed_count}/{total_count} tests passed")
    
    if passed_count == total_count:
        print("🎉 ALL TESTS PASSED - System is working correctly!")
    else:
        print(f"⚠️  {total_count - passed_count} test(s) failed - Issues found!")
    
    print("=" * 70)
    
    return passed_count == total_count


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
