import requests
import time

print("Calling API...")
time.sleep(2)

try:
    r = requests.post("http://localhost:5002/ml/field-aware-suggestions", 
                      json={"test_case_id": "TC002_variant_2"},
                      timeout=10)
    print(f"Status: {r.status_code}")
    if r.status_code != 200:
        print(f"Error: {r.text[:200]}")
except Exception as e:
    print(f"Exception: {e}")

# Read debug log
print("\n=== DEBUG LOG ===")
try:
    with open(r"c:\Users\valaboph\AIAutomation\debug_field_aware.txt", 'r', encoding='utf-8') as f:
        print(f.read())
except Exception as e:
    print(f"Could not read debug log: {e}")

print("\n=== Looking for key indicators ===")
try:
    with open(r"c:\Users\valaboph\AIAutomation\debug_field_aware.txt", 'r', encoding='utf-8') as f:
        content = f.read()
        if "Script dir:" in content:
            print("✓ NEW debugging code IS running!")
        else:
            print("✗ OLD code still running (no 'Script dir:' found)")
        
        if "pathlib" in content or ".rglob" in content:
            print("✓ Pathlib search method detected")
        else:
            print("? Pathlib not mentioned in debug")
            
except Exception as e:
    print(f"Error: {e}")
