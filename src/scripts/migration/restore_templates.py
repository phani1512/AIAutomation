import json
from datetime import datetime

# Load current dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    current_dataset = json.load(f)

# Load backup with template entries
backup_file = 'src/resources/combined-training-dataset-final.json.backup_20260318_192046'
with open(backup_file, 'r', encoding='utf-8') as f:
    backup_dataset = json.load(f)

print("RESTORING TEMPLATE ENTRIES FOR HYBRID APPROACH")
print("=" * 70)

# Find removed entries (templates)
current_prompts = {e['prompt'] for e in current_dataset}
template_entries = [e for e in backup_dataset if e['prompt'] not in current_prompts]

print(f"\n📊 Current dataset: {len(current_dataset)} concrete entries")
print(f"📋 Template entries to restore: {len(template_entries)}")
print(f"📈 Final dataset size: {len(current_dataset) + len(template_entries)}")

# Add metadata to distinguish templates from concrete examples
for entry in template_entries:
    if 'metadata' not in entry:
        entry['metadata'] = {}
    entry['metadata']['entry_type'] = 'template'
    entry['metadata']['usage'] = 'parameter_substitution'

# Add metadata to concrete examples
for entry in current_dataset:
    if 'metadata' not in entry:
        entry['metadata'] = {}
    if 'entry_type' not in entry['metadata']:
        entry['metadata']['entry_type'] = 'concrete'
    if 'usage' not in entry['metadata']:
        entry['metadata']['usage'] = 'ml_training'

# Combine datasets
hybrid_dataset = current_dataset + template_entries

# Show what's being restored
print("\n" + "=" * 70)
print("RESTORED TEMPLATE PATTERNS:")
print("=" * 70)

import re
template_categories = {}
for entry in template_entries:
    prompt = entry['prompt']
    # Extract placeholder types
    placeholders = re.findall(r'\{([a-zA-Z_]+)\}', prompt)
    if placeholders:
        category = placeholders[0]
        if category not in template_categories:
            template_categories[category] = []
        template_categories[category].append(prompt)

for category, prompts in sorted(template_categories.items(), key=lambda x: len(x[1]), reverse=True):
    print(f"\n{category.upper()} Templates ({len(prompts)}):")
    for p in prompts[:3]:
        print(f"  ✅ {p}")
    if len(prompts) > 3:
        print(f"  ... and {len(prompts) - 3} more")

# Backup current before restoring
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_concrete = f'src/resources/combined-training-dataset-final.json.backup_concrete_only_{timestamp}'
with open(backup_concrete, 'w', encoding='utf-8') as f:
    json.dump(current_dataset, f, indent=2)

# Save hybrid dataset
with open('src/resources/combined-training-dataset-final.json', 'w', encoding='utf-8') as f:
    json.dump(hybrid_dataset, f, indent=2)

print("\n" + "=" * 70)
print("✅ HYBRID DATASET CREATED!")
print("=" * 70)
print(f"✅ Concrete examples: {len(current_dataset)} (for ML training)")
print(f"✅ Template patterns: {len(template_entries)} (for parameter substitution)")
print(f"✅ Total entries: {len(hybrid_dataset)}")
print(f"✅ Backup (concrete only): {backup_concrete}")
print(f"✅ Dataset saved: src/resources/combined-training-dataset-final.json")
print("=" * 70)

print("\n📋 USAGE GUIDE:")
print("""
RUNTIME LOGIC (Recommended Implementation):

1. Template Matching (First Priority):
   - Check if prompt matches template pattern
   - Extract parameters from prompt
   - Substitute into template code
   - Return generated code immediately
   
2. ML Model (Fallback):
   - If no template match, use ML model
   - Model trained on concrete examples
   - Generates code based on learned patterns
   
3. Self-Healing (Last Resort):
   - If ML fails or element not found
   - Use vision/semantic analysis
   - Find element by appearance/context

EXAMPLE:
  User: "click the SignOut button"
  
  Step 1: Template match?
    → Pattern: "click {button}" → MATCH!
    → Extract: button="SignOut"  
    → Generate: By.xpath("//button[text()='SignOut']")
    → SUCCESS ✅
    
  User: "click the button in the top right corner"
  
  Step 1: Template match? → NO MATCH
  Step 2: ML Model → Generates locator based on training
  Step 3: Self-healing → Vision finds button by location
""")

print("\n🎉 HYBRID APPROACH READY! Best of both worlds! 🎉")
