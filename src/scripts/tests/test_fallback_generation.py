"""Test script to demonstrate fallback code generation for consolidated email/password entries."""

import sys
import os

# Add the src/main/python directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src', 'main', 'python'))

from core.inference_improved import UnifiedInference

# Initialize inference with the new consolidated dataset
inference = UnifiedInference(
    dataset_path='src/resources/combined-training-dataset-final-consolidated-v2.json'
)

# Test prompts
test_cases = [
    {
        "prompt": "enter text in email field",
        "language": "python",
        "description": "Generic email field (should use consolidated entry with 14 fallbacks)"
    },
    {
        "prompt": "type text in producer email",
        "language": "python",
        "description": "Producer-specific email (should match via prompt_variations)"
    },
    {
        "prompt": "enter text in password field",
        "language": "python",
        "description": "Generic password field (should use consolidated entry with 14 fallbacks)"
    },
    {
        "prompt": "input text in producer password",
        "language": "python",
        "description": "Producer-specific password (should match via prompt_variations)"
    },
    {
        "prompt": "enter test@email.com in email",
        "language": "python",
        "description": "Universal pattern with value (should use universal handler or dataset fallbacks)"
    },
    {
        "prompt": "enter Secret123! in producer password",
        "language": "python",
        "description": "Universal pattern for producer password (should use universal handler or dataset fallbacks)"
    }
]

print("=" * 80)
print("FALLBACK CODE GENERATION TEST")
print("=" * 80)
print()

for i, test in enumerate(test_cases, 1):
    print(f"\n{'='*80}")
    print(f"TEST {i}: {test['description']}")
    print(f"{'='*80}")
    print(f"Prompt: {test['prompt']}")
    print(f"Language: {test['language']}")
    print("-" * 80)
    
    try:
        result = inference.generate_code(
            prompt=test['prompt'],
            language=test['language'],
            comprehensive_mode=False
        )
        
        code = result.get('code', '').strip()
        match_source = result.get('match_source', 'unknown')
        match_method = result.get('match_method', 'unknown')
        
        print(f"\n✅ MATCH FOUND")
        print(f"   Source: {match_source}")
        print(f"   Method: {match_method}")
        print(f"\n📝 GENERATED CODE:")
        print("-" * 80)
        print(code)
        print("-" * 80)
        
        # Check if fallback logic is present
        if 'selectors = [' in code or 'for selector in selectors' in code:
            print("\n🎯 FALLBACK LOGIC DETECTED!")
            # Count how many selectors
            if 'selectors = [' in code:
                selector_count = code.count('",') + 1  # Rough count
                print(f"   Approximately {selector_count} fallback selectors in use")
        else:
            print("\n⚠️  No fallback logic detected (single selector)")
            
    except Exception as e:
        print(f"\n❌ ERROR: {str(e)}")
    
    print()

print("\n" + "=" * 80)
print("TEST COMPLETE")
print("=" * 80)
            print("GENERATED CODE WITH FALLBACKS:")
            print(f"{'─' * 80}")
            print(generated_code)
            print(f"{'─' * 80}\n")
            
            # Show alternatives
            alternatives = data.get('alternatives', [])
            if alternatives:
                print(f"\n🔄 FALLBACK ALTERNATIVES ({len(alternatives)}):")
                for i, alt in enumerate(alternatives, 1):
                    strategy = alt.get('strategy', 'unknown')
                    confidence = alt.get('score', 0.0)
                    matched_prompt = alt.get('prompt', '')
                    print(f"  {i}. [{strategy}] {confidence:.1%} confidence - \"{matched_prompt}\"")
        else:
            print(f"❌ ERROR: {response.status_code}")
            print(response.text)
        
        print()


def test_without_fallbacks():
    """Test standard generation without fallbacks for comparison."""
    
    prompt = "click login button"
    
    print(f"\n{'=' * 80}")
    print(f"STANDARD GENERATION (NO FALLBACKS)")
    print(f"{'=' * 80}\n")
    print(f"PROMPT: {prompt}\n")
    
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "language": "java",
            "with_fallbacks": False  # Disable fallbacks
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        generated_code = data.get('generated', '')
        
        print(f"✅ SUCCESS - Generated standard code")
        print(f"\n{'─' * 80}")
        print("GENERATED CODE (NO FALLBACKS):")
        print(f"{'─' * 80}")
        print(generated_code)
        print(f"{'─' * 80}\n")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)


def test_python_fallbacks():
    """Test fallback generation for Python language."""
    
    prompt = "click submit button"
    
    print(f"\n{'=' * 80}")
    print(f"PYTHON SELF-HEALING CODE GENERATION")
    print(f"{'=' * 80}\n")
    print(f"PROMPT: {prompt}\n")
    
    response = requests.post(
        f"{API_URL}/generate",
        json={
            "prompt": prompt,
            "language": "python",
            "with_fallbacks": True,
            "max_fallbacks": 3
        }
    )
    
    if response.status_code == 200:
        data = response.json()
        generated_code = data.get('generated', '')
        fallback_count = data.get('fallback_count', 0)
        
        print(f"✅ SUCCESS - Generated Python self-healing code")
        print(f"📊 Fallback locators: {fallback_count}")
        print(f"\n{'─' * 80}")
        print("GENERATED PYTHON CODE:")
        print(f"{'─' * 80}")
        print(generated_code)
        print(f"{'─' * 80}\n")
    else:
        print(f"❌ ERROR: {response.status_code}")
        print(response.text)


if __name__ == "__main__":
    print("\n" + "=" * 80)
    print(" " * 20 + "FALLBACK CODE GENERATION TEST")
    print("=" * 80 + "\n")
    
    print("This test demonstrates self-healing test automation where:")
    print("  1. Primary locator is tried first")
    print("  2. If it fails, alternative locators are tried automatically")
    print("  3. The code logs which locator worked for debugging")
    print("  4. Tests adapt to UI changes without manual updates")
    print()
    
    try:
        # Test 1: Java with fallbacks
        test_fallback_generation()
        
        # Test 2: Standard generation without fallbacks
        test_without_fallbacks()
        
        # Test 3: Python with fallbacks
        test_python_fallbacks()
        
        print("\n" + "=" * 80)
        print("✅ ALL TESTS COMPLETED")
        print("=" * 80)
        
    except requests.exceptions.ConnectionError:
        print("\n❌ ERROR: Cannot connect to API server")
        print("Make sure the server is running: python src/main/python/api_server_modular.py")
    except Exception as e:
        print(f"\n❌ ERROR: {e}")
