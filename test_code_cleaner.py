"""Test the code cleaner to see what it's actually producing"""
import sys
import re
sys.path.insert(0, 'src/main/python')

# Sample generated code with fixture function
SAMPLE_CODE = '''"""
Semantic Variant: negative
Generated: 2026-04-07T16:48:44.649469
"""

import pytest
from selenium import webdriver

@pytest.fixture
def driver(request):
    browser = request.config.getoption("--browser", default="chrome")
    if browser.lower() == "firefox":
        driver = webdriver.Firefox()
    else:
        driver = webdriver.Chrome()
    yield driver
    driver.quit()

@pytest.mark.test
def test_logintestretest(driver):
    """Test: Invalid Input Testing"""
    driver.get("https://platform.sircontest.non-prod.sircon.com/")
    element = driver.find_element(By.CSS_SELECTOR, "input[id='producer-email']")
    element.send_keys("test@test.com")
'''

def clean_code_for_execution(code: str) -> str:
    """Simplified version of the cleaning logic"""
    import re
    
    lines = code.split('\n')
    cleaned_lines = []
    skip_lines = 0 
    skip_mode = None
    in_docstring = False
    docstring_delimiter = None
    
    for i, line in enumerate(lines):
        stripped = line.strip()
        
        # Handle multi-line docstrings
        if not in_docstring:
            if stripped.startswith('"""'):
                in_docstring = True
                docstring_delimiter = '"""'
                if stripped.count('"""') >= 2 and len(stripped) > 6:
                    in_docstring = False
                continue
            elif stripped.startswith("'''"):
                in_docstring = True
                docstring_delimiter = "'''"
                if stripped.count("'''") >= 2 and len(stripped) > 6:
                    in_docstring = False
                continue
        else:
            if docstring_delimiter in stripped:
                in_docstring = False
                docstring_delimiter = None
            continue
        
        # If we're skipping lines (inside a function)
        if skip_lines > 0:
            if re.match(r'^\S', line) and line.strip():
                skip_lines = 0
                skip_mode = None
            else:
                skip_lines -= 1
                if skip_mode == 'extract_body' and line.strip():
                    dedented = line[4:] if len(line) > 4 else line.lstrip()
                    cleaned_lines.append(dedented)
                continue
        
        # Skip empty lines and comments
        if not stripped or stripped.startswith('#'):
            continue
        
        # Remove pytest/unittest lines
        if 'pytest' in stripped or 'unittest' in stripped:
            print(f"  [SKIP pytest] {stripped[:60]}")
            continue
        
        # Remove selenium imports
        if re.match(r'^\s*from\s+selenium', stripped) or \
           re.match(r'^\s*import\s+selenium', stripped):
            print(f"  [SKIP import] {stripped[:60]}")
            continue
        
        # Remove decorators
        if stripped.startswith('@'):
            print(f"  [SKIP decorator] {stripped[:60]}")
            continue
        
        # Detect fixture function - skip ENTIRELY
        if re.match(r'^\s*def\s+\w+.*driver.*request', stripped) or \
           re.match(r'^\s*def\s+driver\s*\(', stripped):
            print(f"  [SKIP FIXTURE ENTIRELY] {stripped[:60]}")
            skip_lines = 99999
            skip_mode = 'skip_entirely'
            continue
        
        # Detect test function - extract body
        if re.match(r'^\s*def\s+(test_|setup_|teardown_)', stripped):
            print(f"  [EXTRACT BODY] {stripped[:60]}")
            skip_lines = 99999
            skip_mode = 'extract_body'
            continue
        
        # Keep this line
        cleaned_lines.append(line)
    
    return '\n'.join(cleaned_lines)

if __name__ == '__main__':
    print("="*70)
    print("ORIGINAL CODE:")
    print("="*70)
    print(SAMPLE_CODE)
    print("\n" + "="*70)
    print("CLEANING PROCESS:")
    print("="*70)
    
    cleaned = clean_code_for_execution(SAMPLE_CODE)
    
    print("\n" + "="*70)
    print("CLEANED CODE:")
    print("="*70)
    print(cleaned)
    print("\n" + "="*70)
    
    # Check if 'def driver' appears in cleaned code
    if 'def driver' in cleaned:
        print("❌ ERROR: Fixture function 'def driver' found in cleaned code!")
    else:
        print("✅ SUCCESS: Fixture function removed!")
    
    if 'yield driver' in cleaned:
        print("❌ ERROR: Fixture body 'yield driver' found in cleaned code!")
    else:
        print("✅ SUCCESS: Fixture body not in cleaned code!")
    
    print("="*70)
