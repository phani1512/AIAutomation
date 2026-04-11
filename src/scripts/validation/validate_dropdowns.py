import json

# Load and validate dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f'✅ Valid JSON: {len(data)} total entries')

# Count dropdown entries
dropdown_entries = [e for e in data if e.get('category') == 'dropdown']
print(f'📋 Dropdown entries: {len(dropdown_entries)}')

# Show dropdown locator strategies
print('\n🎯 Dropdown locator strategies:')
for entry in dropdown_entries[:15]:  # Show first 15
    prompt = entry.get('prompt', '')[:60]
    xpath = entry.get('xpath', '')
    locator_type = 'ID' if 'By.id' in xpath else 'NAME' if 'By.name' in xpath else 'XPATH' if 'By.xpath' in xpath else 'CSS' if 'By.cssSelector' in xpath else 'OTHER'
    print(f'  {locator_type:8} | {prompt}')

print(f'\n✅ Dataset ready for server restart')
