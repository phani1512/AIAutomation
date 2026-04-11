# Debug script to trace exact flow for "click Carrier Account 2 button"

import requests
import json

prompt = "click Carrier Account 2 button"
url = "http://localhost:5002/generate"

payload = {
    "prompt": prompt,
    "language": "python",
    "with_fallbacks": True,
    "compact_mode": True
}

print(f"🔍 Testing prompt: '{prompt}'")
print("=" * 70)

response = requests.post(url, json=payload)
result = response.json()

print("\n📝 GENERATED CODE:")
print("-" * 70)
print(result.get('generated', 'NO CODE'))
print("-" * 70)

print("\n📊 METADATA:")
print(f"Has fallbacks: {result.get('has_fallbacks', False)}")
print(f"Fallback count: {result.get('fallback_count', 0)}")

# Extract and display actual selectors
code = result.get('generated', '')
if 'selectors = [' in code:
    start = code.index('selectors = [')
    end = code.index(']', start) + 1
    selectors_line = code[start:end]
    print(f"\n🎯 ACTUAL SELECTORS GENERATED:")
    print(selectors_line[:200] + "..." if len(selectors_line) > 200 else selectors_line)
else:
    print("\n❌ NO SELECTORS ARRAY FOUND - Code might be wrong format!")

# Check for wrong patterns
if '{FIELD}' in code or '{VALUE}' in code:
    print("\n⚠️  WARNING: Unsubstituted placeholders found!")
if 'send_keys' in code.lower() or 'sendkeys' in code.lower():
    print("\n⚠️  WARNING: Using send_keys for a CLICK action!")
if 'By.ID' in code and 'button' in prompt.lower():
    print("\n⚠️  WARNING: Using ID locator for button instead of text-based XPath!")
