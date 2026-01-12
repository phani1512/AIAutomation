"""
Direct code generation without web server
"""
import sys
import os
sys.path.insert(0, 'src/main/python')

from inference_improved import ImprovedSeleniumGenerator

# Initialize generator
print("Loading AI model...")
generator = ImprovedSeleniumGenerator('selenium_ngram_model.pkl')
print("Ready!\n")

# Example usage
prompts = [
    "click login button",
    "enter text in username field", 
    "select from dropdown menu",
    "verify page title"
]

print("=" * 60)
print("Generated Selenium Code Examples")
print("=" * 60)

for prompt in prompts:
    print(f"\nPrompt: {prompt}")
    print("-" * 60)
    code = generator.generate_clean(prompt, max_tokens=50)
    print(code)
    print()
