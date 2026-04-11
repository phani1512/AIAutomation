# Code Generation Package - Modular Architecture

## Overview

This package provides modular components for intelligent test code generation and semantic analysis. All modules work universally across ANY test case type (login, registration, e-commerce, applications, profiles, search, data entry, etc.).

## Package Structure

```
code_generation/
├── __init__.py              # Package initialization
├── field_analyzer.py        # Universal field type detection (30+ types)
├── test_data_generator.py  # Context-aware test data generation
├── context_analyzer.py     # Workflow and domain detection
└── semantic_modifier.py    # Semantic test modifications
```

## Modules

### 1. field_analyzer.py
**Universal Field Type Detection**

Detects 30+ field types using two-tier analysis:
- **Priority 1**: Value pattern matching (email from @, phone from digits, etc.)
- **Priority 2**: Text context analysis (field labels, placeholders)

**Supported Field Types:**
- Authentication: email, password, username
- Contact: phone, name, address, city, state, country
- Date/Time: date, time, datetime
- E-commerce: credit_card, price, zip_code
- Applications: ssn, license_number
- Numeric: number, quantity, age, amount
- Text: text, textarea, search, url, company, title
- Selection: select, checkbox, radio
- File: file_upload

**Key Functions:**
- `infer_field_type_from_text(text, value)` - Detect field type
- `infer_validation_rules(text, value)` - Extract validation rules
- `infer_if_required(text, locator)` - Check if required
- `infer_max_length(text, value)` - Infer max length
- `extract_field_info_from_action(action)` - Extract complete field info

### 2. test_data_generator.py
**Context-Aware Test Data Generation**

Generates intelligent test data for:
- **Negative Testing**: Invalid data specific to field type
- **Boundary Testing**: Min/max values for each field type
- **Variation Testing**: Alternative valid formats

**Key Functions:**
- `generate_invalid_data(...)` - Invalid data (e.g., incomplete phone, negative price)
- `generate_boundary_data(...)` - Min/max values (e.g., a@b.c minimum email)
- `generate_variation_data(...)` - Alternative formats (e.g., international phone)

**Works For:**
- Login tests → Invalid email formats, weak passwords
- E-commerce → Invalid cards, negative prices, zero quantities
- Applications → Incomplete SSN, invalid license formats
- Profiles → Numeric names, invalid dates
- Search → Empty queries, very long queries

### 3. context_analyzer.py
**Workflow and Domain Detection**

Dynamically analyzes test context:
- **Workflow Detection**: authentication, registration, e-commerce, application_form, search, transaction, data_entry
- **Business Domain**: insurance_licensing, financial_services, healthcare, general
- **Field Extraction**: Builds field list from actual test actions

**Key Functions:**
- `analyze_test_context(test_name, test_url, actions)` - Full context analysis
- `extract_workflow_from_test(...)` - Pattern-based workflow detection

**No Hardcoding:**
- Extracts domain from URL dynamically
- Uses extensible workflow patterns
- Builds field array from actual actions

### 4. semantic_modifier.py
**Semantic Test Modifications**

Applies intelligent modifications to test code:
- **Negative**: Replace valid data with invalid data
- **Boundary**: Replace normal data with min/max values
- **Edge Case**: Special characters, security tests (XSS, SQL injection)
- **Variation**: Alternative valid data

**Key Functions:**
- `apply_negative_modifications(code, session, language)` - Invalid data
- `apply_boundary_modifications(code, session, language)` - Boundary values
- `apply_edge_case_modifications(code, session, language)` - Security tests
- `apply_variation_modifications(code, session, language)` - Alternative data

**Returns:**
- Modified test code
- Suggested values list with reasoning

## Usage Example

```python
from code_generation import (
    FieldAnalyzer,
    TestDataGenerator,
    ContextAnalyzer,
    SemanticModifier
)

# Analyze field type
field_type = FieldAnalyzer.infer_field_type_from_text(
    text="email input",
    value="user@example.com"
)
# Returns: 'email'

# Generate test context
context = ContextAnalyzer.analyze_test_context(
    test_name="Login Test",
    test_url="https://example.com/login",
    actions=[...]
)

# Generate invalid data
invalid_value, reason = TestDataGenerator.generate_invalid_data(
    field_value="user@example.com",
    locator="By.ID('email')",
    action_text="Enter email",
    test_context=context,
    step=1
)
# Returns: ('user@', 'Missing domain')

# Apply semantic modifications
modified_code, suggestions = SemanticModifier.apply_negative_modifications(
    code=original_code,
    session=test_session,
    language='python'
)
```

## Benefits

### ✅ Universal Coverage
- Works for ANY test case type (not just login)
- No hardcoded field indicators
- Pattern-based detection from actual data

### ✅ Context-Aware
- Understands workflow (authentication vs registration)
- Adapts to business domain
- Generates relevant test data

### ✅ Maintainable
- Modular architecture
- Clear separation of concerns
- Easy to test and extend

### ✅ Reusable
- Used by both Recorder and Builder
- Can be imported anywhere
- Consistent behavior

## Integration with code_generator.py

**Phase 1 (Current)**: Modules exist alongside `code_generator.py`
- Original file untouched (safe)
- New modules can be tested independently
- Zero risk to existing functionality

**Phase 2 (Next)**: Import modules into `code_generator.py`
```python
from code_generation import (
    FieldAnalyzer,
    TestDataGenerator,
    ContextAnalyzer,
    SemanticModifier
)

# Replace function calls
inferred_type = FieldAnalyzer.infer_field_type_from_text(text, value)
context = ContextAnalyzer.analyze_test_context(name, url, actions)
# etc.
```

**Phase 3 (Final)**: Remove duplicate code from `code_generator.py`
- Keep only orchestration logic
- All analysis/generation delegated to modules
- Clean, maintainable codebase

## Testing Strategy

1. **Unit Tests**: Test each module independently
2. **Integration Tests**: Test modules working together
3. **Regression Tests**: Verify Recorder and Builder still work
4. **Validation**: Compare outputs with original implementation

## Version History

- **v1.0.0**: Initial modular extraction
  - All functions copied from `code_generator.py`
  - Original functionality preserved
  - Zero breaking changes
