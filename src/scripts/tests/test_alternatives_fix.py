"""
Test script to verify alternatives generation after fix.
Tests both:
1. Strong match scenario (primary match + alternatives)
2. Weak match scenario (no primary match but alternatives shown)
"""

import requests
import json

API_URL = "http://localhost:5002/generate"

def test_code_generation(prompt, language='java'):
    """Test code generation and check for alternatives."""
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: '{prompt}' (Language: {language})")
    print('='*80)
    
    payload = {
        'prompt': prompt,
        'language': language,
        'comprehensive_mode': True,
        'with_fallbacks': False  # Disable fallback mode to test alternatives system
    }
    
    try:
        response = requests.post(API_URL, json=payload, timeout=30)
        response.raise_for_status()
        
        data = response.json()
        
        # Check generated code
        generated = data.get('generated', '')
        print(f"\n📝 GENERATED CODE (first 200 chars):")
        print(generated[:200] + ('...' if len(generated) > 200 else ''))
        
        # Check language conversion
        if language == 'java':
            if 'WebDriverWait wait = new' in generated:
                print("\n✅ LANGUAGE CONVERSION: Java syntax confirmed!")
            elif 'wait = WebDriverWait' in generated:
                print("\n❌ LANGUAGE CONVERSION FAILED: Still Python syntax!")
            else:
                print("\n⚠️ LANGUAGE: Code doesn't match typical patterns")
        
        # Check alternatives
        alternatives = data.get('alternatives', [])
        print(f"\n💡 ALTERNATIVES FOUND: {len(alternatives)}")
        
        if alternatives:
            print("\n📋 Alternative suggestions:")
            for i, alt in enumerate(alternatives[:5], 1):
                score = alt.get('score', 0)
                alt_prompt = alt.get('prompt', 'N/A')
                print(f"  {i}. [{score:.1%}] {alt_prompt}")
            print("\n✅ ALTERNATIVES: Working! Modal should appear")
        else:
            print("\n❌ ALTERNATIVES: None returned - modal won't show")
        
        return data
        
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
        return None

# Test cases
print("\n" + "="*80)
print("🎯 ALTERNATIVES FIX VERIFICATION")
print("="*80)

# Test 1: Prompt that might not be in dataset (weak/no match)
test_code_generation("click login button", "java")

# Test 2: Prompt that likely IS in dataset (strong match)
test_code_generation("click email preview over lay dialog close button", "java")

# Test 3: Another common action
test_code_generation("enter username", "java")

# Test 4: Verify action (should filter alternatives by action type)
test_code_generation("verify title is Login Page", "java")

print("\n" + "="*80)
print("🏁 TEST COMPLETE")
print("="*80)
print("\n📊 EXPECTED RESULTS:")
print("  ✓ All tests should show Java syntax (not Python)")
print("  ✓ All tests should show alternatives (even if no strong match)")
print("  ✓ Alternatives should be semantically relevant")
print("  ✓ Browser should show 'Did you mean?' modal")
