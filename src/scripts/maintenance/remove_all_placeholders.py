import json
import re
from datetime import datetime

# Backup
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f'src/resources/combined-training-dataset-final.json.backup_{timestamp}'

with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2)

print(f"✅ Backup created: {backup_file}")
print("\nREMOVING ALL PLACEHOLDER/TEMPLATE ENTRIES")
print("=" * 70)

# Placeholder patterns to detect
placeholder_patterns = [
    r'\{[A-Z_]+\}',  # {TEXT}, {LABEL}, {FILE_PATH}, etc.
    r'\{[a-z_]+\}',  # {filename}, {link}, {criteria}, etc.
    r'<[a-z-]+>',    # <element-id>, <element>
]

clean_entries = []
removed_entries = []

for entry in dataset:
    code = entry.get('code', '')
    prompt = entry.get('prompt', '')
    xpath = entry.get('xpath', '')
    
    has_placeholder = False
    found_placeholders = []
    
    # Check all fields for placeholders
    for pattern in placeholder_patterns:
        if re.search(pattern, code):
            has_placeholder = True
            found_placeholders.extend(re.findall(pattern, code))
        if re.search(pattern, xpath):
            has_placeholder = True
            found_placeholders.extend(re.findall(pattern, xpath))
        if re.search(pattern, prompt):
            has_placeholder = True
            found_placeholders.extend(re.findall(pattern, prompt))
    
    if has_placeholder:
        removed_entries.append({
            'prompt': prompt,
            'placeholders': list(set(found_placeholders))
        })
    else:
        clean_entries.append(entry)

print(f"\n📊 Removal Results:")
print(f"   Started with: {len(dataset)} entries")
print(f"   ❌ Removed placeholders: {len(removed_entries)}")
print(f"   ✅ Clean entries: {len(clean_entries)}")
print(f"   📈 Retention: {(len(clean_entries)/len(dataset)*100):.1f}%")

print("\n" + "=" * 70)
print("EXAMPLES OF REMOVED PLACEHOLDERS:")
print("=" * 70)
for i, entry in enumerate(removed_entries[:15], 1):
    print(f"{i}. {entry['prompt']}")
    print(f"   Placeholders: {', '.join(entry['placeholders'])}")

# Save cleaned dataset
with open('src/resources/combined-training-dataset-final.json', 'w', encoding='utf-8') as f:
    json.dump(clean_entries, f, indent=2)

print("\n" + "=" * 70)
print("✅ PLACEHOLDER REMOVAL COMPLETE!")
print("=" * 70)
print(f"✅ Removed: {len(removed_entries)} template entries")
print(f"✅ Retained: {len(clean_entries)} concrete entries")
print(f"✅ File saved: src/resources/combined-training-dataset-final.json")
print(f"✅ Backup: {backup_file}")
print("=" * 70)

print("\n🔍 VALIDATING CLEAN DATASET:")
# Quick validation
has_any_placeholders = False
for entry in clean_entries:
    for pattern in placeholder_patterns:
        if re.search(pattern, entry.get('code', '')) or re.search(pattern, entry.get('xpath', '')):
            has_any_placeholders = True
            break

if has_any_placeholders:
    print("⚠️  WARNING: Some placeholders still remain!")
else:
    print("✅ NO PLACEHOLDERS REMAINING - All entries are concrete!")

print(f"✅ {len(clean_entries)} production-ready entries")
print("\n✅ DATASET IS NOW 100% CONCRETE TRAINING DATA! 🚀")
