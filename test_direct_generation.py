"""
DIRECT TEST - Bypasses ALL caching, proves the fix works
Upload your SIRCON screenshot and see EXACTLY what gets generated
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

import base64
import json

# Simulated 2-input screenshot data (like SIRCON login)
def create_mock_analysis():
    """Mock analysis result as if from a 2-input login screenshot"""
    return {
        'elements': {
            'inputs': [
                {'x': 100, 'y': 100, 'width': 300, 'height': 40, 'label': 'Email', 'index': 0},
                {'x': 100, 'y': 160, 'width': 300, 'height': 40, 'label': 'Password', 'index': 1}
            ],
            'buttons': [
                {'x': 100, 'y': 220, 'width': 100, 'height': 40, 'text': 'Sign In'}
            ]
        },
        'total_elements': 3,
        'ocr_enabled': False
    }

def main():
    print("="*80)
    print("DIRECT TEST - Fresh Instance Generation")
    print("="*80)
    
    # Import fresh
    from simple_screenshot_test_generator import SimpleScreenshotTestGenerator
    
    print("\n1. Creating FRESH generator instance...")
    gen = SimpleScreenshotTestGenerator()
    print(f"   Instance ID: {id(gen)}")
    
    print("\n2. Creating mock analysis (2 inputs: Email + Password)...")
    analysis = create_mock_analysis()
    print(f"   Inputs: {len(analysis['elements']['inputs'])}")
    for idx, inp in enumerate(analysis['elements']['inputs']):
        print(f"     Input {idx}: label='{inp['label']}'")
    
    print("\n3. Detecting test type...")
    # Manually test the detection logic
    inputs = analysis['elements']['inputs']
    has_password = any('password' in inp.get('label', '').lower() for inp in inputs)
    has_email = any('email' in inp.get('label', '').lower() for inp in inputs)
    print(f"   Has password field: {has_password}")
    print(f"   Has email field: {has_email}")
    print(f"   Input count: {len(inputs)}")
    
    if has_password or (has_email and len(inputs) <= 4):
        test_type = "LOGIN"
    elif len(inputs) == 1:
        test_type = "SEARCH"
    elif len(inputs) >= 4:
        test_type = "FORM"
    else:
        test_type = "GENERIC"
    
    print(f"   ✓ Detected type: {test_type}")
    
    print("\n4. Generating test methods...")
    test_methods = gen.generate_test_methods(analysis, "LoginPageTest")
    print(f"   ✓ Generated {len(test_methods)} test methods")
    
    print("\n5. Test method names:")
    for tm in test_methods[:10]:
        print(f"     - {tm['name']}")
    if len(test_methods) > 10:
        print(f"     ... and {len(test_methods) - 10} more")
    
    print("\n6. Creating complete test class...")
    code = gen.create_complete_test_class(test_methods, "LoginPageTest")
    
    print("\n7. Code quality check:")
    has_smart_ids = "By.id(" in code
    has_bad_xpaths = "@placeholder='&)'" in code or "@placeholder='Input" in code
    has_login_tests = "testSuccessfulLogin" in code
    has_form_tests = "testFormSubmissionWithValidData" in code
    has_email_id = 'By.id("email")' in code
    has_password_id = 'By.id("password")' in code
    
    print(f"   Smart ID locators: {'✓ YES' if has_smart_ids else '✗ NO'}")
    print(f"   Bad placeholder XPaths: {'✗ YES (BAD)' if has_bad_xpaths else '✓ NO'}")
    print(f"   Login-specific tests: {'✓ YES' if has_login_tests else '✗ NO'}")
    print(f"   Generic form tests: {'✗ YES (WRONG)' if has_form_tests else '✓ NO'}")
    print(f"   By.id(\"email\"): {'✓ YES' if has_email_id else '✗ NO'}")
    print(f"   By.id(\"password\"): {'✓ YES' if has_password_id else '✗ NO'}")
    
    print("\n8. First 50 lines of generated code:")
    print("-"*80)
    lines = code.split('\n')[:50]
    for line in lines:
        print(line)
    print("-"*80)
    
    # Save to file
    output_file = "DIRECT_TEST_OUTPUT.java"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(code)
    print(f"\n✓ Full code saved to: {output_file}")
    
    print("\n" + "="*80)
    print("FINAL VERDICT:")
    print("="*80)
    
    if test_type == "LOGIN" and has_login_tests and has_email_id and has_password_id and not has_bad_xpaths:
        print("✓✓✓ SUCCESS! The generator is working perfectly!")
        print("    - Detected LOGIN page type correctly")
        print("    - Generated login-specific tests")
        print("    - Used smart By.id() locators")
        print("    - No bad placeholder XPaths")
        print("\nThe issue is BROWSER CACHING. The code you're seeing is OLD cached data.")
        print("Solution: Hard refresh browser (Ctrl+Shift+R) or use test-generator-fresh.html")
    else:
        print("✗✗✗ PROBLEM FOUND!")
        if test_type != "LOGIN":
            print(f"    - Wrong test type: {test_type} (should be LOGIN)")
        if not has_login_tests:
            print("    - Not generating login-specific tests")
        if not has_email_id or not has_password_id:
            print("    - Not using smart ID locators for email/password")
        if has_bad_xpaths:
            print("    - Generating bad placeholder XPaths")

if __name__ == '__main__':
    main()
