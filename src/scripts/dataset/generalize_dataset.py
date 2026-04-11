"""
Generalize Dataset - Add Generic Element Placeholders

This script analyzes the sircon_ui_dataset.json and creates generic versions
of prompts using <element> placeholders, making the model work for any element.

Example transformations:
- "click the sign in button" → "click <element>"
- "get text from first name" → "get text from <element>"
- "verify username is displayed" → "verify <element> is displayed"
"""

import json
import re
from collections import defaultdict

def extract_element_name(prompt):
    """Extract the element name from a prompt."""
    # Common patterns to remove to get element name
    patterns = [
        (r'^click\s+(?:the\s+)?(.+?)(?:\s+button|\s+link|\s+element|\s+field)?$', r'\1'),
        (r'^get\s+text\s+from\s+(?:the\s+)?(.+)$', r'\1'),
        (r'^verify\s+(?:the\s+)?(.+?)(?:\s+is\s+(?:displayed|present|visible))?$', r'\1'),
        (r'^enter\s+.+?\s+in\s+(?:the\s+)?(.+?)(?:\s+field)?$', r'\1'),
        (r'^select\s+.+?\s+from\s+(?:the\s+)?(.+?)(?:\s+dropdown)?$', r'\1'),
        (r'^wait\s+for\s+(?:the\s+)?(.+?)(?:\s+to\s+(?:load|appear))?$', r'\1'),
        (r'^get\s+count\s+of\s+(?:the\s+)?(.+)$', r'\1'),
    ]
    
    for pattern, replacement in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    return None

def generalize_prompt(prompt, action_type):
    """Create a generic version of a prompt using <element> placeholder."""
    prompt_lower = prompt.lower()
    
    # Click actions
    if 'click' in prompt_lower:
        if 'button' in prompt_lower:
            return "click <element> button"
        elif 'link' in prompt_lower:
            return "click <element> link"
        else:
            return "click <element>"
    
    # Get text actions
    elif 'get text from' in prompt_lower or 'get text' in prompt_lower:
        return "get text from <element>"
    
    # Verify/assert actions
    elif 'verify' in prompt_lower or 'assert' in prompt_lower:
        if 'displayed' in prompt_lower or 'visible' in prompt_lower:
            return "verify <element> is displayed"
        elif 'present' in prompt_lower:
            return "verify <element> is present"
        elif 'enabled' in prompt_lower:
            return "verify <element> is enabled"
        else:
            return "verify <element>"
    
    # Enter/input actions
    elif 'enter' in prompt_lower or 'input' in prompt_lower or 'type' in prompt_lower:
        if 'field' in prompt_lower:
            return "enter <value> in <element> field"
        else:
            return "enter <value> in <element>"
    
    # Select actions
    elif 'select' in prompt_lower:
        if 'dropdown' in prompt_lower:
            return "select <value> from <element> dropdown"
        else:
            return "select <value> from <element>"
    
    # Wait actions
    elif 'wait' in prompt_lower:
        return "wait for <element>"
    
    # Get count
    elif 'get count' in prompt_lower or 'count' in prompt_lower:
        return "get count of <element>"
    
    # Get attribute
    elif 'get attribute' in prompt_lower:
        return "get <attribute> from <element>"
    
    # Is displayed/present/visible
    elif 'is displayed' in prompt_lower or 'is visible' in prompt_lower:
        return "check if <element> is displayed"
    elif 'is present' in prompt_lower:
        return "check if <element> is present"
    
    # Default: keep original if no pattern matches
    return prompt

