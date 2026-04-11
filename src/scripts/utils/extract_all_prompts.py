import json

# Extract all unique prompts from all datasets
datasets = {
    'Common Web Actions': 'src/resources/common-web-actions-dataset.json',
    'Selenium Methods': 'src/resources/selenium-methods-dataset.json',
    'Element Locators': 'src/resources/element-locator-patterns.json',
    'Sircon UI': 'src/resources/sircon_ui_dataset.json'
}

all_prompts = {}

# Common Web Actions
with open(datasets['Common Web Actions']) as f:
    data = json.load(f)
    prompts = []
    for entry in data:
        for step in entry['steps']:
            if 'prompt' in step:
                prompts.append(step['prompt'])
    all_prompts['Common Web Actions'] = sorted(set(prompts))

# Selenium Methods
with open(datasets['Selenium Methods']) as f:
    data = json.load(f)
    prompts = [e['method'] for e in data if 'method' in e]
    all_prompts['Selenium Methods'] = sorted(set(prompts))

# Element Locators
with open(datasets['Element Locators']) as f:
    data = json.load(f)
    prompts = [f"{e.get('locator_type', '')} - {e.get('description', '')}" for e in data]
    all_prompts['Element Locators'] = sorted(set(prompts))

# Sircon UI
with open(datasets['Sircon UI']) as f:
    data = json.load(f)
    prompts = set()
    for entry in data:
        for step in entry.get('steps', []):
            if 'prompt' in step:
                prompts.add(step['prompt'])
    all_prompts['Sircon UI'] = sorted(prompts)

print('Dataset Summary:')
for name, prompts in all_prompts.items():
    print(f'{name}: {len(prompts)} unique prompts')

# Save to file
output = '# ALL DATASETS - COMPLETE PROMPTS REFERENCE\n\n'
output += f'**Generated:** November 27, 2025\n'
output += f'**Total Datasets:** 4\n'
output += f'**Total Prompts:** {sum(len(p) for p in all_prompts.values())}\n\n'
output += '---\n\n'
output += '## Quick Statistics\n\n'
output += '| Dataset | Prompts | Type |\n'
output += '|---------|---------|------|\n'

for dataset_name, prompts in all_prompts.items():
    prompt_type = 'UI Prompts' if 'Web Actions' in dataset_name or 'Sircon' in dataset_name else 'API Patterns'
    output += f'| {dataset_name} | {len(prompts)} | {prompt_type} |\n'

output += '\n---\n\n'

for dataset_name, prompts in all_prompts.items():
    output += f'## {dataset_name} ({len(prompts)} Prompts)\n\n'
    for i, prompt in enumerate(prompts, 1):
        output += f'{i}. `{prompt}`\n'
    output += '\n---\n\n'

with open('ALL_DATASETS_PROMPTS_COMPLETE.md', 'w', encoding='utf-8') as f:
    f.write(output)

print(f'\n✅ Created: ALL_DATASETS_PROMPTS_COMPLETE.md')
print(f'Total prompts: {sum(len(p) for p in all_prompts.values())}')
