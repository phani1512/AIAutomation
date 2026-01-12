import json

# Load sircon dataset
with open('src/resources/sircon_ui_dataset.json') as f:
    data = json.load(f)

# Search for producer-login related prompts
matches = []
for entry in data:
    for step in entry.get('steps', []):
        prompt = step.get('prompt', '').lower()
        if 'producer' in prompt and 'login' in prompt:
            matches.append({
                'action': entry.get('action'),
                'prompt': step.get('prompt'),
                'locator': step.get('locator'),
                'code': step.get('code', '')[:100]
            })

print(f'Found {len(matches)} matches for producer + login:\n')
for i, m in enumerate(matches[:5], 1):
    print(f"{i}. Prompt: {m['prompt']}")
    print(f"   Locator: {m['locator']}")
    print(f"   Code: {m['code']}")
    print()
