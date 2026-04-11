"""
Comprehensive test for send_keys quote verification across all code paths
"""
import sys
sys.path.insert(0, r'c:\Users\valaboph\AIAutomation\src\main\python')

from core.inference_improved import ImprovedSeleniumGenerator
from core.fallback_strategy import FallbackStrategyGenerator
from core.universal_patterns import UniversalPatternHandler
from generators.comprehensive_code_generator import ComprehensiveCodeGenerator
from core.locator_utils import LocatorUtils

def test_send_keys_quotes():
    """Test that all send_keys calls properly quote values"""
    print("=" * 70)
    print("TESTING SEND_KEYS QUOTES ACROSS ALL CODE PATHS")
    print("=" * 70)
    
    gen = ImprovedSeleniumGenerator()
    
    test_cases = [
        ("enter test in email field", "python"),
        ("enter test in username", "python"),
        ("type password in password field", "python"),
        ("fill test@email.com in email", "python"),
        ("enter test in email field", "java"),
        ("enter test in username", "javascript"),
        ("type password in password field", "csharp"),
    ]
    
    issues_found = []
    
    for prompt, language in test_cases:
        print(f"\n📝 Testing: {prompt} ({language})")
        try:
            result = gen.infer(
                prompt,
                return_alternatives=False,
                language=language,
                comprehensive_mode=False,
                preserve_data_placeholder=True
            )
            
            code = result.get('code', '')
            
            # Check for problematic patterns
            problems = []
            
            # Pattern 1: send_keys(value) without quotes
            if 'send_keys(value)' in code or 'sendKeys(value)' in code or 'SendKeys(value)' in code:
                problems.append("❌ Found send_keys(value) - missing quotes!")
            
            # Pattern 2: send_keys({VALUE}) without outer quotes
            if 'send_keys({VALUE})' in code or 'sendKeys({VALUE})' in code:
                problems.append("❌ Found send_keys({VALUE}) - missing quotes!")
            
            # Check for correct patterns
            has_correct = (
                'send_keys("{VALUE}")' in code or 
                'sendKeys("{VALUE}")' in code or
                'SendKeys("{VALUE}")' in code or
                'send_keys(\'{VALUE}\')' in code
            )
            
            if problems:
                issues_found.extend(problems)
                for p in problems:
                    print(f"  {p}")
                print(f"  Code snippet: {code[:200]}...")
            elif has_correct:
                print(f"  ✅ Correct: Found properly quoted placeholder")
            else:
                # Might be a click action or other non-input action
                if 'send_keys' in code.lower():
                    print(f"  ⚠️  Warning: send_keys found but pattern unclear")
                    print(f"  Code: {code[:200]}...")
                else:
                    print(f"  ℹ️  No send_keys in this code (might be click/navigate)")
                    
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            issues_found.append(f"Exception in {prompt}: {e}")
    
    print("\n" + "=" * 70)
    if issues_found:
        print(f"❌ FOUND {len(issues_found)} ISSUES:")
        for issue in issues_found:
            print(f"  - {issue}")
        print("\n⚠️  QUOTE ISSUES DETECTED - NEED FIXES")
    else:
        print("✅ ALL TESTS PASSED - NO QUOTE ISSUES FOUND")
    print("=" * 70)
    
    return len(issues_found) == 0


def test_fallback_strategy_quotes():
    """Test fallback strategy specifically"""
    print("\n" + "=" * 70)
    print("TESTING FALLBACK STRATEGY SEND_KEYS QUOTES")
    print("=" * 70)
    
    fallback_gen = FallbackStrategyGenerator()
    locator_utils = LocatorUtils()
    
    # Test with email field
    selectors = locator_utils.generate_field_selectors('email')
    
    languages = ['python', 'java', 'javascript', 'csharp']
    issues = []
    
    for lang in languages:
        print(f"\n📝 Testing {lang} fallback code")
        try:
            code = fallback_gen.generate_code_with_fallbacks(
                prompt="enter test in email",
                fallback_selectors=selectors,
                action_type="input",
                language=lang,
                comprehensive_mode=False,
                value_extractor_func=lambda p: "test_value"
            )
            
            # Check for issues
            if lang == 'python':
                if 'send_keys(value)' in code or 'send_keys(test_value)' in code:
                    issues.append(f"❌ {lang}: Missing quotes in send_keys")
                    print(f"  ❌ Found unquoted value")
                elif 'send_keys("' in code:
                    print(f"  ✅ Properly quoted")
                else:
                    print(f"  ⚠️  No send_keys found")
                    
            elif lang == 'java':
                if 'sendKeys(value)' in code or 'sendKeys(test_value)' in code:
                    issues.append(f"❌ {lang}: Missing quotes in sendKeys")
                    print(f"  ❌ Found unquoted value")
                elif 'sendKeys("' in code:
                    print(f"  ✅ Properly quoted")
                else:
                    print(f"  ⚠️  No sendKeys found")
                    
        except Exception as e:
            print(f"  ❌ ERROR: {e}")
            issues.append(f"{lang} exception: {e}")
    
    print("\n" + "=" * 70)
    if issues:
        print(f"❌ FOUND {len(issues)} ISSUES IN FALLBACK STRATEGY:")
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("✅ ALL FALLBACK TESTS PASSED")
    print("=" * 70)
    
    return len(issues) == 0


if __name__ == "__main__":
    print("\n🔍 COMPREHENSIVE SEND_KEYS QUOTE VERIFICATION\n")
    
    test1_pass = test_send_keys_quotes()
    test2_pass = test_fallback_strategy_quotes()
    
    print("\n" + "=" * 70)
    print("FINAL RESULTS:")
    print("=" * 70)
    print(f"Main inference tests: {'✅ PASS' if test1_pass else '❌ FAIL'}")
    print(f"Fallback strategy tests: {'✅ PASS' if test2_pass else '❌ FAIL'}")
    print("=" * 70)
    
    if test1_pass and test2_pass:
        print("\n🎉 ALL TESTS PASSED - CODE IS READY FOR PRODUCTION")
        sys.exit(0)
    else:
        print("\n⚠️  SOME TESTS FAILED - REVIEW NEEDED")
        sys.exit(1)
