# 🚀 Quick Reference - Browser Integration

## Start Server
```powershell
python src/main/python/api_server_improved.py
```
**Server URL**: http://localhost:5002

---

## Web Interface Tabs

### 1️⃣ Generate Tab
- Enter prompt → Generate code
- Example: "click login button"

### 2️⃣ Locator Tab
- Paste HTML → Get locator suggestions
- Example: `<button id="submit">Submit</button>`

### 3️⃣ Action Tab
- Select element type → Get action suggestions
- Example: Button → click(), submit()

### 4️⃣ 🌐 Browser Tab (NEW!)
**Initialize Browser**:
- Select: Chrome / Firefox / Edge
- Optional: ☑ Headless mode
- Click: 🚀 Initialize Browser

**Execute Test**:
- URL: https://example.com
- Prompt: "click submit button"
- Click: ▶️ Execute in Browser

**Close**:
- Click: ⏹️ Close Browser

---

## API Endpoints (New)

### Initialize Browser
```bash
curl -X POST http://localhost:5002/browser/initialize \
  -H "Content-Type: application/json" \
  -d '{"browser":"chrome","headless":false}'
```

### Execute Code
```bash
curl -X POST http://localhost:5002/generate \
  -H "Content-Type: application/json" \
  -d '{"prompt":"click login","execute":true,"url":"https://example.com"}'
```

### Close Browser
```bash
curl -X POST http://localhost:5002/browser/close
```

---

## Supported Prompts

✅ **Click**: "click login button"
✅ **Input**: "enter username in field"  
✅ **Select**: "select USA from dropdown"
✅ **Verify**: "verify success message"
✅ **Navigate**: "open https://example.com"
✅ **Wait**: "wait for element"

---

## Python Demo
```python
import requests

API = "http://localhost:5002"

# Initialize
requests.post(f"{API}/browser/initialize", 
              json={"browser":"chrome"})

# Execute
response = requests.post(f"{API}/generate", json={
    "prompt": "click submit button",
    "execute": True,
    "url": "https://example.com"
})

print(response.json())

# Close
requests.post(f"{API}/browser/close")
```

---

## Troubleshooting

**Browser not starting?**
- Install Chrome/Firefox/Edge
- Check internet (driver download)

**port 5002 in use?**
```powershell
netstat -ano | findstr :5002
taskkill /PID <PID> /F
```

**Element not found?**
- Add wait: "wait for button"
- Verify URL is correct

---

## Features at a Glance

| Feature | Status |
|---------|--------|
| Code Generation | ✅ |
| Chrome Support | ✅ |
| Firefox Support | ✅ |
| Edge Support | ✅ |
| Headless Mode | ✅ |
| Real-time Execution | ✅ |
| Screenshot Capture | ✅ |
| Page Info | ✅ |

---

**Need Help?** See `BROWSER_INTEGRATION_GUIDE.md`

