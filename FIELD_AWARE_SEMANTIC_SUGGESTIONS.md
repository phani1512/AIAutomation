# Field-Aware Semantic Suggestions Enhancement

## Current Problem

**What we have now:**
```javascript
{
  "name": "Empty Form Submission Test",
  "actions": [
    { "step": 1, "action_type": "click_and_input", "value": "pvalaboju@vertafore.com" },
    { "step": 2, "action_type": "click_and_input", "value": "Phanindraa@1512" }
  ],
  "steps": [  // Generic scenario steps
    "Leave all required fields empty",
    "Attempt to submit form",
    "Verify validation errors appear",
    "Verify form is not submitted"
  ]
}
```

**What we need:**
```javascript
{
  "name": "Email Boundary Testing - Invalid Formats",
  "actions": [
    { "step": 1, "action_type": "click_and_input", "value": "pvalaboju@vertafore.com" },
    { "step": 2, "action_type": "click_and_input", "value": "Phanindraa@1512" }
  ],
  "field_suggestions": [  // Per-field boundary data
    {
      "field_index": 0,
      "field_type": "email",
      "original_value": "pvalaboph@vertafore.com",
      "suggestions": [
        { "value": "notanemail", "description": "Missing @ symbol" },
        { "value": "user@", "description": "Incomplete domain" },
        { "value": "@domain.com", "description": "Missing username" },
        { "value": "test+user@example.com", "description": "Plus sign in email" },
        { "value": "admin'--@test.com", "description": "SQL injection attempt" }
      ]
    },
    {
      "field_index": 1,
      "field_type": "password",
      "original_value": "Phanindraa@1512",
      "suggestions": [
        { "value": "123", "description": "Too short (< 8 chars)" },
        { "value": "password", "description": "No special characters" },
        { "value": "Password123", "description": "No special characters" },
        { "value": "@#$%^&*", "description": "Only special characters" },
        { "value": "' OR '1'='1", "description": "SQL injection attempt" }
      ]
    }
  ]
}
```

---

## Implementation Plan

### 1. Create Field Type Detector

**File**: `src/main/python/ml_models/field_type_detector.py`

```python
def detect_field_type(action: dict) -> str:
    """
    Detect field type from action data.
    Returns: 'email', 'password', 'phone', 'url', 'text', 'number', 'date', etc.
    """
    # Check element attributes
    element_id = action.get('element_id', '').lower()
    element_name = action.get('element_name', '').lower()
    value = action.get('value', '')
    
    # Email detection
    if 'email' in element_id or 'email' in element_name:
        return 'email'
    if '@' in value and '.' in value:
        return 'email'
    
    # Password detection
    if 'password' in element_id or 'password' in element_name or 'pwd' in element_id:
        return 'password'
    
    # Phone detection
    if 'phone' in element_id or 'tel' in element_id or 'mobile' in element_id:
        return 'phone'
    
    # URL detection
    if 'url' in element_id or 'website' in element_id or 'link' in element_id:
        return 'url'
    
    # Number detection
    if 'age' in element_id or 'number' in element_id or 'quantity' in element_id:
        return 'number'
    
    # Date detection
    if 'date' in element_id or 'dob' in element_id or 'birth' in element_id:
        return 'date'
    
    # Default to text
    return 'text'
```

### 2. Create Boundary Data Generator

**File**: `src/main/python/ml_models/boundary_data_generator.py`

