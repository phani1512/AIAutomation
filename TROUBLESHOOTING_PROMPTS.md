# 🔧 Troubleshooting: Form Input Prompts

## ❌ Common Issue: "Execution failed: Message:"

This error typically means the AI couldn't find the elements or the browser wasn't ready.

---

## ✅ Solution: Use Specific Prompts

### ❌ Too Vague (Will Fail):
```
enter email test@example.com and password secret123
```
**Problem:** AI doesn't know WHICH fields to use

### ✅ Better (More Specific):
```
enter test@example.com in email field and secret123 in password field
```
**Better:** Specifies "email field" and "password field"

### ⭐ Best (With Locators):
```
enter test@example.com in input field with id email and enter secret123 in input field with id password
```
**Best:** Specifies exact element IDs

---

## 📋 Workflow Checklist

Before entering data, make sure you:

### 1. ✅ Initialize Browser
```
Browser Control Page → Click "Initialize Browser"
Wait for: "✅ CHROME browser initialized successfully!"
```

### 2. ✅ Navigate to Page
```
Browser Control Page
├─ Navigate to URL: https://your-site.com/login
├─ Test Prompt: (leave empty)
└─ Click "Execute in Browser"
Wait for page to load
```

### 3. ✅ Enter Data with Specific Prompts
```
Browser Control Page
├─ Test Prompt: "enter myemail@example.com in email field"
└─ Click "Execute in Browser"

Then:
├─ Test Prompt: "enter mypassword in password field"
└─ Click "Execute in Browser"
```

---

## 🎯 Prompt Templates

### For Email Fields:
```
✅ enter myemail@example.com in email field
✅ enter myemail@example.com in input with id email
✅ enter myemail@example.com in input with name email
✅ type myemail@example.com into email input field
```

### For Password Fields:
```
✅ enter mypassword in password field
✅ enter mypassword in input with id password
✅ enter mypassword in input with type password
✅ type mypassword into password input field
```

### For Text Fields:
```
✅ enter John in first name field
✅ enter Doe in input with id lastName
✅ type 12345 into zip code field
```

### For Combined Actions:
```
✅ enter john@email.com in email field and mypassword in password field then click login button
```

---

## 🔍 Finding Element Locators

### Method 1: Inspect Element in Browser
1. Right-click on the field → "Inspect"
2. Look for `id=`, `name=`, or `class=`
3. Use in prompt: "input with id [value]"

### Method 2: Check Page Source
1. View page source (Ctrl+U)
2. Search for the input field
3. Note the id, name, or class attributes

### Example:
```html
<input id="user-email" name="email" type="email" />
```

**Prompts you can use:**
- `enter test@example.com in input with id user-email`
- `enter test@example.com in input with name email`
- `enter test@example.com in email field`

---

## 💡 Special Characters in Passwords

If your password has special characters like `$`, use quotes in the prompt:

### ✅ Correct:
```
enter "Phanindraa$1215" in password field
```

### ⭐ Even Better:
```
enter Phanindraa$1215 in input field with id password
```

---

## 🐛 Debugging Steps

### If you get "Execution failed: Message:"

**Step 1:** Check browser initialized
```
Look for: "✅ CHROME browser initialized successfully!"
If not, click "Initialize Browser"
```

**Step 2:** Check you're on the right page
```
Prompt: "navigate to https://yoursite.com/login"
Execute
```

**Step 3:** Use more specific prompt
```
Instead of: "enter email and password"
Try: "enter myemail@example.com in email field"
```

**Step 4:** Split into separate steps
```
Step 1: "enter myemail@example.com in email field"
Step 2: "enter mypassword in password field"  
Step 3: "click login button"
```

**Step 5:** Add element identifiers
```
Inspect the page to find IDs, then:
"enter myemail@example.com in input with id email-field"
```

---

## 📊 Example: Complete Login Flow

### Full Working Example:

```
Step 1: Initialize Browser
Browser Control → Click "Initialize Browser"
✅ Browser initialized

Step 2: Navigate
Navigate to URL: https://www.saucedemo.com
Test Prompt: (leave empty)
Execute
✅ Page loaded

Step 3: Enter Username
Test Prompt: enter standard_user in input with id user-name
Execute
✅ Username entered

Step 4: Enter Password
Test Prompt: enter secret_sauce in input with id password
Execute
✅ Password entered

Step 5: Click Login
Test Prompt: click button with id login-button
Execute
✅ Logged in
```

---

## ⚡ Quick Reference

### Basic Form Input Pattern:
```
enter [VALUE] in [FIELD_DESCRIPTION]

Examples:
- enter john@email.com in email field
- enter mypassword in password field
- enter John in first name field
```

### With Element Locators:
```
enter [VALUE] in input with [ATTRIBUTE] [VALUE]

Examples:
- enter john@email.com in input with id email
- enter mypassword in input with name password
- enter John in input with id firstName
```

### Combined Actions:
```
enter [VALUE1] in [FIELD1] and [VALUE2] in [FIELD2] then click [BUTTON]

Example:
- enter john@email.com in email field and mypassword in password field then click login button
```

---

## 🎯 Your Specific Case

### ❌ What didn't work:
```
enter email pvalaboju@vertafore.com and password Phanindraa$1215
```

### ✅ Try this instead:

**Option 1 - Step by Step:**
```
Step 1: enter pvalaboju@vertafore.com in email field
Step 2: enter Phanindraa$1215 in password field
Step 3: click login button
```

**Option 2 - Combined:**
```
enter pvalaboju@vertafore.com in email field and Phanindraa$1215 in password field then click login button
```

**Option 3 - With IDs (inspect page first):**
```
enter pvalaboju@vertafore.com in input with id email and enter Phanindraa$1215 in input with id password then click button with id login
```

---

## 📞 Still Having Issues?

1. Check the "Generated Code" section - what code did the AI create?
2. Check browser console for JavaScript errors
3. Make sure you initialized the browser first
4. Make sure you navigated to the login page
5. Try inspecting the page to find exact element IDs

---

**Remember:** The more specific your prompt, the better the AI can generate working code!
