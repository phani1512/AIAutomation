"""Remove orphaned code from inference_improved.py"""
import sys

# Read the file
with open(r'c:\Users\valaboph\AIAutomation\src\main\python\inference_improved.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Total lines before: {len(lines)}")
print(f"Removing lines 787-1082 (orphaned code with duplicates)")

# Keep lines before 787 and after 1082 (0-based indexing, so 0-786 and 1082+)
new_lines = lines[:786] + lines[1082:]

print(f"Total lines after: {len(new_lines)}")
print(f"Removed {len(lines) - len(new_lines)} lines")

# Write back
with open(r'c:\Users\valaboph\AIAutomation\src\main\python\inference_improved.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print("✅ Orphaned code removed successfully!")
print("\nPreview of lines around the deletion point:")
print("".join(new_lines[780:795]))
