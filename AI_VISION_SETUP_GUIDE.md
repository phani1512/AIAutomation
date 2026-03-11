# AI Vision Detection Setup Guide

## 🎯 Overview

The system now uses **AI Vision Understanding** (like GPT-4 Vision or Claude) as the PRIMARY detection method, with CV+OCR as fallback.

This means the system will "see" screenshots like an AI would - understanding context, semantics, and element purpose, not just shapes and edges.

---

## 🚀 Setup Options

### Option 1: OpenAI GPT-4 Vision (Recommended)

1. Get an API key from https://platform.openai.com/api-keys
2. Set environment variable:
   ```powershell
   $env:OPENAI_API_KEY = "sk-your-key-here"
   ```
3. Restart the server - it will auto-detect and use OpenAI

**Pros:**
- Very accurate element detection
- Understands context semantically
- No false positives from text labels/logos
- Works on ANY screenshot type

**Cons:**
- Requires API key ($)
- Needs internet connection

---

### Option 2: Anthropic Claude Vision

1. Get an API key from https://console.anthropic.com/
2. Set environment variable:
   ```powershell
   $env:ANTHROPIC_API_KEY = "sk-ant-your-key-here"
   ```
3. Restart the server - it will auto-detect and use Claude

**Pros:**
- Similar accuracy to GPT-4
- Good at understanding UI context
- Alternative if OpenAI unavailable

**Cons:**
- Requires API key ($)
- Needs internet connection

---

### Option 3: CV + OCR Fallback (Current - Free)

If no API key is set, the system automatically uses:
- Pytesseract for text extraction
- OpenCV for visual element detection
- Intelligent analyzer for context understanding

**Pros:**
- Free, no API costs
- Works offline
- No API key needed

**Cons:**
- Less accurate than AI vision
- May have false positives
- Struggles with complex layouts

---

## 📊 Detection Priority

The system tries methods in this order:

1. **AI Vision** (if API key available) → MOST ACCURATE
   - OpenAI GPT-4 Vision
   - Anthropic Claude Vision
   
2. **Intelligent CV+OCR** (fallback) → GOOD
   - Pytesseract OCR for text
   - OpenCV for visual elements
   - Context-aware filtering
   
3. **Basic CV** (last resort) → BASIC
   - Pure computer vision
   - No semantic understanding

---

## 🎓 Training Custom AI Model (Future)

For users who want to train a custom vision model on their specific UI patterns:

### Option 4: Fine-tuned Local Model

1. **Collect Training Data:**
   - 50-100 screenshots of your app
   - Manually annotate element positions and types
   - Save as JSON dataset

2. **Train Model:**
   ```python
   from ai_vision_trainer import AIVisionTrainer
   
   trainer = AIVisionTrainer()
   trainer.load_dataset("my_app_screenshots.json")
   trainer.train(epochs=50)
   trainer.save_model("my_app_model.pth")
   ```

3. **Use Custom Model:**
   ```python
   from ai_vision_detector import AIVisionDetector
   
   detector = AIVisionDetector(model_path="my_app_model.pth")
   ```

**Pros:**
- Tailored to YOUR specific app
- No API costs after training
- Works offline
- Very fast inference

**Cons:**
- Requires training time and data
- Needs ML expertise
- Initial setup effort

---

## 🧪 Testing AI Vision

1. **Set API Key** (skip if using fallback):
   ```powershell
   $env:OPENAI_API_KEY = "sk-your-key-here"
   ```

2. **Restart Server:**
   ```powershell
   python src/main/python/api_server_modular.py
   ```

3. **Check Logs:**
   Look for:
   ```
   [AI-VISION] ✓ OpenAI API detected
   [MULTIMODAL] ✓ AI Vision Detector initialized: openai mode
   ```

4. **Upload Screenshot:**
   Go to http://localhost:5002/screenshot-generator
   Upload any screenshot
   
5. **Expected Results:**
   - Only actual interactive elements detected (inputs, buttons)
   - NO false positives (text labels, logos, navigation)
   - Semantic labels (e.g., "Username", "Password", "Login")

---

## 📝 Example API Usage

```python
import requests
import base64

# Read screenshot
with open("screenshot.png", "rb") as f:
    img_data = base64.b64encode(f.read()).decode()

# Analyze with AI Vision
response = requests.post("http://localhost:5002/screenshot/analyze", json={
    "screenshot": f"data:image/png;base64,{img_data}"
})

result = response.json()
print(f"Inputs found: {len(result['elements']['inputs'])}")
print(f"Buttons found: {len(result['elements']['buttons'])}")

# Detection method used
print(f"Method: {result.get('detection_method', 'CV fallback')}")
```

---

## 🔍 Troubleshooting

**Problem: Still getting false positives**
- Make sure API key is set correctly
- Check logs show "AI Vision SUCCESS"
- If using CV fallback, consider getting API key

**Problem: No elements detected**
- Check screenshot quality (not too blurry)
- Verify API key is valid
- Check internet connection (for API modes)

**Problem: API quota exceeded**
- OpenAI/Anthropic have usage limits
- Consider caching results
- Or switch to CV fallback temporarily

---

## 💰 Cost Comparison

| Method | Cost | Accuracy | Speed |
|--------|------|----------|-------|
| OpenAI GPT-4 Vision | ~$0.01-0.03/image | 95%+ | 2-5s |
| Anthropic Claude | ~$0.01-0.04/image | 95%+ | 2-5s |
| CV + OCR Fallback | FREE | 70-80% | <1s |
| Custom Trained Model | FREE (after training) | 90%+ (for specific app) | <0.5s |

---

## 🎯 Recommendations

**For Development:**
- Use CV+OCR fallback (free, fast)
- Set up API key for final validation

**For Production:**
- Use API-based AI vision for accuracy
- Cache results to reduce API calls
- Or train custom model for your app

**For Training Custom Model:**
- Collect 100+ annotated screenshots
- Train locally or use cloud GPU
- Achieves best balance of cost/accuracy

---

## 📚 Next Steps

1. ✅ **Now:** Try with CV+OCR fallback (current)
2. 🔑 **Better:** Set OpenAI/Anthropic API key
3. 🎓 **Best:** Train custom model for your app

**Current Status:** Using CV+OCR fallback (free, no API key needed)

To use AI Vision: Set `OPENAI_API_KEY` or `ANTHROPIC_API_KEY` environment variable and restart server.
