# Placeholder System for Dynamic Values

## Overview

The training dataset (`src/resources/common-web-actions-dataset.json`) now uses **placeholder tokens** instead of hardcoded values. This allows the AI to generate code templates that accept dynamic values from user prompts at runtime.

## Placeholder Tokens

All `sendKeys()` statements in the dataset now use placeholders:

| Placeholder | Usage | Example Prompt |
|------------|-------|----------------|
| `{USERNAME}` | Username fields | "enter johndoe in username field" |
| `{PASSWORD}` | Password fields | "enter MyPass123 in password field" |
| `{EMAIL}` | Email address fields | "enter pvalaboju@vertafore.com in producer-email field" |
| `{FIRST_NAME}` | First name fields | "enter John in firstName field" |
| `{LAST_NAME}` | Last name fields | "enter Smith in lastName field" |
| `{PHONE}` | Phone number fields | "enter 555-1234 in phone field" |
| `{SEARCH_QUERY}` | Search boxes | "enter selenium testing in searchBox" |
| `{TEXT}` | Generic text inputs | "enter some text in input field" |
| `{FILE_PATH}` | File upload fields | "upload C:\\Documents\\file.pdf" |

## How It Works

### 1. **Dataset Training**
The dataset teaches the AI to recognize patterns like:
```json
{
  "code": "driver.findElement(By.id(\"username\")).sendKeys(\"{USERNAME}\");",
  "value": "{USERNAME}",
  "prompt": "enter username"
}
```

### 2. **Runtime Value Extraction**
When user provides a prompt like: **"enter pvalaboju@vertafore.com in producer-email field"**

The `inference_improved.py` code:
- Calls `_extract_input_value(prompt)` 
- Uses regex patterns to extract: `pvalaboju@vertafore.com`
- Replaces `{EMAIL}` with the extracted value
- Generates: `driver.findElement(By.id("producer-email")).sendKeys("pvalaboju@vertafore.com");`

### 3. **Value Extraction Logic** (in `inference_improved.py`)

```python
def _extract_input_value(self, prompt):
    """Extract the value to input from the prompt."""
    prompt = prompt.strip()
    
    # Pattern 1: "enter VALUE in field"
    patterns = [
        r'enter\s+([^\s]+(?:\s+[^\s]+)*?)\s+in\s+',
        r'type\s+([^\s]+(?:\s+[^\s]+)*?)\s+into\s+',
        r'input\s+([^\s]+(?:\s+[^\s]+)*?)\s+in\s+',
    ]
    
    for pattern in patterns:
        match = re.search(pattern, prompt, re.IGNORECASE)
        if match:
            return match.group(1).strip()
    
    # Pattern 2: Email addresses
    email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
    email_match = re.search(email_pattern, prompt)
    if email_match:
        return email_match.group(0)
    
    # Pattern 3: Quoted strings
    quoted_pattern = r'["\']([^"\']+)["\']'
    quoted_match = re.search(quoted_pattern, prompt)
    if quoted_match:
        return quoted_match.group(1)
    
    # Fallback
    return "your_text_here"
```

## Changes Made

### Dataset Updates (10 replacements)

| Line | Old Value | New Placeholder |
|------|-----------|----------------|
| 16 | `"testuser"` | `"{USERNAME}"` |
| 24 | `"password123"` | `"{PASSWORD}"` |
| 53 | `"selenium webdriver"` | `"{SEARCH_QUERY}"` |
| 132 | `"C:\\path\\to\\file.pdf"` | `"{FILE_PATH}"` |
| 168 | `"modal text"` | `"{TEXT}"` |
| 351 | `"John"` | `"{FIRST_NAME}"` |
| 359 | `"Doe"` | `"{LAST_NAME}"` |
| 374 | `"john.doe@example.com"` | `"{EMAIL}"` |
| 382 | `"123-456-7890"` | `"{PHONE}"` |
| 404 | `"pvalaboju@vertafore.com"` | `"{EMAIL}"` |
| 413 | `"Phanindraa$1215"` | `"{PASSWORD}"` |

## Verification

Run this to verify all placeholders:
```powershell
Select-String -Path "src\resources\common-web-actions-dataset.json" -Pattern '\.sendKeys'
```

Expected output: All `sendKeys()` should now use `{PLACEHOLDER}` format (except file paths which are legitimate).

## Next Steps

### 1. **Retokenize the Dataset**
```powershell
python src\main\python\tokenize_dataset.py
```
This creates `tokenized_dataset.json` with placeholder-based training data.

### 2. **Retrain the Model**
```powershell
python src\main\python\train_simple.py
```
This trains the AI to recognize placeholder patterns and generate dynamic code.

### 3. **Restart API Server**
```powershell
# Stop current server (Ctrl+C in terminal)
# Or kill the task
python src\main\python\api_server_improved.py
```
The server loads the trained model on startup.

### 4. **Test with User Prompts**

**Test 1: Producer Email Login**
```
Prompt: "enter pvalaboju@vertafore.com in producer-email field"
Expected Code: driver.findElement(By.id("producer-email")).sendKeys("pvalaboju@vertafore.com");
```

**Test 2: Producer Password**
```
Prompt: "enter Phanindraa$1215 in producer-password field"
Expected Code: driver.findElement(By.id("producer-password")).sendKeys("Phanindraa$1215");
```

**Test 3: Search Query**
```
Prompt: "enter test automation in searchBox"
Expected Code: driver.findElement(By.id("searchBox")).sendKeys("test automation");
```

**Test 4: Generic Username**
```
Prompt: "enter johndoe in username field"
Expected Code: driver.findElement(By.id("username")).sendKeys("johndoe");
```

## Benefits

✅ **Generic Training Data**: Dataset no longer contains user-specific values
✅ **Dynamic Values**: Users provide actual values in prompts at runtime
✅ **Reusable Patterns**: Same pattern works for any user/application
✅ **Better AI Learning**: AI learns the pattern, not specific values
✅ **Privacy**: No hardcoded credentials in training data

## Example Workflow

**Before (Hardcoded):**
- Dataset: `sendKeys("pvalaboju@vertafore.com")`
- Prompt: "enter email in producer-email"
- Generated: `sendKeys("pvalaboju@vertafore.com")` ❌ Always same email!

**After (Placeholders):**
- Dataset: `sendKeys("{EMAIL}")`
- Prompt: "enter john@example.com in producer-email"
- Generated: `sendKeys("john@example.com")` ✅ Uses prompt value!

## Troubleshooting

### Issue: Generated code still uses placeholders
**Solution**: Retrain the model and restart server

### Issue: Value not extracted from prompt
**Solution**: Check prompt format - use "enter VALUE in FIELD" pattern

### Issue: Wrong placeholder used
**Solution**: Add field type keywords to prompt (email/password/username/etc.)

## Documentation Files

Related documentation:
- `CORRECTED_WORKFLOW.md` - Browser Control workflow
- `TROUBLESHOOTING_PROMPTS.md` - Prompt format help
- `BROWSER_AI_WORKFLOW_GUIDE.md` - Complete guide
- `QUICK_REFERENCE.md` - Quick command reference
