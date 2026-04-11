#!/usr/bin/env python3
"""Fix extra closing parentheses in dataset code blocks"""
import json

# Load dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

fixed_count = 0

for entry in data:
    if 'code' in entry and entry['code']:
        original_code = entry['code']
        
        # Simple fix: Replace ))))\n with )))\n (extra closing paren before newline)
        fixed_code = original_code.replace('))))\n', ')))\n')
        
        # Also check end of string
        if fixed_code.endswith('))))'):
            fixed_code = fixed_code[:-4] + ')'
        
        if fixed_code != original_code:
            entry['code'] = fixed_code
            fixed_count += 1
            prompt = entry.get('prompt', 'Unknown')
            # Truncate with ... if too long
            display_prompt = prompt if len(prompt) <= 60 else prompt[:57] + '...'
            print(f"✓ Fixed: {display_prompt}")

# Save fixed dataset
with open('src/resources/combined-training-dataset-final.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, indent=2, ensure_ascii=False)

print(f"\n✅ Fixed {fixed_count} entries with extra parentheses")
