# CRITICAL FIX - Install Tesseract OCR

## The ROOT CAUSE of your issue:

**Tesseract OCR is NOT installed**, so the system cannot read text labels from screenshots!

Without OCR:
- Can't extract "Email" and "Password" labels ❌
- Can't detect it's a LOGIN page ❌  
- Generates generic FORM tests instead ❌
- Uses bad XPath locators instead of `By.id("email")` ❌

## SOLUTION: Install Tesseract OCR

### Step 1: Download Tesseract
1. Go to: https://github.com/UB-Mannheim/tesseract/wiki
2. Download: **tesseract-ocr-w64-setup-5.3.3.20231005.exe** (or latest version)
3. Run the installer

### Step 2: Install Tesseract
1. During installation, note the installation path (default: `C:\Program Files\Tesseract-OCR\`)
2. **IMPORTANT**: Check the box to "Add to PATH" during installation
3. Complete the installation

### Step 3: Verify Installation
Open PowerShell and run:
```powershell
tesseract --version
```

You should see:
```
tesseract 5.3.3
```

### Step 4: Configure Python
If Tesseract is NOT in your PATH, run this in PowerShell:
```powershell
$env:PATH += ";C:\Program Files\Tesseract-OCR"
[System.Environment]::SetEnvironmentVariable('PATH', $env:PATH, 'User')
```

### Step 5: Restart Your Server
```powershell
Stop-Process -Name python* -Force -ErrorAction SilentlyContinue
Start-Sleep -Seconds 2
$env:PYTHONIOENCODING='utf-8'
python src/main/python/api_server_modular.py
```

### Step 6: Test with Hard Refresh
1. Go to: http://localhost:5002/screenshot-generator
2. Press **Ctrl + Shift + R** (hard refresh)
3. Upload your SIRCON login screenshot
4. Click "Generate Code"

## Expected Results AFTER Installing Tesseract:

Server logs will show:
```
[OCR] ✓ Input 0: Found label 'Email'
[OCR] ✓ Input 1: Found label 'Password'
[SIMPLE-GEN] Detected LOGIN page (has_password=True)
[SCREENSHOT] Generated 14 test methods
```

Generated code will have:
```java
// ✓ Correct test names
testSuccessfulLogin()
testLoginWithEmptyFields()
testLoginWithWrongPassword()

// ✓ Smart locators
driver.findElement(By.id("email"))
driver.findElement(By.id("password"))

// ✓ Total: 14 comprehensive login tests
```

## Alternative: Quick Test Without Installing

If you can't install Tesseract right now, I can create a version that uses **placeholder detection** instead of OCR. It will work for simple SIRCON forms but won't be as accurate.

Let me know:
1. Can you install Tesseract? (recommended - 5 minutes)
2. Or should I create the placeholder-based version? (less accurate but works immediately)