def analyze_dataset(dataset_path):
    """Analyze the dataset and show statistics."""
    with open(dataset_path, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    action_types = defaultdict(int)
    prompt_patterns = defaultdict(list)
    
    print("=" * 80)
    print("DATASET ANALYSIS")
    print("=" * 80)
    print(f"\nTotal records: {len(data)}")
    
    for item in data:
        for step in item.get('steps', []):
            action = step.get('action', '')
            prompt = step.get('prompt', '')
            action_types[action] += 1
            
            generic = generalize_prompt(prompt, action)
            prompt_patterns[generic].append(prompt)
    
    print(f"\n📊 Action Types Distribution:")
    for action, count in sorted(action_types.items(), key=lambda x: -x[1]):
        print(f"  {action:20s}: {count:4d}")
    
    print(f"\n🔍 Generic Patterns Found: {len(prompt_patterns)}")
    print("\nTop 20 Generic Patterns:")
    for i, (generic, originals) in enumerate(sorted(prompt_patterns.items(), key=lambda x: -len(x[1]))[:20], 1):
        print(f"\n{i}. Generic: '{generic}'")
        print(f"   Covers {len(originals)} specific prompts:")
        for orig in originals[:3]:  # Show first 3 examples
            print(f"   - {orig}")
        if len(originals) > 3:
            print(f"   ... and {len(originals) - 3} more")
    
    return data, prompt_patterns

def create_generic_entries(data):
    """Create generic versions of dataset entries."""
    generic_entries = []
    seen_generics = set()
    
    for item in data:
        for step in item.get('steps', []):
            action = step.get('action', '')
            prompt = step.get('prompt', '')
            code = step.get('code', '')
            element_type = step.get('element_type', 'element')
            
            # Create generic prompt
            generic_prompt = generalize_prompt(prompt, action)
            
            # Avoid duplicates
            key = (generic_prompt, action, element_type)
            if key in seen_generics:
                continue
            seen_generics.add(key)
            
            # Create generic entry
            generic_entry = {
                "action": f"Generic - {action}",
                "description": f"Generic pattern for {action} action on any {element_type}",
                "steps": [{
                    "step": 1,
                    "action": action,
                    "code": code.replace(step.get('locator', 'By.id("element")'), 'By.id("<element-id>")'),
                    "element_type": element_type,
                    "locator": 'By.id("<element-id>")',
                    "value": step.get('value', ''),
                    "prompt": generic_prompt,
                    "page_object": "GenericPage",
                    "method_name": f"generic{action.capitalize()}",
                    "error_message": step.get('error_message', 'element not found'),
                    "is_generic": True  # Flag to identify generic entries
                }]
            }
            
            generic_entries.append(generic_entry)
    
    return generic_entries

def enhance_dataset(dataset_path, output_path):
    """Enhance dataset with generic patterns."""
    print("\n" + "=" * 80)
    print("ENHANCING DATASET")
    print("=" * 80)
    
    # Load original data
    with open(dataset_path, 'r', encoding='utf-8') as f:
        original_data = json.load(f)
    
    print(f"\n✅ Loaded {len(original_data)} original entries")
    
    # Create generic entries
    generic_entries = create_generic_entries(original_data)
    print(f"✅ Created {len(generic_entries)} generic entries")
    
    # Combine: Keep originals + add generics
    enhanced_data = original_data + generic_entries
    
    # Save enhanced dataset
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(enhanced_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n💾 Saved enhanced dataset to: {output_path}")
    print(f"   Total entries: {len(enhanced_data)} ({len(original_data)} original + {len(generic_entries)} generic)")
    
    return enhanced_data

def show_examples(enhanced_data):
    """Show example comparisons."""
    print("\n" + "=" * 80)
    print("EXAMPLE TRANSFORMATIONS")
    print("=" * 80)
    
    generic_items = [item for item in enhanced_data if item['steps'][0].get('is_generic', False)]
    
    print("\n🔄 Sample Generic Patterns (first 10):\n")
    for i, item in enumerate(generic_items[:10], 1):
        step = item['steps'][0]
        print(f"{i}. Action: {step['action']}")
        print(f"   Generic Prompt: '{step['prompt']}'")
        print(f"   Element Type: {step['element_type']}")
        print(f"   Generic Locator: {step['locator']}")
        print()

if __name__ == "__main__":
    import os
    
    # File paths
    dataset_path = "src/resources/sircon_ui_dataset.json"
    output_path = "src/resources/sircon_ui_dataset_enhanced.json"
    
    if not os.path.exists(dataset_path):
        print(f"❌ Error: Dataset not found at {dataset_path}")
        print("   Please run this script from the project root directory")
        exit(1)
    
    print("\n🚀 Dataset Generalization Tool")
    print("   This tool creates generic versions of your prompts using <element> placeholders")
    print("   The model will learn flexible patterns that work for ANY element!\n")
    
    # Step 1: Analyze
    data, patterns = analyze_dataset(dataset_path)
    
    # Step 2: Enhance
    enhanced_data = enhance_dataset(dataset_path, output_path)
    
    # Step 3: Show examples
    show_examples(enhanced_data)
    
    print("\n" + "=" * 80)
    print("✅ COMPLETE!")
    print("=" * 80)
    print(f"""
Next Steps:
1. Review the enhanced dataset: {output_path}
2. Retrain your model with the new generic patterns
3. Test with prompts like:
   - "click <element>"
   - "get text from <element>"
   - "verify <element> is displayed"
   
The model will now understand generic patterns and work for ANY element! 🎉
""")
