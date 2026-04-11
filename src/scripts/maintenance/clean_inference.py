"""
Script to clean up inference_improved.py by removing orphaned code blocks
"""
import re

# Read the file
with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Find line numbers
enhance_method_end = None
first_convert_start = None
second_convert_start = None

for i, line in enumerate(lines):
    if 'print(f"[COMPREHENSIVE] ✅ Generated comprehensive code' in line:
        # Found end of _enhance_dataset_code_comprehensive
        enhance_method_end = i + 1  # Line after return statement
    elif '_convert_code_to_language' in line and 'def ' in line:
        if first_convert_start is None:
            first_convert_start = i
        elif second_convert_start is None:
            second_convert_start = i

print(f"Enhance method ends at line: {enhance_method_end}")
print(f"First _convert_code_to_language at line: {first_convert_start}")
print(f"Second _convert_code_to_language at line: {second_convert_start}")

# Check if we found the problematic section
if enhance_method_end and first_convert_start and second_convert_start:
    print(f"\n✅ Will remove lines {first_convert_start} to {second_convert_start-1}")
    print(f"That's {second_convert_start - first_convert_start} lines of orphaned code")
    
    # Create clean version
    clean_lines = lines[:first_convert_start] + lines[second_convert_start:]
    
    # Write clean file
    with open('src/main/python/inference_improved_clean.py', 'w', encoding='utf-8') as f:
        f.writelines(clean_lines)
    
    print(f"\n✅ Clean file written to: inference_improved_clean.py")
    print(f"Original: {len(lines)} lines")
    print(f"Clean: {len(clean_lines)} lines")
    print(f"Removed: {len(lines) - len(clean_lines)} lines")
else:
    print("❌ Could not locate all required sections")
