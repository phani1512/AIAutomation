#!/usr/bin/env python3
import json
import re

with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print('BROKEN/INCOMPLETE CODE PATTERNS')
print('=' * 70)

issues = {
    'incomplete_try': 0,
    'helper_methods': 0,
    'list_loops': 0,
    'empty_code': 0,
    'very_short': 0  # Less than 50 chars
}

examples = []

for i, entry in enumerate(dataset):
    code = entry.get('code', '').strip()
    prompt = entry.get('prompt', '')
    
    if not code:
        issues['empty_code'] += 1
        if len(examples) < 10:
            examples.append((prompt, 'EMPTY CODE'))
        continue
    
    # Incomplete try block
    if code == 'try {' or code.startswith('try {') and len(code) < 20:
        issues['incomplete_try'] += 1
        if len(examples) < 10:
            examples.append((prompt, f'INCOMPLETE TRY: {code}'))
        continue
    
    # Helper method calls
    if 'getDropDownList' in code or ('findElements(' in code and 'for' in code):
        issues['helper_methods'] += 1
        if len(examples) < 10:
            examples.append((prompt, f'HELPER CALL: {code[:60]}...'))
        continue
    
    # List/loop without WebDriver setup
    if code.startswith('List<') and 'WebDriverWait' not in code:
        issues['list_loops'] += 1
        if len(examples) < 10:
            examples.append((prompt, f'LIST NO SETUP: {code[:60]}...'))
        continue
    
    # Very short code (likely incomplete)
    if len(code) < 50 and 'WebElement' not in code:
        issues['very_short'] += 1
        if len(examples) < 10:
            examples.append((prompt, f'TOO SHORT: {code}'))

print()
for issue_type, count in issues.items():
    print(f'{count:4d} entries with {issue_type}')

print()
print('=' * 70)
print('EXAMPLES:')
print('=' * 70)
for i, (prompt, issue) in enumerate(examples[:10], 1):
    print(f'\n{i}. Prompt: {prompt[:60]}')
    print(f'   Issue: {issue}')

print()
print('=' * 70)
print(f'TOTAL BROKEN: {sum(issues.values())} entries')
print('=' * 70)
