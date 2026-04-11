"""Quick Test - Verify placeholder fix"""
import requests

BASE_URL = "http://localhost:5002"

print("=" * 70)
print("TESTING PLACEHOLDER FIX")
print("=" * 70)

# Create session
print("\nStep 1: Creating session...")
r = requests.post(f"{BASE_URL}/test-suite/session/start", json={
    "name": "Placeholder Test",
    "description": "Testing VALUE placeholder"
})
session_id = r.json()['session']['session_id']
print(f"Created session: {session_id}")

# Add prompt with value
print("\nStep 2: Adding prompt with value 'myemail@test.com'...")
r = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
    json={
        "prompt": "enter text in email field",
        "value": "myemail@test.com",
        "language": "python"
    }
)

if r.status_code == 200:
    code = r.json()['step_result']['code']
    print(f"\nGenerated code preview:")
    print(code[:300])
    if '{VALUE}' in code:
        print("\n[OK] {VALUE} placeholder found in generated code")
    else:
        print("\n[FAIL] {VALUE} placeholder NOT found!")
        print("Full code:")
        print(code)
else:
    print(f"[ERROR] Failed to add prompt: {r.text}")
    exit(1)

# Get preview
print("\nStep 3: Getting preview...")
r = requests.get(f"{BASE_URL}/test-suite/session/{session_id}/preview?language=python")

if r.status_code == 200:
    preview = r.json()['code']
    
    # Check for replacement
    if 'myemail@test.com' in preview:
        print("[PASS] Value 'myemail@test.com' correctly substituted!")
    else:
        print("[FAIL] Value NOT substituted!")
        
    if '{VALUE}' in preview:
        print("[FAIL] {VALUE} placeholder still present in preview!")
    else:
        print("[PASS] {VALUE} placeholder correctly replaced!")
        
    # Check for literal "value" string
    if 'send_keys("value")' in preview or "send_keys('value')" in preview:
        print("[FAIL] Found send_keys('value') - using wrong value!")
    else:
        print("[PASS] No literal 'value' string found!")
        
    # Show relevant lines
    print("\nRelevant lines from preview:")
    for i, line in enumerate(preview.split('\n'), 1):
        if 'send_keys' in line.lower() or 'myemail' in line.lower():
            print(f"  Line {i}: {line.strip()}")
else:
    print(f"[ERROR] Failed to get preview: {r.text}")
    exit(1)

print("\n" + "=" * 70)
print("TEST COMPLETE")
print("=" * 70)
