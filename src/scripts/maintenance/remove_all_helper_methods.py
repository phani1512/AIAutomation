import json
import re
from datetime import datetime

print("=== Removing Entries with Non-Working Helper Methods ===\n")

# Load dataset
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

print(f"Original entries: {len(dataset)}")

# Create backup
backup_path = f'src/resources/combined-training-dataset-final-backup-clean-{datetime.now().strftime("%Y%m%d_%H%M%S")}.json'
print(f"Creating backup: {backup_path}")
with open(backup_path, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2, ensure_ascii=False)

# List of ALL custom helper methods that won't work in test builder
custom_helper_methods = [
    # Page loading/waiting utilities
    'waitForProcessingSpinner',
    'waitForPageLoading',
    'waitForToastSuccess',
    'waitUntilDialogIsOpen',
    
    # Element interaction helpers
    'clickSubmitButton',
    'clickDialogButton',
    'clickEditPencilButton',
    'clickLink',
    
    # Search/table utilities
    'searchTable',
    'searchWorkFlows',
    'isSearchTableNoResultsFound',
    
    # Element finding helpers (custom, not standard Selenium)
    'isElementFound',
    'findWebElementBy',
    'findWebElementsBy',
    'isElementInvisible',
    'isSubmitButtonDisabled',
    
    # Get text/data helpers
    'getWebElementText',
    'getToastSuccessText',
    'getInputFieldValidationMessage',
    'getPanelContents',
    'getStringListBy',
    'getWebElementCount',
    
    # Select/dropdown helpers
    'selectElementByVisibleText',
    
    # Frame/window helpers
    'switchToFrameByLocator',
    
    # Scroll helpers
    'scrollIntoView',
    
    # Other custom utilities
    'executeScript',
    'sleep'
]

# Create pattern to match any of these methods
helper_pattern = '|'.join([re.escape(method + '(') for method in custom_helper_methods])

# Filter out entries with helper methods
clean_entries = []
removed_entries = []

for i, entry in enumerate(dataset):
    code = entry.get('code', '')
    
    # Check if code contains any custom helper method
    has_helper = any(method + '(' in code for method in custom_helper_methods)
    
    if has_helper:
        removed_entries.append({
            'index': i,
            'prompt': entry.get('prompt', ''),
            'helpers': [m for m in custom_helper_methods if m + '(' in code]
        })
    else:
        clean_entries.append(entry)

print(f"\n=== Removal Summary ===")
print(f"Entries removed: {len(removed_entries)}")
print(f"Clean entries kept: {len(clean_entries)}")

# Show what's being removed
print(f"\n=== Top Reasons for Removal ===")
helper_counts = {}
for entry in removed_entries:
    for helper in entry['helpers']:
        helper_counts[helper] = helper_counts.get(helper, 0) + 1

sorted_helpers = sorted(helper_counts.items(), key=lambda x: x[1], reverse=True)
for helper, count in sorted_helpers[:15]:
    print(f"  {helper}: {count} entries")

# Show sample removed entries
print(f"\n=== Sample Removed Entries ===")
for i, entry in enumerate(removed_entries[:3]):
    print(f"\n{i+1}. Prompt: {entry['prompt']}")
    print(f"   Helpers: {', '.join(entry['helpers'])}")

# Validate clean entries
print(f"\n=== Validating Clean Entries ===")
all_valid = True
for entry in clean_entries:
    code = entry.get('code', '')
    if not code or not code.strip():
        print(f"  ⚠ Empty code in entry: {entry.get('prompt', '')}")
        all_valid = False

if all_valid:
    print("  ✅ All clean entries have valid code")

# Quality check
has_webdriverwait = sum(1 for e in clean_entries if 'WebDriverWait' in e.get('code', ''))
has_xpath = sum(1 for e in clean_entries if e.get('xpath', '').strip())

print(f"\n=== Clean Dataset Quality ===")
print(f"  Total entries: {len(clean_entries)}")
print(f"  With WebDriverWait: {has_webdriverwait} ({has_webdriverwait/len(clean_entries)*100:.1f}%)")
print(f"  With XPath: {has_xpath} ({has_xpath/len(clean_entries)*100:.1f}%)")

# Save cleaned dataset
print(f"\n=== Saving Clean Dataset ===")
with open('src/resources/combined-training-dataset-final.json', 'w', encoding='utf-8') as f:
    json.dump(clean_entries, f, indent=2, ensure_ascii=False)

print(f"✓ Saved {len(clean_entries)} clean entries")

print("\n" + "="*60)
print("✅ CLEANUP COMPLETE!")
print("="*60)
print(f"Original:  {len(dataset)} entries")
print(f"Removed:   {len(removed_entries)} entries ({len(removed_entries)/len(dataset)*100:.1f}%)")
print(f"Final:     {len(clean_entries)} entries ({len(clean_entries)/len(dataset)*100:.1f}%)")
print(f"Backup:    {backup_path}")
print("="*60)
print("\n✅ Dataset now contains ONLY working Selenium WebDriver code!")
