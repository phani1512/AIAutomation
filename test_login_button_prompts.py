import sys
sys.path.insert(0, 'src/main/python')

from inference_improved import ImprovedSeleniumGenerator

gen = ImprovedSeleniumGenerator()

# Test different prompts for the login button
test_prompts = [
    "click producer login button",
    "click on producer-login",
    "click login button",
    "click the login button",
    "click submit button",
    "click the submit button"
]

print("Testing prompts for: <button type=\"submit\" class=\"button primary-btn\">Login</button>")
print("=" * 80)

for prompt in test_prompts:
    print(f"\nPrompt: '{prompt}'")
    print("-" * 80)
    result = gen.generate_clean(prompt)
    print(result)
    print()