```python
class BoundaryDataGenerator:
    """Generate field-specific boundary test data."""
    
    BOUNDARY_DATA = {
        'email': [
            {'value': 'notanemail', 'description': 'Missing @ symbol', 'category': 'invalid_format'},
            {'value': 'user@', 'description': 'Incomplete domain', 'category': 'invalid_format'},
            {'value': '@domain.com', 'description': 'Missing username', 'category': 'invalid_format'},
            {'value': 'user @domain.com', 'description': 'Space in email', 'category': 'invalid_format'},
            {'value': 'test+user@example.com', 'description': 'Plus sign (valid but often rejected)', 'category': 'edge_case'},
            {'value': 'user@sub.domain.example.com', 'description': 'Subdomain email', 'category': 'edge_case'},
            {'value': 'a@b.c', 'description': 'Minimal valid email', 'category': 'boundary'},
            {'value': 'x' * 64 + '@example.com', 'description': 'Max length username (64 chars)', 'category': 'boundary'},
            {'value': "admin'--@test.com", 'description': 'SQL injection', 'category': 'security'},
            {'value': '<script>@test.com', 'description': 'XSS attempt', 'category': 'security'},
            {'value': '../../etc/passwd@test.com', 'description': 'Path traversal', 'category': 'security'}
        ],
        
        'password': [
            {'value': '123', 'description': 'Too short (< 8 chars)', 'category': 'invalid'},
            {'value': 'password', 'description': 'Common weak password', 'category': 'weak'},
            {'value': 'Password123', 'description': 'No special characters', 'category': 'weak'},
            {'value': 'password123', 'description': 'No uppercase', 'category': 'weak'},
            {'value': 'PASSWORD123', 'description': 'No lowercase', 'category': 'weak'},
            {'value': '@#$%^&*', 'description': 'Only special characters', 'category': 'edge_case'},
            {'value': '12345678', 'description': 'Only numbers', 'category': 'weak'},
            {'value': 'aA1!', 'description': 'Minimum valid (4 types)', 'category': 'boundary'},
            {'value': 'x' * 128, 'description': 'Very long password', 'category': 'boundary'},
            {'value': "' OR '1'='1", 'description': 'SQL injection', 'category': 'security'},
            {'value': '<script>alert(1)</script>', 'description': 'XSS attempt', 'category': 'security'},
            {'value': 'Pass word1!', 'description': 'Space in password', 'category': 'edge_case'}
        ],
        
        'phone': [
            {'value': '123', 'description': 'Too short', 'category': 'invalid'},
            {'value': 'abcdefghij', 'description': 'Letters instead of numbers', 'category': 'invalid'},
            {'value': '555-1234', 'description': 'Missing area code', 'category': 'invalid'},
            {'value': '+1-555-123-4567', 'description': 'International format', 'category': 'valid'},
            {'value': '(555) 123-4567', 'description': 'With parentheses', 'category': 'valid'},
            {'value': '5551234567', 'description': 'No formatting', 'category': 'valid'},
            {'value': '+44 20 7123 4567', 'description': 'UK format', 'category': 'edge_case'},
            {'value': '1' * 15, 'description': 'Max digits', 'category': 'boundary'}
        ],
        
        'url': [
            {'value': 'notaurl', 'description': 'No protocol', 'category': 'invalid'},
            {'value': 'http://', 'description': 'No domain', 'category': 'invalid'},
            {'value': 'example.com', 'description': 'Missing protocol', 'category': 'edge_case'},
            {'value': 'http://example.com', 'description': 'HTTP (not HTTPS)', 'category': 'valid'},
            {'value': 'https://example.com', 'description': 'HTTPS', 'category': 'valid'},
            {'value': 'https://sub.domain.example.com/path?query=value#hash', 'description': 'Complex URL', 'category': 'edge_case'},
            {'value': 'ftp://example.com', 'description': 'FTP protocol', 'category': 'edge_case'},
            {'value': "javascript:alert(1)", 'description': 'JavaScript injection', 'category': 'security'}
        ],
        
        'text': [
            {'value': '', 'description': 'Empty string', 'category': 'boundary'},
            {'value': ' ', 'description': 'Only spaces', 'category': 'edge_case'},
            {'value': 'a', 'description': 'Single character', 'category': 'boundary'},
            {'value': 'x' * 1000, 'description': 'Very long text (1000 chars)', 'category': 'boundary'},
            {'value': '你好世界', 'description': 'Unicode/Chinese characters', 'category': 'i18n'},
            {'value': 'مرحبا', 'description': 'Arabic/RTL text', 'category': 'i18n'},
            {'value': '😀🎉👍', 'description': 'Emojis', 'category': 'edge_case'},
            {'value': "'; DROP TABLE users--", 'description': 'SQL injection', 'category': 'security'},
            {'value': '<script>alert(1)</script>', 'description': 'XSS attempt', 'category': 'security'},
            {'value': '../../../etc/passwd', 'description': 'Path traversal', 'category': 'security'}
        ],
        
        'number': [
            {'value': '-1', 'description': 'Negative (often invalid)', 'category': 'edge_case'},
            {'value': '0', 'description': 'Zero', 'category': 'boundary'},
            {'value': '1', 'description': 'Minimum positive', 'category': 'boundary'},
            {'value': '999999999', 'description': 'Large number', 'category': 'boundary'},
            {'value': '1.5', 'description': 'Decimal (may be invalid)', 'category': 'edge_case'},
            {'value': 'abc', 'description': 'Non-numeric', 'category': 'invalid'}
        ],
        
        'date': [
            {'value': '13/32/2024', 'description': 'Invalid month/day', 'category': 'invalid'},
            {'value': '01/01/1900', 'description': 'Very old date', 'category': 'boundary'},
            {'value': '01/01/2100', 'description': 'Future date', 'category': 'boundary'},
            {'value': '02/29/2023', 'description': 'Invalid leap year', 'category': 'invalid'},
            {'value': '2024-12-31', 'description': 'ISO format', 'category': 'edge_case'}
        ]
    }
    
    def generate_for_field(self, field_type: str, original_value: str, max_suggestions: int = 5) -> list:
        """Generate boundary test suggestions for a specific field."""
        suggestions = self.BOUNDARY_DATA.get(field_type, self.BOUNDARY_DATA['text'])
        
        # Return top N suggestions
        return suggestions[:max_suggestions]
```

### 3. Enhance ML Semantic Analyzer

**File**: `src/main/python/ml_models/ml_semantic_analyzer.py`

Add new method:

