"""Test code generation directly"""
import sys
sys.path.insert(0, r'c:\Users\valaboph\AIAutomation\src\main\python')

from core.inference_improved import ImprovedSeleniumGenerator

# Test code generation
gen = ImprovedSeleniumGenerator()

test_prompts = [
    "click login button",
    "enter username in username field",
    "click submit"
]

print("="*70)
print("TESTING CODE GENERATION")
print("="*70)

for prompt in test_prompts:
    print(f"\n📝 Testing: {prompt}")
    try:
        result = gen.infer(
            prompt, 
            return_alternatives=False,
            language='python',
            comprehensive_mode=False,
            preserve_data_placeholder=True
        )
        
        if result and 'code' in result:
            code = result['code']
            print(f"✅ SUCCESS")
            print(f"Generated code: {code}")
        else:
            print(f"❌ FAILED - No code in result: {result}")
    except Exception as e:
        print(f"❌ ERROR: {e}")
        import traceback
        traceback.print_exc()

print("\n" + "="*70)
