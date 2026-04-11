"""Test to verify fallback selectors and prompt variations are now included."""
import requests
import json

# Test the "click login button" prompt
prompt = "click login button"
language = "java"

print(f"Testing: '{prompt}'\n")

# Make API request with fallbacks enabled
url = "http://localhost:5002/generate"
data = {
    "prompt": prompt,
    "language": language,
    "with_fallbacks": True,  # Now enabled for Generate Code
    "comprehensive_mode": True
}

response = requests.post(url, json=data)

if response.status_code == 200:
    result = response.json()
    
    code = result.get('code', '')
    alternatives = result.get('alternatives', [])
    fallback_count = result.get('fallback_count', 0)
    
    print(f"✅ Response received!\n")
    print(f"Generated code length: {len(code)} characters")
    print(f"Fallback selectors count: {fallback_count}")
    print(f"\nGenerated code (first 300 chars):")
    print(code[:300])
    print("\n" + "="*80)
    
    # Check if code has fallback strategies
    has_fallback_logic = 'try' in code.lower() or 'catch' in code.lower() or 'except' in code.lower()
    has_multiple_selectors = code.count('By.') > 1 or code.count('findElement') > 1
    
    print(f"\n🔍 Fallback Analysis:")
    print(f"  Has try-catch blocks: {has_fallback_logic}")
    print(f"  Has multiple selectors: {has_multiple_selectors}")
    print(f"  Fallback count from API: {fallback_count}")
    
    print(f"\n📋 Alternatives ({len(alternatives)}):")
    for i, alt in enumerate(alternatives, 1):
        score = alt.get('score', 0)
        prompt_text = alt.get('prompt', 'N/A')
        category = alt.get('category', 'N/A')
        variations = alt.get('prompt_variations', [])
        
        print(f"\n  {i}. [{score:.1%}] {prompt_text}")
        print(f"     Category: {category}")
        
        if variations:
            print(f"     ✨ Prompt Variations ({len(variations)}):")
            for v in variations[:5]:  # Show first 5
                print(f"        - {v}")
            if len(variations) > 5:
                print(f"        ... and {len(variations) - 5} more")
        else:
            print(f"     ⚠️ No prompt variations found")
    
    # Summary
    print(f"\n" + "="*80)
    if fallback_count > 0 and any(alt.get('prompt_variations') for alt in alternatives):
        print("✅ SUCCESS: Both fallback selectors AND prompt variations are included!")
    elif fallback_count > 0:
        print("⚠️ PARTIAL: Fallback selectors included, but no prompt variations")
    elif any(alt.get('prompt_variations') for alt in alternatives):
        print("⚠️ PARTIAL: Prompt variations included, but no fallback selectors")
    else:
        print("❌ FAILURE: Neither fallback selectors nor prompt variations included")
    print("="*80)
else:
    print(f"❌ Error: {response.status_code}")
    print(response.text)