```python
def suggest_field_specific_scenarios(self, actions: list, context: dict) -> list:
    """
    Generate field-specific boundary test scenarios.
    Returns test variants with per-field suggestions.
    """
    from .field_type_detector import detect_field_type
    from .boundary_data_generator import BoundaryDataGenerator
    
    generator = BoundaryDataGenerator()
    scenarios = []
    
    # Get input fields only
    input_actions = [a for a in actions if a.get('action_type') in ['input', 'click_and_input', 'select']]
    
    if not input_actions:
        return []
    
    # Generate per-field suggestions
    field_suggestions = []
    for idx, action in enumerate(input_actions):
        field_type = detect_field_type(action)
        original_value = action.get('value', '')
        
        suggestions = generator.generate_for_field(field_type, original_value)
        
        field_suggestions.append({
            'field_index': idx,
            'field_type': field_type,
            'field_step': action.get('step'),
            'original_value': original_value,
            'suggestions': suggestions
        })
    
    # Create test variants grouped by category
    categories = {}
    for field_sugg in field_suggestions:
        for sugg in field_sugg['suggestions']:
            category = sugg['category']
            if category not in categories:
                categories[category] = []
            categories[category].append({
                'field_index': field_sugg['field_index'],
                'field_type': field_sugg['field_type'],
                'suggestion': sugg
            })
    
    # Create scenario for each category
    for category, suggestions in categories.items():
        scenario = {
            'type': category,
            'title': f'{category.replace("_", " ").title()} Testing',
            'description': f'Test with {category} boundary data',
            'priority': 'high' if category == 'security' else 'medium',
            'field_suggestions': field_suggestions,  # Include all field suggestions
            'steps': [f"Test {s['field_type']} field with: {s['suggestion']['value']}" for s in suggestions]
        }
        scenarios.append(scenario)
    
    return scenarios
```

### 4. Update Test Variant Generation

When saving semantic test variants, include `field_suggestions`:

```python
# In recorder_handler.py or semantic analyzer
def create_field_aware_variants(test_case_id: str, actions: list):
    """Create semantic test variants with field-specific suggestions."""
    analyzer = get_ml_semantic_analyzer()
    
    # Get field-specific scenarios
    scenarios = analyzer.suggest_field_specific_scenarios(actions, {})
    
    variants = []
    for idx, scenario in enumerate(scenarios):
        variant = {
            'test_case_id': f"{test_case_id}_variant_{idx + 1}",
            'name': scenario['title'],
            'description': scenario['description'],
            'actions': actions,  # Original actions
            'field_suggestions': scenario['field_suggestions'],  # NEW: Per-field data
            'steps': scenario['steps'],  # Keep for display
            'tags': ['semantic', 'ai-generated', scenario['type']]
        }
        variants.append(variant)
    
    return variants
```

---

## Frontend Changes

### Update test-suite.js

**Current (Lines 1753-1810):**
```javascript
// Shows generic suggestions
const inlineSuggestions = item.isSemanticTest && semanticSuggestions.length > 0
    ? `<div style="background: rgba(139, 92, 246, 0.08);">
           💡 AI Test Scenarios - Choose one:
           ${semanticSuggestions.map((s, i) => `${i + 1}. ${s}`).join('<br>')}
       </div>`
    : '';
```

**New (Field-aware):**
```javascript
// Show field-specific suggestions
let inlineSuggestions = '';
if (item.isSemanticTest && window.currentFieldSuggestions) {
    const fieldSugg = window.currentFieldSuggestions[item.index];
    if (fieldSugg && fieldSugg.suggestions) {
        inlineSuggestions = `
            <div style="background: rgba(139, 92, 246, 0.08); padding: 12px; border-radius: 6px; margin-top: 8px;">
                <div style="font-weight: 600; margin-bottom: 8px;">
                    💡 Boundary Tests for ${fieldSugg.field_type} field:
                </div>
                ${fieldSugg.suggestions.map((s, i) => `
                    <div style="padding: 4px 0; cursor: pointer;" onclick="document.getElementById('input-${item.index}').value='${s.value.replace(/'/g, "\\'")}'; this.style.background='#7C3AED20';">
                        ${i + 1}. <code>${s.value}</code> - ${s.description}
                    </div>
                `).join('')}
            </div>
        `;
    }
}
```

---

## Training the System

### Option 1: Rule-Based (Quick Start)

Use the `BOUNDARY_DATA` dictionary above. No training needed.

### Option 2: ML-Powered (Advanced)

1. **Create training dataset**: Collect examples of valid/invalid data for each field type
2. **Train per field type**: Email validator, password strength checker, etc.
3. **Use in suggestions**: ML model predicts which boundary cases are most likely to fail

---

## Benefits

✅ **Field-specific**: Email suggestions for email fields, password suggestions for password fields  
✅ **Security-focused**: Includes SQL injection, XSS, path traversal tests  
✅ **I18N coverage**: Unicode, RTL, emoji tests  
✅ **Boundary testing**: Min/max lengths, edge cases  
✅ **Click-to-fill**: User can click a suggestion to auto-fill the field  
✅ **Categorized**: Groups tests by invalid, weak, security, edge_case, etc.

---

## Quick Win: Immediate Implementation

For now, add this to the frontend to show field-aware suggestions:

1. Add field type detection in JavaScript (email, password keywords)
2. Hard-code boundary data arrays in frontend
3. Display per-field suggestions in modal

This gives immediate value while you build the backend training pipeline.
