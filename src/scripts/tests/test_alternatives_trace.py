"""Test API alternatives with full tracing."""
import requests
import json

# Test the problematic prompt
prompt = "click login button"
language = "java"

print(f"Testing prompt: '{prompt}'")
print(f"Language: {language}\n")

# Make API request
url = "http://localhost:5002/generate"
data = {
    "prompt": prompt,
    "language": language,
    "with_fallbacks": False,
    "comprehensive_mode": True
}

print(f"Sending request to {url}...")
print(f"Request data: {json.dumps(data, indent=2)}\n")

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    print(f"Response received!")
    print(f"\nGenerated code (first 200 chars):")
    print(result.get('code', 'N/A')[:200])
    
    alternatives = result.get('alternatives', [])
    print(f"\nAlternatives ({len(alternatives)}):")
    for i, alt in enumerate(alternatives, 1):
        score = alt.get('score', 0)
        prompt_text = alt.get('prompt', 'N/A')
        category = alt.get('category', 'N/A')
        print(f"  {i}. [{score:.1%}] {prompt_text} (category: {category})")
    
    # Check if the right alternatives were returned
    expected_actions = ['click', 'press', 'tap']
    wrong_actions = ['choose', 'select', 'dropdown']
    
    has_correct = any(any(action in alt.get('prompt', '').lower() for action in expected_actions) 
                     for alt in alternatives)
    has_wrong = any(any(action in alt.get('prompt', '').lower() for action in wrong_actions) 
                   for alt in alternatives)
    
    print(f"\n{'='*80}")
    if has_correct and not has_wrong:
        print("✅ PASS: Alternatives contain click-related suggestions only")
    elif has_wrong:
        print("❌ FAIL: Alternatives contain dropdown suggestions")
    else:
        print("⚠️ WARNING: No clear click or dropdown alternatives found")
    print(f"{'='*80}")
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
