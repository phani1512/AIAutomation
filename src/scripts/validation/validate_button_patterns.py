import json

# Load and validate dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'✅ Valid JSON: {len(data)} total entries')

# Count different entry types
dropdown_entries = [e for e in data if e.get('category') == 'dropdown']
click_entries = [e for e in data if e.get('category') == 'click']
button_text_entries = [e for e in data if 'xpath_text_contains' in str(e.get('metadata', {}).get('locator_strategy', ''))]

print(f'📋 Dropdown entries: {len(dropdown_entries)}')
print(f'🖱️ Click entries: {len(click_entries)}')
print(f'🔘 Button-by-text entries: {len(button_text_entries)}')

print('\n🎯 New Button-by-Text Pattern Entries:')
for entry in button_text_entries[:10]:  # Show first 10
    prompt = entry.get('prompt', '')[:60]
    xpath = entry.get('xpath', '')
    is_universal = entry.get('metadata', {}).get('is_universal', False)
    universal_mark = ' [UNIVERSAL]' if is_universal else ''
    print(f'  {prompt}{universal_mark}')
    print(f'    XPath: {xpath[:80]}')

print(f'\n✅ Dataset ready with button-by-text patterns!')
print(f'✅ Total entries: {len(data)}')
