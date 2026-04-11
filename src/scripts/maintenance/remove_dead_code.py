#!/usr/bin/env python3
"""Remove orphaned dead code from inference_improved.py"""

file_path = r'c:\Users\valaboph\AIAutomation\src\main\python\inference_improved.py'

# Read the file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original file: {len(lines)} lines")
print(f"Line 599 (last valid line): {lines[598].rstrip()}")
print(f"Line 600 (first orphaned): {lines[599].rstrip()}")
print(f"Line 892 (last orphaned): {lines[891].rstrip()}")
print(f"Line 893 (clean_output): {lines[892].rstrip()}")

# Remove lines 600-892 (indices 599-891, inclusive)
# Keep lines 0-599 (indices 0-598) and 893+ (indices 892+)
new_lines = lines[:599] + lines[892:]

print(f"\nLines removed: {892 - 599} = {len(lines) - len(new_lines)} lines")
print(f"New file: {len(new_lines)} lines")

# Write back
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("\n✅ File updated successfully")
print(f"Removed orphaned dead code (lines 600-892)")
