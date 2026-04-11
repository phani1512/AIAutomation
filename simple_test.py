import requests
import time

print("Waiting for server...")
time.sleep(3)

print("Calling API...")
try:
    r = requests.post("http://localhost:5002/ml/field-aware-suggestions", 
                      json={"test_case_id": "TC002_variant_2"}, 
                      timeout=10)
    print(f"Status: {r.status_code}")
except Exception as e:
    print(f"Error: {e}")

print("\nReading debug log...")
with open(r"c:\Users\valaboph\AIAutomation\debug_field_aware.txt", 'r') as f:
    print(f.read())
