"""
Test the exact bugfix scenario: email, password, login button
"""
import requests

BASE_URL = "http://localhost:5002"

print("=" * 70)
print("TESTING BUGFIX SCENARIO (Email + Password + Login)")
print("=" * 70)

# Create session
r = requests.post(f"{BASE_URL}/test-suite/session/start", json={
    "name": "bugfix",
    "description": "Test: bugfix"
})
session_id = r.json()['session']['session_id']
print(f"\nCreated session: {session_id}")

# Add email step
print("\nAdding Step 1: enter text in email field...")
r = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
    json={
        "prompt": "enter text in email field",
        "value": "test@email.com",  # User's actual email
        "language": "python"
    }
)
print(f"  Status: {r.status_code}")

# Add password step  
print("\nAdding Step 2: enter text in password field...")
r = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
    json={
        "prompt": "enter text in password field",
        "value": "MyPassword123!",  # User's actual password
        "language": "python"
    }
)
print(f"  Status: {r.status_code}")

# Add login button click
print("\nAdding Step 3: click login button...")
r = requests.post(
    f"{BASE_URL}/test-suite/session/{session_id}/add-prompt",
    json={
        "prompt": "click login button",
        "language": "python"
    }
)
print(f"  Status: {r.status_code}")

# Get preview
print("\n" + "=" * 70)
print("GETTING PREVIEW")
print("=" * 70)

r = requests.get(f"{BASE_URL}/test-suite/session/{session_id}/preview?language=python")

if r.status_code == 200:
    preview = r.json()['code']
    
    # Check for correct values
    checks = [
        ('test@email.com', 'Email value'),
        ('MyPassword123!', 'Password value'),
        ('send_keys("test@email.com")', 'Email with quotes'),
        ('send_keys("MyPassword123!")', 'Password with quotes'),
    ]
    
    wrong_checks = [
        ('send_keys("value")', 'Literal "value" string'),
        ('{VALUE}', 'Unreplaced placeholder'),
        ('send_keys(value)', 'Unquoted value variable'),
    ]
    
    print("\nPOSITIVE CHECKS:")
    for check, desc in checks:
        if check in preview:
            print(f"  [PASS] {desc}: Found '{check}'")
        else:
            print(f"  [FAIL] {desc}: NOT FOUND '{check}'")
    
    print("\nNEGATIVE CHECKS (should NOT be present):")
    for check, desc in wrong_checks:
        if check not in preview:
            print(f"  [PASS] {desc}: Correctly absent")
        else:
            print(f"  [FAIL] {desc}: STILL PRESENT!")
    
    # Show the actual send_keys lines
    print("\n" + "=" * 70)
    print("ACTUAL SEND_KEYS LINES:")
    print("=" * 70)
    for i, line in enumerate(preview.split('\n'), 1):
        if 'send_keys' in line.lower():
            print(f"Line {i}: {line.strip()}")
            
    print("\n" + "=" * 70)
    print("FINAL VERDICT")
    print("=" * 70)
    
    if 'test@email.com' in preview and 'MyPassword123!' in preview and 'send_keys("value")' not in preview:
        print("[SUCCESS] All values correctly substituted with proper quotes!")
        print("The generated test is ready to use.")
    else:
        print("[FAILED] Issues still present in generated code")
else:
    print(f"[ERROR] Failed: {r.text}")
