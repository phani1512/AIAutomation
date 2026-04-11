#!/usr/bin/env python3
"""Debug script to capture 500 error details"""
import requests
import json

# Test one of the failing prompts
test_cases = [
    {"prompt": "is button found", "language": "javascript"},
    {"prompt": "get value from username field", "language": "python"},
    {"prompt": "is password field disabled", "language": "javascript"},
    {"prompt": "upload file", "language": "java"},
]

url = "http://localhost:5002/generate"

print("="*80)
print("DEBUGGING 500 ERRORS")
print("="*80)

for test_case in test_cases:
    prompt = test_case["prompt"]
    language = test_case["language"]
    
    print(f"\n\n🔍 Testing: '{prompt}' ({language})")
    print("-"*80)
    
    payload = {
        "prompt": prompt,
        "language": language,
        "comprehensive_mode": True
    }
    
    try:
        response = requests.post(url, json=payload, timeout=10)
        print(f"Status Code: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"✅ SUCCESS: Generated {len(result.get('generated', ''))} chars")
            print(f"Code preview: {result.get('generated', '')[:100]}...")
        else:
            print(f"❌ ERROR {response.status_code}")
            print(f"Response: {response.text[:500]}")
            
            # Try to parse error details
            try:
                error_data = response.json()
                print(f"\nError details:")
                print(json.dumps(error_data, indent=2))
            except:
                print(f"Raw error:\n{response.text}")
    
    except Exception as e:
        print(f"❌ EXCEPTION: {e}")

print("\n" + "="*80)
print("DEBUGGING COMPLETE")
print("="*80)
