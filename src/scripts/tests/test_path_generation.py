import sys
sys.path.insert(0, 'src/main/python')

from test_management.test_case_builder import TestCaseBuilder

# Create a simple test builder
builder = TestCaseBuilder("TestPath", [
    {"action": "click", "locator": "#login", "generated_code": "driver.find_element(By.CSS_SELECTOR, '#login').click()"}
])

# Generate Python code
code = builder.generate_pytest_code()

# Check for the path line
lines = code.split('\n')
for i, line in enumerate(lines, 1):
    if 'script_dir' in line:
        print(f"\nLine {i}: {line.strip()}")
        if 'os.path.dirname(os.path.abspath(__file__))' in line:
            print("✅ CORRECT - Using dynamic path")
        elif '..\python' in line or '..\\python' in line:
            print("❌ WRONG - Using old hardcoded path")
        break
