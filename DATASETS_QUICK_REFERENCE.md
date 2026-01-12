# Quick Reference: Datasets & Prompts

## ✅ Confirmed: ALL 4 Datasets Active

| # | Dataset | Entries | Status | Prompts Available |
|---|---------|---------|--------|-------------------|
| 1 | selenium-methods-dataset.json | 111 | ✅ Loaded | Yes - API methods |
| 2 | common-web-actions-dataset.json | 23 | ✅ Loaded | Yes - with placeholders |
| 3 | element-locator-patterns.json | 21 | ✅ Loaded | Yes - locator strategies |
| 4 | sircon_ui_dataset.json | **1,582** | ✅ Loaded | Yes - with placeholders |

**TOTAL: 1,737 entries → 468,295 tokens → Trained Model ✅**

---

## Sample Prompts You Can Use

### Sircon-Specific (from sircon_ui_dataset.json)
```
click the business tab
click the get help signing in link
enter {EMAIL} in producer-email field
enter {PASSWORD} in producer-password field
click on producer-login
verify page errors is present
get text from info message
select {STATE} from dropdown
wait and click on element
```

### Generic Actions (from common-web-actions-dataset.json)
```
enter {EMAIL} in email field
enter {PASSWORD} in password field
click login button
navigate to {URL}
verify success message
select option from dropdown
```

### Complete Login Example
```
enter pvalaboju@vertafore.com in producer-email field and enter Phanindraa$1215 in producer-password and click on producer-login
```

---

## Placeholders Available

From both common-web-actions and sircon_ui datasets:

- `{EMAIL}` - Email addresses
- `{PASSWORD}` - Passwords
- `{USERNAME}` - Usernames
- `{NAME}`, `{FIRST_NAME}`, `{LAST_NAME}` - Names
- `{PHONE}` - Phone numbers
- `{ADDRESS}`, `{ADDRESS_LINE2}`, `{CITY}`, `{STATE}`, `{ZIPCODE}` - Address
- `{DATE}` - Dates
- `{AMOUNT}` - Monetary amounts
- `{TEXT}` - Generic text/comments
- `{COMPANY_NAME}` - Company names
- `{URL}` - URLs

---

## Files Confirmed

✅ `src/resources/selenium-methods-dataset.json` (44.86 KB)  
✅ `src/resources/common-web-actions-dataset.json` (13.56 KB)  
✅ `src/resources/element-locator-patterns.json` (14.15 KB)  
✅ `src/resources/sircon_ui_dataset.json` (1,101.41 KB)  
✅ `src/resources/selenium_dataset.bin` (1.79 MB - tokenized)  
✅ `selenium_ngram_model.pkl` (815.35 KB - trained model)  

---

## Configuration Confirmed

File: `src/main/python/tokenize_dataset.py` (Lines 85-107)

```python
dataset_configs = [
    {"filename": "selenium-methods-dataset.json", "weight": 1.0},
    {"filename": "common-web-actions-dataset.json", "weight": 1.5},
    {"filename": "element-locator-patterns.json", "weight": 1.2},
    {"filename": "sircon_ui_dataset.json", "weight": 2.0}  # ✅ INCLUDED
]
```

✅ All datasets configured  
✅ All datasets tokenized (468,295 tokens)  
✅ All datasets trained into model  
✅ All prompts available in application  

---

## Usage

### Test Script
```bash
python test_login_generation.py
```

### API Server
```bash
python src\main\python\api_server_modular.py
```

### Web Interface
```
http://localhost:5001
```

---

**All datasets are loaded and all prompts are available! 🎉**
