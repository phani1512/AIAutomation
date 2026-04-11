"""
Regenerate execution-ready code for semantic variant tests.
This ensures they have the latest URL navigation logic.
"""
import sys
import os
import json

# Add project paths
project_root = os.path.abspath(os.path.dirname(__file__))
src_path = os.path.join(project_root, 'src', 'main', 'python')
sys.path.insert(0, src_path)

from test_management.test_case_builder import TestCaseBuilder, TestCase

def regenerate_variant_code(test_case_id):
    """Regenerate execution-ready code for a semantic variant."""
    print(f"\n=== Regenerating code for {test_case_id} ===")
    
    builder = TestCaseBuilder()
    
    # Load the test case
    test_case = builder.load_test_case(test_case_id)
    if not test_case:
        print(f"❌ Test case {test_case_id} not found")
        return False
    
    print(f"✓ Loaded test case: {test_case.name}")
    print(f"  URL: {test_case.url}")
    print(f"  Parent: {test_case.parent_test_case_id}")
    print(f"  Prompts: {len(test_case.prompts)}")
    
    # Regenerate execution-ready code for each prompt
    if test_case.prompts:
        print("\n Regenerating code for each prompt...")
        for i, prompt in enumerate(test_case.prompts):
            print(f"\n  Prompt {i+1}: {prompt.get('description', 'No description')}")
            
            # Create a temporary test case with just this prompt's steps
            temp_test = TestCase(
                test_case_id=test_case.test_case_id,
                name=test_case.name,
                description=test_case.description,
                url=test_case.url  # This should have the URL now
            )
            temp_test.parent_test_case_id = test_case.parent_test_case_id
            temp_test.steps = prompt.get('steps', [])
            
            # Generate execution-ready code
            new_code = builder._generate_python_code_execution_ready(temp_test)
            
            # Update the prompt's generated_code
            prompt['generated_code'] = new_code
            
            # Check if URL is in the code
            has_url = 'driver.get(' in new_code
            print(f"    Code length: {len(new_code)} chars")
            print(f"    Has driver.get(): {has_url}")
            if has_url:
                # Extract the URL line
                for line in new_code.split('\n'):
                    if 'driver.get(' in line:
                        print(f"    Found: {line.strip()}")
                        break
        
        # Save the updated test case
        builder.save_test_case(test_case)
        print(f"\n✓ Saved updated test case with {len(test_case.prompts)} prompts")
        return True
    else:
        print("❌ No prompts found in test case")
        return False

if __name__ == "__main__":
    # Regenerate code for all semantic variants
    variants = [
        "TC001_variant_1"
    ]
    
    for variant_id in variants:
        success = regenerate_variant_code(variant_id)
        if success:
            print(f"\n✅ Successfully regenerated {variant_id}")
        else:
            print(f"\n❌ Failed to regenerate {variant_id}")
