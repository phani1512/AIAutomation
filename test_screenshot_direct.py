"""
Direct test of screenshot analysis - bypass all caching
This will prove whether the detection logic works correctly
"""
import sys
sys.path.insert(0, 'src/main/python')

import base64
from visual_element_detector import VisualElementDetector
from multimodal_generator import MultiModalCodeGenerator
from simple_screenshot_test_generator import SimpleScreenshotTestGenerator

def test_login_screenshot():
    """Test with a login screenshot"""
    
    # Read the screenshot file you're testing with
    screenshot_path = input("Enter path to your SIRCON login screenshot: ")
    
    with open(screenshot_path, 'rb') as f:
        screenshot_bytes = f.read()
        screenshot_b64 = base64.b64encode(screenshot_bytes).decode('utf-8')
    
    print("\n" + "="*80)
    print("CREATING FRESH INSTANCES (NO CACHING)")
    print("="*80)
    
    # Create FRESH instances
    visual = VisualElementDetector()
    modal = MultiModalCodeGenerator(visual)
    simple = SimpleScreenshotTestGenerator()
    
    print(f"\n✓ Fresh instances created:")
    print(f"  Visual: {id(visual)}")
    print(f"  Modal: {id(modal)}")
    print(f"  Simple: {id(simple)}")
    
    print("\n" + "="*80)
    print("STEP 1: ANALYZE SCREENSHOT")
    print("="*80)
    
    analysis = modal.analyze_screenshot(screenshot_b64, "Login page test", use_ocr=True)
    
    print(f"\n✓ Analysis complete:")
    print(f"  Total elements: {analysis['total_elements']}")
    print(f"  Buttons: {len(analysis['elements'].get('buttons', []))}")
    print(f"  Inputs: {len(analysis['elements'].get('inputs', []))}")
    print(f"  OCR enabled: {analysis['ocr_enabled']}")
    
    print(f"\n📋 Input fields detected:")
    for idx, inp in enumerate(analysis['elements'].get('inputs', [])):
        label = inp.get('label', 'NO LABEL')
        placeholder = inp.get('placeholder', 'NO PLACEHOLDER')
        print(f"  Input {idx}: label='{label}', placeholder='{placeholder}'")
    
    print(f"\n📋 Buttons detected:")
    for idx, btn in enumerate(analysis['elements'].get('buttons', [])):
        text = btn.get('text', 'NO TEXT')
        print(f"  Button {idx}: text='{text}'")
    
    print("\n" + "="*80)
    print("STEP 2: DETECT TEST TYPE")
    print("="*80)
    
    # Check what test type would be detected
    inputs = analysis['elements'].get('inputs', [])
    has_password = any('password' in inp.get('label', '').lower() for inp in inputs)
    has_email = any('email' in inp.get('label', '').lower() for inp in inputs)
    input_count = len(inputs)
    
    print(f"\n🔍 Test type detection:")
    print(f"  Input count: {input_count}")
    print(f"  Has password field: {has_password}")
    print(f"  Has email field: {has_email}")
    
    if has_password or (has_email and input_count <= 4):
        detected_type = "LOGIN"
    elif input_count == 1:
        detected_type = "SEARCH"
    elif input_count >= 4:
        detected_type = "FORM"
    else:
        detected_type = "GENERIC"
    
    print(f"  ➜ DETECTED TYPE: {detected_type}")
    
    print("\n" + "="*80)
    print("STEP 3: GENERATE TEST CODE")
    print("="*80)
    
    test_methods = simple.generate_test_methods(analysis, "LoginPageTest")
    
    print(f"\n✓ Generated {len(test_methods)} test methods:")
    for tm in test_methods[:5]:  # Show first 5
        print(f"  - {tm['name']}: {tm['description']}")
    
    if len(test_methods) > 5:
        print(f"  ... and {len(test_methods) - 5} more")
    
    print("\n" + "="*80)
    print("STEP 4: CHECK LOCATORS")
    print("="*80)
    
    test_class = simple.create_complete_test_class(test_methods, "LoginPageTest")
    
    # Check for smart locators vs bad XPaths
    has_smart_ids = "By.id(" in test_class
    has_bad_xpaths = "@placeholder='&)'" in test_class or "@placeholder='Input" in test_class
    has_login_tests = "testSuccessfulLogin" in test_class or "testLoginWith" in test_class
    has_form_tests = "testFormSubmissionWithValidData" in test_class
    
    print(f"\n📊 Code quality check:")
    print(f"  Smart ID locators: {'✓ YES' if has_smart_ids else '✗ NO'}")
    print(f"  Bad placeholder XPaths: {'✗ YES (BAD!)' if has_bad_xpaths else '✓ NO'}")
    print(f"  Login-specific tests: {'✓ YES' if has_login_tests else '✗ NO'}")
    print(f"  Generic form tests: {'✗ YES (WRONG!)' if has_form_tests else '✓ NO'}")
    
    print("\n" + "="*80)
    print("GENERATED CODE PREVIEW")
    print("="*80)
    
    # Show first 100 lines
    lines = test_class.split('\n')[:100]
    print('\n'.join(lines))
    
    if len(test_class.split('\n')) > 100:
        print(f"\n... ({len(test_class.split('\n')) - 100} more lines)")
    
    print("\n" + "="*80)
    print("DIAGNOSIS")
    print("="*80)
    
    if detected_type == "LOGIN" and has_login_tests and has_smart_ids and not has_bad_xpaths:
        print("\n✓✓✓ SUCCESS! Everything working correctly!")
        print("The issue is browser caching. Do a hard refresh (Ctrl+Shift+R)")
    elif detected_type != "LOGIN":
        print(f"\n✗✗✗ PROBLEM: Wrong test type detected ({detected_type} instead of LOGIN)")
        print("The OCR is not extracting the 'Password' label correctly")
    elif has_form_tests:
        print("\n✗✗✗ PROBLEM: Generating form tests instead of login tests")
        print("The test type detection logic is broken")
    elif has_bad_xpaths:
        print("\n✗✗✗ PROBLEM: Using bad placeholder XPaths instead of smart IDs")
        print("The locator building logic is broken")
    else:
        print("\n⚠️⚠️⚠️ PARTIAL SUCCESS but something is still wrong")
    
    print("\n" + "="*80)
    
    # Save the generated code
    output_file = "test_output_direct.java"
    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(test_class)
    
    print(f"\n✓ Full code saved to: {output_file}")
    print("\nCompare this with the code you're seeing in the browser!")

if __name__ == '__main__':
    test_login_screenshot()
