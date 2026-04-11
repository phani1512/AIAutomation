"""
Test field detection for builder vs recorder format actions
"""
from ml_models.field_aware_suggestions import FieldTypeDetector

# Test 1: Recorder format (with element object)
recorder_action = {
    "step": 1,
    "action_type": "click_and_input",
    "element": {
        "id": "producer-email",
        "name": "username",
        "type": "text",
        "placeholder": None
    },
    "value": "test@test.com"
}

# Test 2: Builder format (with prompt)
builder_action = {
    "prompt": "enter text in email field",
    "type": "action",
    "value": "AAAAAAAAAA",
    "description": "Field Length Boundary Testing: enter text in email field at boundary"
}

# Test 3: Builder password format
builder_password_action = {
    "prompt": "enter password",
    "type": "action",
    "value": "test123",
    "description": "enter password in login form"
}

# Test 4: Builder phone format
builder_phone_action = {
    "prompt": "enter phone number",
    "type": "action",
    "value": "555-1234",
    "description": "provide contact phone"
}

detector = FieldTypeDetector()

print("=" * 60)
print("FIELD TYPE DETECTION TEST")
print("=" * 60)

print("\n1. Recorder Format (element.id='producer-email'):")
field_type = detector.detect(recorder_action)
print(f"   Detected: {field_type}")
print(f"   Expected: email")
print(f"   Result: {'✓ PASS' if field_type == 'email' else '✗ FAIL'}")

print("\n2. Builder Format (prompt='enter text in email field'):")
field_type = detector.detect(builder_action)
print(f"   Detected: {field_type}")
print(f"   Expected: email")
print(f"   Result: {'✓ PASS' if field_type == 'email' else '✗ FAIL'}")

print("\n3. Builder Password (prompt='enter password'):")
field_type = detector.detect(builder_password_action)
print(f"   Detected: {field_type}")
print(f"   Expected: password")
print(f"   Result: {'✓ PASS' if field_type == 'password' else '✗ FAIL'}")

print("\n4. Builder Phone (prompt='enter phone number'):")
field_type = detector.detect(builder_phone_action)
print(f"   Detected: {field_type}")
print(f"   Expected: phone")
print(f"   Result: {'✓ PASS' if field_type == 'phone' else '✗ FAIL'}")

print("\n" + "=" * 60)
