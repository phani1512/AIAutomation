import json

print("=== Dataset Structure Validation ===\n")

# Load dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Total entries: {len(dataset)}\n")

# Check the structure of a few key entries
test_prompts = [
    "wait for loading spinner to disappear",
    "wait for page to finish loading",
    "click submit button",
    "wait for dialog to open",
    "get success toast message text"
]

print("=== Checking Key Entries ===\n")
for prompt_text in test_prompts:
    entry = next((e for e in dataset if e.get('prompt', '').lower() == prompt_text.lower()), None)
    if entry:
        print(f"✅ Prompt: \"{prompt_text}\"")
        print(f"   Category: {entry.get('category', 'N/A')}")
        print(f"   Has code: {bool(entry.get('code', '').strip())}")
        code = entry.get('code', '')
        print(f"   Code length: {len(code)} chars")
        print(f"   Code preview: {code[:100]}...")
        print(f"   Has xpath: {bool(entry.get('xpath', '').strip())}")
        print()
    else:
        print(f"❌ Prompt: \"{prompt_text}\" - NOT FOUND")
        print()

# Check if all entries have required fields
print("\n=== Field Coverage ===")
missing_code = [e for e in dataset if not e.get('code', '').strip()]
missing_prompt = [e for e in dataset if not e.get('prompt', '').strip()]
missing_category = [e for e in dataset if not e.get('category', '').strip()]

print(f"Entries missing code: {len(missing_code)}")
print(f"Entries missing prompt: {len(missing_prompt)}")
print(f"Entries missing category: {len(missing_category)}")

# Check for problematic entries (code too short or generic)
generic_patterns = ['elementId', 'Element element', 'driver.findElement']
problematic = []

for i, entry in enumerate(dataset):
    code = entry.get('code', '')
    # Check if code is too short
    if len(code) < 50:
        problematic.append({
            'index': i,
            'prompt': entry.get('prompt', ''),
            'issue': f'Code too short ({len(code)} chars)',
            'code': code
        })
    # Check if code contains generic placeholders that might confuse inference
    elif any(pattern in code for pattern in ['elementId', 'Element element = driver.findElement']):
        if 'wait for' not in entry.get('prompt', '').lower():
            problematic.append({
                'index': i,
                'prompt': entry.get('prompt', ''),
                'issue': 'Contains generic placeholder',
                'code': code[:100]
            })

print(f"\n=== Potentially Problematic Entries: {len(problematic)} ===")
for item in problematic[:10]:
    print(f"\nPrompt: {item['prompt']}")
    print(f"Issue: {item['issue']}")
    print(f"Code: {item['code'][:80]}...")

# Check dataset format
print("\n=== Dataset Format ===")
print(f"Type: {type(dataset)}")
print(f"Is list: {isinstance(dataset, list)}")
if isinstance(dataset, list) and len(dataset) > 0:
    print(f"First entry type: {type(dataset[0])}")
    print(f"First entry keys: {list(dataset[0].keys())}")
    
# Show a complete sample entry
print("\n=== Sample Complete Entry ===")
sample = dataset[0]
print(json.dumps(sample, indent=2)[:500] + "...")

print("\n" + "="*60)
print("RECOMMENDATION FOR INFERENCE ENGINE:")
print("="*60)
print("Your inference system should:")
print("1. Load this JSON file as a list of dictionaries")
print("2. Match user prompt against 'prompt' field (fuzzy match)")
print("3. Return the 'code' field directly")
print("4. Replace placeholders like {BUTTON_TEXT}, {FIELD}, etc.")
print("5. NOT use default templates - use actual code from dataset")
print("="*60)
