"""Debug script to trace why alternatives aren't being returned."""
import sys
sys.path.insert(0, 'src/main/python')

from core.inference_improved import ImprovedSeleniumGenerator

# Create engine instance
print("Loading ImprovedSeleniumGenerator...")
engine = ImprovedSeleniumGenerator(silent=True)
print(f"✅ Engine loaded\n")

# Test specific prompts
test_prompts = [
    "click login button",
    "click email preview over lay dialog close button",
    "enter username",
    "verify title is Login Page"
]

for prompt in test_prompts:
    print(f"\n{'='*80}")
    print(f"🧪 TESTING: '{prompt}'")
    print('='*80)
    
    # Call _find_dataset_match with return_alternatives=True
    result = engine._find_dataset_match(prompt, return_alternatives=True)
    
    if isinstance(result, dict):
        match = result.get('match')
        alternatives = result.get('alternatives', [])
        
        print(f"\n📋 RESULT:")
        print(f"  Primary match: {match is not None}")
        if match:
            code = match.get('code', 'N/A')
            print(f"  Match code: {code[:100] if code else 'None'}...")
        print(f"  Alternatives count: {len(alternatives)}")
        
        if alternatives:
            print(f"\n💡 ALTERNATIVES:")
            for i, alt in enumerate(alternatives[:5], 1):
                print(f"  {i}. [{alt['score']:.1%}] {alt['prompt']}")
        else:
            print(f"\n❌ NO ALTERNATIVES RETURNED")
    else:
        print(f"\n⚠️ Result is not a dict: {type(result)}")

print(f"\n\n{'='*80}")
print("DEBUG COMPLETE")
print('='*80)
