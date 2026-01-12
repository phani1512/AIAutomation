import json

with open('src/resources/sircon_ui_dataset.json') as f:
    data = json.load(f)

# Find "click on" prompts
click_on_prompts = []
for entry in data:
    for step in entry.get('steps', []):
        prompt = step.get('prompt', '')
        if prompt.startswith('click on'):
            click_on_prompts.append({
                'prompt': prompt,
                'locator': step.get('locator', ''),
                'code': step.get('code', '')[:150]
            })

print(f"Found {len(click_on_prompts)} 'click on' prompts\n")
for i, p in enumerate(click_on_prompts[:10], 1):
    print(f"{i}. {p['prompt']}")
    print(f"   Locator: {p['locator']}")
    print()
