import sys
sys.path.insert(0, 'src/main/python')

from inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator()

# Test the exact prompt
prompt = "click on producer-login"
print(f"Testing prompt: '{prompt}'")
print("=" * 60)

result = gen.generate_clean(prompt)
print(f"\nGenerated Code:\n{result}")
print("=" * 60)

# Test element name extraction
element_name = gen._extract_element_name(prompt)
print(f"\nExtracted element name: {element_name}")
