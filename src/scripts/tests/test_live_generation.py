# Test script to verify path generation
import sys
sys.path.insert(0, 'src/main/python')

# Import WITHOUT cache
import importlib
from test_management import test_case_builder
importlib.reload(test_case_builder)

from test_management.test_case_builder import TestCaseBuilder

# Create test
builder = TestCaseBuilder()
session_data = {
    'name': 'LiveTest',
    'description': 'Test right now',
    'prompts': [{
        'step': 1,
        'prompt': 'click button',
        'generated_code': 'driver.find_element(By.ID, "test").click()'
    }]
}

test_case = builder.build_from_session(session_data, test_case_id='LIVE001', languages=['python'])
code = test_case.generated_code.get('python', '')

# Find the script_dir line
for i, line in enumerate(code.split('\n'), 1):
    if 'script_dir' in line:
        print(f"\n{'='*70}")
        print(f"Line {i}: {line.strip()}")
        if 'os.path.dirname(os.path.abspath(__file__))' in line:
            print("✅ CORRECT - Using dynamic path!")
        elif '..\python' in line or '..\\python' in line:
            print("❌ WRONG - Using old hardcoded path!")
        print('='*70)
        break
