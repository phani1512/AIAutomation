"""Quick test to debug inference dataset matching."""
import sys
import os

# Add path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from inference_improved import ImprovedSeleniumGenerator

# Initialize generator
model_path = 'src/resources/selenium_ngram_model.pkl'
generator = ImprovedSeleniumGenerator(model_path, silent=False)

print("\n" + "="*60)
print("TESTING: 'is dialog open' prompt")
print("="*60)

# Test the prompt
prompt = "is dialog open"
code = generator.generate_clean(prompt, language='java')

print(f"\nGenerated code:")
print(code)

print("\n" + "="*60)
print("CHECKING DATASET CACHE")
print("="*60)

# Check if prompt is in cache
if prompt.lower() in generator.dataset_cache:
    entry = generator.dataset_cache[prompt.lower()]
    print(f"✓ Prompt found in cache!")
    print(f"  Code: {entry.get('code')}")
    print(f"  Locator: {entry.get('locator')}")
    print(f"  Action: {entry.get('action')}")
else:
    print(f"✗ Prompt NOT in cache!")
    print(f"\nSearching for similar prompts...")
    for cached_prompt in list(generator.dataset_cache.keys())[:10]:
        if 'dialog' in cached_prompt:
            print(f"  - {cached_prompt}")
