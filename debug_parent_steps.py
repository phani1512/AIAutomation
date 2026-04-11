"""
Debug: Check if parent test steps have generated_code
"""
import sys
sys.path.insert(0, 'src/main/python')

from test_management.test_case_builder import TestCaseBuilder

builder = TestCaseBuilder()

# Load parent test TC001
parent_test = builder.load_test_case('TC001')

if parent_test:
    print(f"\n✓ Parent test loaded: {parent_test.name}")
    print(f"  Test ID: {parent_test.test_case_id}")
    print(f"  Steps: {len(parent_test.steps)}")
    
    # Check each step for generated_code
    for i, step in enumerate(parent_test.steps):
        step_num = step.get('step', i+1)
        prompt = step.get('prompt', 'N/A')
        has_code = 'generated_code' in step
        code_length = len(step.get('generated_code', '')) if has_code else 0
        
        print(f"\n  Step {step_num}: {prompt[:50]}...")
        print(f"    Has generated_code: {has_code}")
        if has_code:
            code_preview = step['generated_code'][:100].replace('\n', ' ')
            print(f"    Code preview: {code_preview}...")
        else:
            print(f"    ⚠ NO CODE!")
else:
    print("✗ Parent test TC001 not found!")
