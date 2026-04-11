"""
Test if the docstring fix is working on the server
"""
import requests
import time

print("Waiting for server...")
time.sleep(3)

print("\nTesting semantic test execution...")

# Call the execute endpoint with a semantic test
test_id = "TC002_variant_1"  # Field Length Boundary Testing

try:
    response = requests.post(
        "http://localhost:5002/recorder/execute-test",
        json={
            "test_id": test_id,
            "headless": True
        },
        timeout=30
    )
    
    print(f"Status: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"\n✓ Test executed!")
        print(f"  Success: {result.get('success')}")
        print(f"  Status: {result.get('status')}")
        
        if result.get('logs'):
            print("\n  Last 5 logs:")
            for log in result['logs'][-5:]:
                print(f"    [{log['level']}] {log['message'][:80]}")
                
        if not result.get('success'):
            print(f"\n  Error: {result.get('error_message', 'Unknown')[:200]}")
    else:
        print(f"Error: {response.text[:200]}")
        
except Exception as e:
    print(f"Exception: {e}")

print("\n" + "="*70)
print("If you see 'Syntax Error' above, the fix didn't work")
print("If you see success or a different error, the docstring fix worked!")
print("="*70)
