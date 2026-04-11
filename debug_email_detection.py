"""
Debug why email field detection is failing for semantic test action
"""
import sys
sys.path.insert(0, 'src/main/python')

from ml_models.field_aware_suggestions import FieldTypeDetector
import re

# Exact action from semantic test
action = {
    "prompt": "enter text in email field",
    "type": "action",
    "value": "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA",
    "description": "Field Length Boundary Testing: enter text in email field at boundary"
}

detector = FieldTypeDetector()

print("=" * 70)
print("DEBUG: Email Field Detection")
print("=" * 70)

# Extract metadata simulation
element = action.get('element', {})
if isinstance(element, dict):
    element_id = (element.get('id') or '').lower()
    element_name = (element.get('name') or '').lower()
    element_class = (element.get('className') or '').lower()
    element_type = (element.get('type') or '').lower()
    placeholder = (element.get('placeholder') or '').lower()
else:
    element_id = (action.get('element_id') or '').lower()
    element_name = (action.get('element_name') or '').lower()
    element_class = (action.get('element_class') or '').lower()
    element_type = ''
    placeholder = (action.get('placeholder') or '').lower()

prompt = (action.get('prompt') or '').lower()
description = (action.get('description') or '').lower()
value = action.get('value', '')

combined_text = f"{element_id} {element_name} {element_class} {element_type} {placeholder} {prompt} {description}"

print(f"\n1. Extracted Fields:")
print(f"   element_id: '{element_id}'")
print(f"   element_name: '{element_name}'")
print(f"   element_class: '{element_class}'")
print(f"   element_type: '{element_type}'")
print(f"   placeholder: '{placeholder}'")
print(f"   prompt: '{prompt}'")
print(f"   description: '{description}'")

print(f"\n2. Combined Text:")
print(f"   '{combined_text}'")

print(f"\n3. Pattern Matching:")
email_patterns = [
    r'email', r'e-mail', r'mail', r'user.*mail',
    r'contact.*email', r'login.*email'
]
for pattern in email_patterns:
    match = re.search(pattern, combined_text, re.IGNORECASE)
    print(f"   Pattern '{pattern}': {' MATCH!' if match else 'no match'}")

print(f"\n4. Actual Detection:")
detected = detector.detect(action)
print(f"   Result: {detected}")
print(f"   Expected: email")
print(f"   Status: {'✓ PASS' if detected == 'email' else '✗ FAIL'}")

print("\n" + "=" * 70)
