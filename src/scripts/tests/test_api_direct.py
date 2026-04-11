import requests
import json

url = "http://localhost:5002/generate"

payload = {
    "prompt": "click login button",
    "language": "java",
    "comprehensive_mode": True,
    "with_fallbacks": False
}

print(f"🧪 Testing: {payload['prompt']}")
print(f"📤 Sending request...")

response = requests.post(url, json=payload)
result = response.json()

print(f"\n📥 Response:")
print(json.dumps(result, indent=2))

print(f"\n🔍 Alternatives count: {len(result.get('alternatives', []))}")
if result.get('alternatives'):
    print("\n💡 Alternatives:")
    for alt in result['alternatives']:
        print(f"  - [{alt['score']:.1%}] {alt['prompt']}")
else:
    print("\n❌ NO ALTERNATIVES in response")
