"""Test to verify fallback selectors and prompt variations work for ALL prompts, not just login."""
import requests
import json

# Test various prompts from different categories
test_prompts = [
    "click login button",           # Click action
    "enter text in email field",    # Input field
    "select from role dropdown",    # Dropdown
    "wait for modal to appear",     # Wait operation
    "click sign in button",         # Another click action
]

url = "http://localhost:5002/generate"

print("="*80)
print("TESTING FALLBACK SELECTORS & PROMPT VARIATIONS ACROSS ALL PROMPT TYPES")
print("="*80)

for prompt in test_prompts:
    print(f"\n{'='*80}")
    print(f"Testing: '{prompt}'")
    print(f"{'='*80}")
    
    data = {
        "prompt": prompt,
        "language": "java",
        "with_fallbacks": True,
        "comprehensive_mode": True
    }
    
    try:
        response = requests.post(url, json=data)
        
        if response.status_code == 200:
            result = response.json()
            
            code = result.get('code', '')
            alternatives = result.get('alternatives', [])
            fallback_count = result.get('fallback_count', 0)
            
            # Quick analysis
            has_fallbacks = fallback_count > 0
            has_try_catch = 'try' in code.lower() or 'catch' in code.lower()
            has_variations = any(alt.get('prompt_variations') for alt in alternatives)
            total_variations = sum(len(alt.get('prompt_variations', [])) for alt in alternatives)
            
            print(f"\n✅ Response received!")
            print(f"  Code length: {len(code)} chars")
            print(f"  Fallback count: {fallback_count}")
            print(f"  Has try-catch: {has_try_catch}")
            print(f"  Alternatives: {len(alternatives)}")
            print(f"  Has variations: {has_variations}")
            print(f"  Total variations: {total_variations}")
            
            # Show first alternative with variations
            if alternatives and len(alternatives) > 0:
                first_alt = alternatives[0]
                variations = first_alt.get('prompt_variations', [])
                print(f"\n  First alternative:")
                print(f"    Prompt: {first_alt.get('prompt', 'N/A')}")
                print(f"    Score: {first_alt.get('score', 0):.1%}")
                print(f"    Variations: {len(variations)}")
                if variations:
                    print(f"    Sample: {variations[:3]}")
            
            # Status check
            if has_fallbacks and has_variations:
                print(f"\n  ✅ PASS: Both fallbacks and variations present")
            elif has_fallbacks:
                print(f"\n  ⚠️ PARTIAL: Has fallbacks but no variations")
            elif has_variations:
                print(f"\n  ⚠️ PARTIAL: Has variations but no fallbacks")
            else:
                print(f"\n  ❌ FAIL: Neither fallbacks nor variations")
        else:
            print(f"  ❌ Error: {response.status_code}")
            
    except Exception as e:
        print(f"  ❌ Exception: {e}")

print(f"\n{'='*80}")
print("TEST COMPLETE")
print(f"{'='*80}")
