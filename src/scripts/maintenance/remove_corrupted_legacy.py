"""Remove the corrupted legacy method by line numbers"""

with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"Original: {len(lines)} lines")

# Remove lines 801-1078 (0-indexed: 800-1077) - the corrupted _java_to_python_by_REMOVED_SECTION method
# Keep the comment on line 800 and jump to the real _java_to_python_by on line 1079
new_lines = lines[:801] + lines[1079:]

with open('src/main/python/inference_improved.py', 'w', encoding='utf-8') as f:
    f.writelines(new_lines)

print(f"New: {len(new_lines)} lines")
print(f"Removed: {len(lines) - len(new_lines)} lines")
