"""Quick test of field-aware suggestions API"""
import requests
import json

print("=" * 60)
print("Testing Field-Aware Suggestions API")
print("=" * 60)

# Test the API
url = "http://localhost:5002/ml/field-aware-suggestions"
payload = {"test_case_id": "TC002_variant_2"}

print(f"\nCalling: {url}")
print(f"Payload: {json.dumps(payload, indent=2)}")

try:
    response = requests.post(url, json=payload, timeout=10)
    
    print(f"\nStatus Code: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        print("\n✓ SUCCESS!")
        print(f"  Test Case: {data.get('test_name', 'Unknown')}")
        print(f"  Input Fields: {data.get('metadata', {}).get('input_fields_found', 0)}")
        print(f"  Variant Type: {data.get('metadata', {}).get('variant_type', 'none')}")
        print(f"  Scenarios: {data.get('scenarios_count', 0)}")
        
        print("\n  Scenario Breakdown:")
        for scenario in data.get('scenarios', []):
            priority = "⭐" if scenario.get('is_prioritized') else "  "
            print(f"    {priority} {scenario.get('type').upper()}: {len(scenario.get('suggestions', []))} suggestions")
        
        print("\n" + "=" * 60)
        print("Field-aware suggestions are working! ✓")
        print("=" * 60)
        
    else:
        print(f"\n✗ ERROR: {response.status_code}")
        print(f"Response: {response.text}")
        
except Exception as e:
    print(f"\n✗ EXCEPTION: {str(e)}")

# Show debug log
print("\n" + "=" * 60)
print("Debug Log (last 20 lines):")
print("=" * 60)
try:
    with open(r"c:\Users\valaboph\AIAutomation\debug_field_aware.txt", 'r') as f:
        lines = f.readlines()
        for line in lines[-20:]:
            print(line.rstrip())
except FileNotFoundError:
    print("Debug file not found")
