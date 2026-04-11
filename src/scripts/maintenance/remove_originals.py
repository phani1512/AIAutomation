"""Script to remove all _ORIGINAL backup functions from code_generator.py"""
import re

def remove_original_functions(filepath):
    with open(filepath, 'r', encoding='utf-8') as f:
        lines = f.readlines()
    
    cleaned_lines = []
    in_original_block = False
    skip_line_count = 0
    
    for i, line in enumerate(lines):
        # Check if we're starting an _ORIGINAL function
        if '_ORIGINAL' in line and 'def ' in line:
            in_original_block = True
            print(f"Found _ORIGINAL function at line {i+1}: {line.strip()}")
            continue
        
        # Check if we're exiting an _ORIGINAL block (found next regular function)
        if in_original_block and line.startswith('def ') and '_ORIGINAL' not in line:
            in_original_block = False
            skip_line_count += 1
            print(f"Exiting _ORIGINAL block at line {i+1}, found: {line.strip()}")
        
        # Only keep lines not in _ORIGINAL blocks
        if not in_original_block:
            cleaned_lines.append(line)
        else:
            skip_line_count += 1
    
    print(f"\nTotal lines removed: {skip_line_count}")
    print(f"Original lines: {len(lines)}")
    print(f"Cleaned lines: {len(cleaned_lines)}")
    
    # Write cleaned file
    with open(filepath, 'w', encoding='utf-8') as f:
        f.writelines(cleaned_lines)
    
    print(f"\n✓ Successfully cleaned {filepath}")

if __name__ == '__main__':
    remove_original_functions('src/main/python/code_generator.py')
