"""Aggressive cleanup: Remove excessive blank lines and verbose comments"""
import re

with open('src/main/python/inference_improved.py', 'r', encoding='utf-8') as f:
    lines = f.readlines()

print(f"📊 Original: {len(lines)} lines")

# Clean up excessive blank lines (max 1 consecutive)
cleaned = []
prev_blank = False
for line in lines:
    is_blank = line.strip() == ''
    
    # Skip if this is a blank line and previous was also blank
    if is_blank and prev_blank:
        continue
    
    cleaned.append(line)
    prev_blank = is_blank

print(f"�� After removing excessive blank lines: {len(cleaned)} lines")

# Remove specific verbose/outdated comment lines
patterns_to_remove = [
    r'^\s*# REMOVED:.*$\n',  # Remove "# REMOVED:" markers
    r'^\s*# Legacy.*$\n',    # Remove "# Legacy" markers  
    r'^\s*# REFACTORED.*$\n',  # Remove "# REFACTORED" markers
]

content = ''.join(cleaned)
for pattern in patterns_to_remove:
    content = re.sub(pattern, '', content, flags=re.MULTILINE)

final_lines = content.split('\n')
print(f"✅ After removing marker comments: {len(final_lines)} lines")

# Write back
with open('src/main/python/inference_improved.py', 'w', encoding='utf-8', newline='\n') as f:
    f.write(content)

removed = len(lines) - len(final_lines)
print(f"\n🎯 Total removed: {removed} lines ({removed/len(lines)*100:.1f}%)")
print(f"📊 Final size: {len(final_lines)} lines")
