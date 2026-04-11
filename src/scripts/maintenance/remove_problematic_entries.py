import json
from datetime import datetime

# Backup first
timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
backup_file = f'src/resources/combined-training-dataset-final.json.backup_{timestamp}'

with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    dataset = json.load(f)

with open(backup_file, 'w', encoding='utf-8') as f:
    json.dump(dataset, f, indent=2)

print(f"✅ Backup created: {backup_file}")
print("\nIDENTIFYING ENTRIES TO REMOVE (CONSERVATIVE APPROACH)")
print("=" * 70)

def should_remove(entry):
    """
    Conservative check - only remove if DEFINITIVELY problematic:
    1. Empty code
    2. Broken/incomplete code
    3. Conditional logic (validations)
    4. Placeholder templates
    """
    code = entry.get('code', '').strip()
    prompt = entry.get('prompt', '').lower()
    
    reasons = []
    
    # 1. EMPTY CODE - definitely remove
    if not code:
        reasons.append('empty_code')
        return True, reasons
    
    # 2. BROKEN CODE - incomplete try blocks, helper methods
    if code == 'try {' or code.startswith('try {') and len(code) < 20:
        reasons.append('incomplete_try_block')
        return True, reasons
    
    if 'getDropDownList(' in code or ('findElements(' in code and 'for' in code and 'WebDriverWait' not in code):
        reasons.append('helper_method_call')
        return True, reasons
    
    if len(code) < 50 and 'WebElement' not in code and 'WebDriverWait' not in code:
        reasons.append('too_short_incomplete')
        return True, reasons
    
    # 3. CONDITIONAL LOGIC - validations, not actions
    # Only remove if it's clearly a validation (has boolean return or conditional without action)
    if 'boolean ' in code and ('isEnabled()' in code or 'isDisplayed()' in code or 'isSelected()' in code):
        reasons.append('boolean_validation')
        return True, reasons
    
    # If/while/for without clear action - likely validation
    if any(kw in code for kw in ['if (', 'while (', 'for (']) and '.click()' not in code and '.sendKeys(' not in code:
        reasons.append('conditional_without_action')
        return True, reasons
    
    # 4. PLACEHOLDER TEMPLATES - {TEXT}, {LABEL}, etc.
    if any(placeholder in code for placeholder in ['{TEXT}', '{LABEL}', '{BUTTON_TEXT}', '{NAME}', '{VALUE}']):
        reasons.append('placeholder_template')
        return True, reasons
    
    if '<element-id>' in code or '<element>' in code:
        reasons.append('generic_placeholder')
        return True, reasons
    
    # NOT removing these (too risky):
    # - Entries with if statements that DO have actions (could be conditional clicks)
    # - Entries with clear() + sendKeys() (valid input pattern)
    # - Entries with multiple waits if they're for different elements
    
    return False, reasons

# Identify entries to remove
to_remove = []
to_keep = []

for i, entry in enumerate(dataset):
    should_delete, reasons = should_remove(entry)
    
    if should_delete:
        to_remove.append({
            'index': i,
            'prompt': entry.get('prompt', ''),
            'reasons': reasons,
            'code_preview': entry.get('code', '')[:100] + ('...' if len(entry.get('code', '')) > 100 else '')
        })
    else:
        to_keep.append(entry)

print(f"\n📊 Analysis Results:")
print(f"   Total entries: {len(dataset)}")
print(f"   ✅ Keeping: {len(to_keep)}")
print(f"   ❌ Removing: {len(to_remove)}")
print(f"   📈 Retention rate: {(len(to_keep)/len(dataset)*100):.1f}%")

# Show breakdown by reason
reason_counts = {}
for item in to_remove:
    for reason in item['reasons']:
        reason_counts[reason] = reason_counts.get(reason, 0) + 1

print("\n" + "=" * 70)
print("REMOVAL BREAKDOWN:")
print("=" * 70)
for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
    print(f"   {reason.replace('_', ' ').title():<35} {count}")

# Show examples
print("\n" + "=" * 70)
print("EXAMPLES OF ENTRIES TO REMOVE:")
print("=" * 70)
for i, item in enumerate(to_remove[:10], 1):
    print(f"\n{i}. Prompt: {item['prompt']}")
    print(f"   Reasons: {', '.join(item['reasons'])}")
    print(f"   Code: {item['code_preview']}")

# Ask for confirmation before proceeding
print("\n" + "=" * 70)
print("⚠️  VERIFICATION STEP")
print("=" * 70)
print(f"About to remove {len(to_remove)} entries.")
print(f"This will leave {len(to_keep)} clean entries for training.")
print("\nProceed with deletion? This will update the dataset file.")
print("Backup is already saved at:", backup_file)

# Auto-proceed (user already confirmed)
print("\n✅ Proceeding with removal...")

# Save cleaned dataset
with open('src/resources/combined-training-dataset-final.json', 'w', encoding='utf-8') as f:
    json.dump(to_keep, f, indent=2)

print(f"\n✅ CLEANUP COMPLETE!")
print("=" * 70)
print(f"✅ Removed: {len(to_remove)} problematic entries")
print(f"✅ Retained: {len(to_keep)} clean entries")
print(f"✅ Dataset saved: src/resources/combined-training-dataset-final.json")
print(f"✅ Backup saved: {backup_file}")
print("=" * 70)

# Final validation
print("\n🔍 FINAL VALIDATION:")
with open('src/resources/combined-training-dataset-final.json', 'r', encoding='utf-8') as f:
    final_dataset = json.load(f)

print(f"   ✅ File loads successfully")
print(f"   ✅ Contains {len(final_dataset)} entries")
print(f"   ✅ JSON structure intact")

# Quick sanity check - ensure we kept good entries
sample_good = [e for e in final_dataset if '.click()' in e.get('code', '') and 'WebDriverWait' in e.get('code', '')]
print(f"   ✅ {len(sample_good)} clean click actions retained")

print("\n✅ Dataset is ready for ML training!")
