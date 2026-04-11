import json
import os
from datetime import datetime

# Load the dataset
print("Loading dataset...")
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Original entries: {len(dataset)}")

# Create backup first
backup_path = f'src/resources/combined-training-dataset-final-backup-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
print(f"\nCreating backup: {backup_path}")
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

# Helper method patterns to identify
helper_patterns = [
    'waitUntilVisibilityOfElementLocatedBy',
    'waitAndGetText',
    'waitAndClickOnElement',
    'clickNavigationTab',
    'clearAndSendKeys',
    'setInputFieldValue',
    'clickButton',
    'setDropdownValue',
    'setCheckboxOn'
]

# Identify truncated entries
def is_truncated(code):
    """Check if code appears truncated (doesn't end properly)"""
    if not code or not code.strip():
        return True
    
    code = code.strip()
    
    # Proper endings for Java code
    proper_endings = [';', '}', ')', '"]', '\"]', '")']
    
    # Check if ends properly
    ends_properly = any(code.endswith(ending) for ending in proper_endings)
    
    if not ends_properly:
        return True
    
    # Additional checks for incomplete code
    # Check for incomplete method calls
    if code.rstrip().endswith(','):
        return True
    
    # Check for incomplete strings
    if code.count('"') % 2 != 0:
        return True
    
    return False

# Categorize entries
truncated_indices = []
helper_but_complete = []
clean_entries = []

for i, entry in enumerate(dataset):
    code = entry.get('code', '')
    has_helper = any(pattern in code for pattern in helper_patterns)
    truncated = is_truncated(code)
    
    if truncated:
        truncated_indices.append(i)
    elif has_helper:
        helper_but_complete.append(i)
    else:
        clean_entries.append(i)

print(f"\n=== Analysis ===")
print(f"Truncated entries to remove: {len(truncated_indices)}")
print(f"Entries with helpers but complete: {len(helper_but_complete)}")
print(f"Clean entries: {len(clean_entries)}")
print(f"Expected final count: {len(helper_but_complete) + len(clean_entries)}")

# Show sample of what will be removed
print(f"\n=== Sample Truncated Entries Being Removed ===")
for idx in truncated_indices[:3]:
    entry = dataset[idx]
    print(f"\nPrompt: {entry.get('prompt', '')}")
    code = entry.get('code', '')
    print(f"Code ending: ...{code[-100:]}")
    print(f"Reason: Ends with '{code.strip()[-20:]}'")

# Remove truncated entries
print(f"\n=== Removing Truncated Entries ===")
cleaned_dataset = [entry for i, entry in enumerate(dataset) if i not in truncated_indices]

print(f"Entries removed: {len(dataset) - len(cleaned_dataset)}")
print(f"Final dataset size: {len(cleaned_dataset)}")

# Verify no truncated entries remain
print(f"\n=== Verification ===")
remaining_truncated = sum(1 for entry in cleaned_dataset if is_truncated(entry.get('code', '')))
print(f"Remaining truncated entries: {remaining_truncated}")

remaining_helpers = sum(1 for entry in cleaned_dataset if any(p in entry.get('code', '') for p in helper_patterns))
print(f"Remaining entries with helper methods: {remaining_helpers}")

# Validate JSON structure
print(f"\n=== JSON Validation ===")
all_have_prompt = all('prompt' in entry for entry in cleaned_dataset)
all_have_code = all('code' in entry for entry in cleaned_dataset)
all_code_nonempty = all(entry.get('code', '').strip() for entry in cleaned_dataset)

print(f"All entries have 'prompt': {all_have_prompt}")
print(f"All entries have 'code': {all_have_code}")
print(f"All code fields non-empty: {all_code_nonempty}")

# Check for duplicates
prompts = [entry.get('prompt', '') for entry in cleaned_dataset]
unique_prompts = set(prompts)
print(f"Total prompts: {len(prompts)}")
print(f"Unique prompts: {len(unique_prompts)}")
print(f"Duplicates: {len(prompts) - len(unique_prompts)}")

# Save cleaned dataset
output_path = 'src/resources/combined-training-dataset-final.json'
print(f"\n=== Saving Cleaned Dataset ===")
print(f"Saving to: {output_path}")

with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(cleaned_dataset, f, indent=2, ensure_ascii=False)

print(f"✓ Saved successfully")

# Final statistics
print(f"\n{'='*60}")
print(f"FINAL SUMMARY")
print(f"{'='*60}")
print(f"Original entries:      {len(dataset)}")
print(f"Truncated removed:     {len(truncated_indices)}")
print(f"Final entries:         {len(cleaned_dataset)}")
print(f"Clean entries:         {len(clean_entries)}")
print(f"Complete with helpers: {len(helper_but_complete)}")
print(f"Backup saved to:       {backup_path}")
print(f"{'='*60}")
print(f"✓ Dataset cleanup complete!")
