"""Debug table row count issue"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from core.inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator(silent=True)

prompt = 'how many rows in table'
print(f"Prompt: '{prompt}'\n")

# Check dataset match
dataset = gen._find_dataset_match(prompt)
if dataset:
    print(f"Dataset code: {dataset.get('code')}")
    print(f"Dataset locator: {dataset.get('locator')}")
    print(f"Dataset action: {dataset.get('action')}\n")
    
    # Generate simple code from locator
    simple = gen._simple_code_from_locator(dataset['locator'], dataset.get('action'), prompt)
    print(f"Simple code generated: {simple}\n")
    
    # Enhance with ComprehensiveCodeGenerator
    enhanced = gen.comprehensive_generator.enhance_to_comprehensive(
        simple_code=simple,
        prompt=prompt,
        language='java'
    )
    print(f"Enhanced code:\n{enhanced}\n")
    
    # Check for expected keywords
    has_presence = 'presenceOfAllElementsLocatedBy' in enhanced
    has_size = 'rows.size()' in enhanced or 'elements.size()' in enhanced
    
    print(f"Has 'presenceOfAllElementsLocatedBy': {has_presence}")
    print(f"Has 'size()': {has_size}")
    print(f"Status: {'✓ PASS' if (has_presence and has_size) else '✗ FAIL'}")
