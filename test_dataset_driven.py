import sys
sys.path.insert(0, 'src/main/python')

from inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator()

# Test prompts that should be found in datasets
test_prompts = [
    "click producer login button",  # common-web-actions
    "enter email in producer-email field",  # common-web-actions
    "click search button",  # common-web-actions
    "select United States from country dropdown",  # common-web-actions
    "upload file test.txt",  # common-web-actions
    "click on producer-login",  # Should still work with fallback
]

print("=" * 80)
print("TESTING DATASET-DRIVEN ELEMENT EXTRACTION")
print("=" * 80)

for prompt in test_prompts:
    print(f"\nPrompt: '{prompt}'")
    print("-" * 80)
    
    # Show what was found in dataset
    match = gen._find_dataset_match(prompt)
    if match:
        print(f"✅ Found in dataset:")
        print(f"   Locator: {match.get('locator', 'N/A')}")
    else:
        print(f"⚠️  Not found in dataset - using fallback")
    
    # Show extracted element
    element = gen._extract_element_name(prompt)
    print(f"   Extracted: {element}")
    
    # Generate code
    result = gen.generate_clean(prompt)
    print(f"\nGenerated Code:")
    print(result)
    print()
