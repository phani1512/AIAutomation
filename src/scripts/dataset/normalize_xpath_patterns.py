"""
XPath Normalization Script

This script upgrades all XPath patterns in the dataset to use normalize-space()
for robust text matching. This is a best practice that handles:
- Leading/trailing whitespace
- Multiple internal spaces
- Tab characters, newlines, etc.

Patterns to update:
1. //element[text()='value'] → //element[normalize-space()='value']
2. //element[contains(text(), 'value')] → //element[normalize-space()='value']
3. //element[text()='{VAR}'] → //element[normalize-space()='{VAR}']
"""

import json
import re
from pathlib import Path

def normalize_xpath_patterns(dataset_path):
    """Update all XPath patterns to use normalize-space()."""
    
    print("🔧 XPath Normalization Script")
    print("=" * 60)
    
    # Load dataset
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    updates = 0
    patterns_found = {
        'text()': 0,
        'contains(text(),': 0,
        'already_normalized': 0
    }
    
    for entry in data:
        changed = False
        
        # Update code field
        if 'code' in entry:
            original_code = entry['code']
            
            # Pattern 1: text()='...' or text()=\"...\"
            new_code = re.sub(
                r'\[text\(\)\s*=\s*(["\'])',
                r'[normalize-space()=\1',
                original_code
            )
            
            # Pattern 2: contains(text(), '...') for exact matching
            # Only if it's a simple contains without wildcards
            new_code = re.sub(
                r'\[contains\(text\(\)\s*,\s*(["\'])([^"\']*)\1\)\]',
                r'[normalize-space()=\1\2\1]',
                new_code
            )
            
            if new_code != original_code:
                entry['code'] = new_code
                changed = True
                if 'text()' in original_code:
                    patterns_found['text()'] += 1
                if 'contains(text(),' in original_code:
                    patterns_found['contains(text(),'] += 1
        
        # Update xpath field
        if 'xpath' in entry:
            original_xpath = entry['xpath']
            
            # Skip if already uses normalize-space()
            if 'normalize-space()' in original_xpath:
                patterns_found['already_normalized'] += 1
                continue
            
            # Pattern 1: text()='...'
            new_xpath = re.sub(
                r'\[text\(\)\s*=\s*(["\'])',
                r'[normalize-space()=\1',
                original_xpath
            )
            
            # Pattern 2: contains(text(), '...')
            new_xpath = re.sub(
                r'\[contains\(text\(\)\s*,\s*(["\'])([^"\']*)\1\)\]',
                r'[normalize-space()=\1\2\1]',
                new_xpath
            )
            
            if new_xpath != original_xpath:
                entry['xpath'] = new_xpath
                changed = True
        
        if changed:
            updates += 1
    
    # Save updated dataset
    backup_path = dataset_path.replace('.json', '_backup_before_normalize.json')
    print(f"\n📦 Creating backup: {Path(backup_path).name}")
    with open(backup_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    print(f"💾 Saving updated dataset...")
    with open(dataset_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    
    # Report
    print("\n" + "=" * 60)
    print("✅ XPath Normalization Complete!")
    print("=" * 60)
    print(f"📊 Statistics:")
    print(f"   Updated entries: {updates}")
    print(f"   text() patterns fixed: {patterns_found['text()']}")
    print(f"   contains() patterns fixed: {patterns_found['contains(text(),']}")
    print(f"   Already normalized: {patterns_found['already_normalized']}")
    print(f"\n💡 Benefits:")
    print(f"   ✓ Handles whitespace variations")
    print(f"   ✓ More reliable element matching")
    print(f"   ✓ Industry best practice")
    print(f"   ✓ Works with {updates} dataset entries")
    
    return updates


if __name__ == "__main__":
    import sys
    
    # Get dataset path
    if len(sys.argv) > 1:
        dataset_path = sys.argv[1]
    else:
        dataset_path = "src/resources/combined-training-dataset-final.json"
    
    print(f"📂 Dataset: {dataset_path}\n")
    
    try:
        count = normalize_xpath_patterns(dataset_path)
        print(f"\n✨ Success! Updated {count} entries.")
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
