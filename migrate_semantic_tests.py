"""
Migrate existing semantic tests from pytest format to execution-ready format.
This updates all semantic test JSON files to have code without pytest fixtures.

⚠️ ONE-TIME UTILITY SCRIPT ⚠️
This is NOT part of the production runtime system. It's a batch migration tool
for fixing OLD tests that were saved before the execution_ready fix was implemented.

New semantic tests generate correctly from source (test_case_builder.py) and don't need this.

Usage: python migrate_semantic_tests.py
"""
import json
import glob
import re
from pathlib import Path

def extract_execution_ready_code(pytest_code):
    """Extract test body from pytest code, removing fixtures and decorators."""
    if not pytest_code or not isinstance(pytest_code, str):
        return pytest_code
    
    lines = pytest_code.split('\n')
    cleaned_lines = []
    skip_mode = None
    skip_lines = 0
    
    for line in lines:
        stripped = line.strip()
        
        # Skip if we're in skip mode
        if skip_lines > 0:
            # Check if back to column 0 (end of function)
            if re.match(r'^\S', line) and stripped:
                skip_lines = 0
                skip_mode = None
            else:
                skip_lines -= 1
                # If in extract mode, get the dedented line
                if skip_mode == 'extract' and stripped:
                    dedented = line[4:] if len(line) > 4 else line.lstrip()
                    cleaned_lines.append(dedented)
                continue
        
        # Skip docstrings, imports, comments
        if (stripped.startswith('"""') or stripped.startswith("'''") or
            stripped.startswith('import ') or stripped.startswith('from ') or
            (stripped.startswith('#') and not 'driver.get' in stripped)):
            continue
        
        # Skip decorators
        if stripped.startswith('@'):
            continue
        
        # Detect fixture function - skip entirely
        if 'def driver(' in stripped or ('def ' in stripped and 'request' in stripped):
            skip_lines = 99999
            skip_mode = 'skip'
            continue
        
        # Detect test function - extract body
        if stripped.startswith('def test_'):
            skip_lines = 99999
            skip_mode = 'extract'
            continue
        
        # Skip empty lines at start
        if not cleaned_lines and not stripped:
            continue
        
        # Keep non-empty lines if not in a function yet
        if stripped and skip_mode is None:
            cleaned_lines.append(line)
    
    if cleaned_lines:
        # Add header
        header = ['# Execution-ready code (no pytest fixtures)', '']
        return '\n'.join(header + cleaned_lines)
    else:
        return None

def migrate_test_file(json_path):
    """Migrate a single test JSON file."""
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            test_data = json.load(f)
        
        # Check if it's a semantic test
        if test_data.get('generated_by') != 'semantic-analysis':
            return False, "Not a semantic test"
        
        # Check if it has pytest code
        python_code = test_data.get('generated_code', {}).get('python', '')
        if not python_code or '@pytest.fixture' not in python_code:
            return False, "Already migrated or no pytest code"
        
        # Extract execution-ready code
        new_code = extract_execution_ready_code(python_code)
        
        if new_code and len(new_code) > 50:  # Sanity check
            test_data['generated_code']['python'] = new_code
            
            # Write back
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(test_data, f, indent=2, ensure_ascii=False)
            
            return True, f"Migrated: {len(python_code)} → {len(new_code)} chars"
        else:
            return False, "Migration produced empty code"
            
    except Exception as e:
        return False, f"Error: {str(e)}"

def main():
    # Find all semantic test JSON files
    test_patterns = [
        'test_suites/**/builder/*.json',
        'test_suites/**/recorded/*.json'
    ]
    
    all_files = []
    for pattern in test_patterns:
        all_files.extend(glob.glob(pattern, recursive=True))
    
    print(f"Found {len(all_files)} test files")
    print("=" * 60)
    
    migrated = 0
    skipped = 0
    errors = 0
    
    for json_path in all_files:
        success, message = migrate_test_file(json_path)
        
        if success:
            migrated += 1
            print(f"✓ {Path(json_path).name}: {message}")
        else:
            if "Not a semantic test" not in message and "Already migrated" not in message:
                errors += 1
                print(f"✗ {Path(json_path).name}: {message}")
            else:
                skipped += 1
    
    print("=" * 60)
    print(f"✓ Migrated: {migrated}")
    print(f"⊘ Skipped: {skipped}")
    print(f"✗ Errors: {errors}")
    print(f"Total: {len(all_files)}")

if __name__ == '__main__':
    main()
