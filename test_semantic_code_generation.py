"""
Test the execution-ready code generation for semantic tests
"""
import requests
import json

API_URL = "http://localhost:5003"

# Create a semantic variant test data
semantic_test = {
    "test_case_id": "TC001_variant_boundary_test",
    "name": "Boundary Testing",
    "description": "Test with boundary values",
    "url": "https://www.sircontest.non-prod.sircon.com/login.jsp",
    "test_type": "regression",
    "source": "builder",
    "parent_test_case_id": "TC001",
    "generated_by": "semantic-analysis",
    "variant_type": "boundary",
    "tags": ["semantic", "boundary"],
    "priority": "high",
    "prompts": [
        {
            "step": 1,
            "prompt": "enter text in email field",
            "value": "x@y.z",  # Minimal email (boundary)
            "description": "Boundary: minimal valid email"
        },
        {
            "step": 2,
            "prompt": "enter text in password field",
            "value": "12345678",  # Minimal 8 chars (boundary)
            "description": "Boundary: minimum password length"
        },
        {
            "step": 3,
            "prompt": "click login button",
            "value": None,
            "description": "Click login"
        }
    ],
    "actions": [
        {
            "prompt": "enter text in email field",
            "type": "action",
            "value": "x@y.z",
            "description": "Boundary: minimal valid email"
        },
        {
            "prompt": "enter text in password field",
            "type": "action",
            "value": "12345678",
            "description": "Boundary: minimum password length"
        },
        {
            "prompt": "click login button",
            "type": "action",
            "value": None,
            "description": "Click login"
        }
    ]
}

print("Creating semantic test variant...")
print(f"Test ID: {semantic_test['test_case_id']}")
print(f"Parent: {semantic_test['parent_test_case_id']}")
print(f"Steps: {len(semantic_test['prompts'])}")

# Save the test using the semantic save endpoint
response = requests.post(
    f"{API_URL}/semantic/save-generated-tests",
    json={
        "tests": [semantic_test],
        "test_type": "regression"
    },
    headers={"Content-Type": "application/json"}
)

print(f"\nResponse Status: {response.status_code}")
result = response.json()
print(f"Response: {json.dumps(result, indent=2)}")
print(f"Success: {result.get('success')}")

if result.get('success'):
    # Check for saved tests
    saved_tests = result.get('saved_tests', [])
    print(f"Saved tests: {len(saved_tests)}")
    
    if saved_tests:
        test_info = saved_tests[0]
        print(f"Test ID: {test_info.get('test_case_id')}")
        print(f"File: {test_info.get('file_path')}")
    
    # Read the generated code
    import pathlib
    file_path = result.get('file_path')
    if file_path:
        json_file = pathlib.Path(file_path)
        if json_file.exists():
            with open(json_file, 'r', encoding='utf-8') as f:
                saved_test = json.load(f)
            
            python_code = saved_test.get('generated_code', {}).get('python', '')
            print("\n" + "=" * 70)
            print("GENERATED PYTHON CODE:")
            print("=" * 70)
            print(python_code[:1000])  # First 1000 chars
            print("..." if len(python_code) > 1000 else "")
            print("=" * 70)
            
            # Check if it's just pass statements
            if python_code.count('pass') > 2 and 'driver.' not in python_code:
                print("\n❌ FAIL: Code contains only 'pass' statements!")
            else:
                print("\n✓ PASS: Code contains actual Selenium commands!")
else:
    print(f"Error: {result.get('error')}")
    print(f"Details: {result.get('details')}")
