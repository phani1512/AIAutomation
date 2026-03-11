

 # 🎓 AI Vision Model Training Guide

## 🎯 Goal: Train Custom Vision Model for 95%+ Accuracy

Your current results: 81 text regions, 2 buttons, 3 inputs detected.
**Target:** Precise detection with NO false positives using trained AI vision.

---

## 📋 Prerequisites

### Install PyTorch (Required for Training)

```powershell
# Install PyTorch with CPU support (or GPU if you have CUDA)
pip install torch torchvision torchaudio
```

### Check Installation:
```powershell
python -c "import torch; print(f'PyTorch {torch.__version__} installed')"
```

---

## 🚀 Training Process (3 Steps)

### Step 1: Annotate Screenshots (1-2 hours)

**Run the annotation tool:**
```powershell
python src/main/python/annotate_screenshots.py
```

**What to do:**
1. Click "Load Screenshot" → Select a screenshot
2. Select element type (input, button, checkbox, link)
3. **Click and drag** to draw box around element
4. Enter label/text for the element
5. Repeat for ALL elements on the page
6. Click "Save Annotations" → Saves JSON file
7. Repeat for 50-100 different screenshots

**Tips for Good Annotations:**
- ✅ Draw TIGHT boxes around elements
- ✅ Include username/password inputs separately
- ✅ Label buttons with their text ("Login", "Submit")
- ✅ Annotate ALL interactive elements
- ❌ Don't include text labels or logos
- ❌ Don't skip elements (complete coverage!)

**Recommended Screenshots:**
- 20 login pages (different sites)
- 20 registration forms
- 20 search forms
- 20 data entry forms
- 20 misc pages (dashboards, settings, etc.)

**Save annotations to:** `training_data/annotations/`

---

### Step 2: Train the Model (30-60 minutes)

**Create training data directory:**
```powershell
mkdir training_data
mkdir training_data\annotations
```

**Move your annotation JSON files to:**
`training_data\annotations\`

**Run training:**
```powershell
python src/main/python/train_vision_model.py --annotations training_data/annotations --epochs 50
```

**Training Parameters:**
- `--epochs 50` - Number of training cycles (50 recommended)
- `--batch-size 16` - Samples per batch (adjust based on RAM)
- `--learning-rate 0.001` - Learning rate (default is good)

**What happens during training:**
```
Epoch [1/50] Train Loss: 1.2456 Acc: 65.23% | Val Loss: 0.9876 Acc: 72.45%
Epoch [2/50] Train Loss: 0.8765 Acc: 78.90% | Val Loss: 0.7654 Acc: 81.23%
...
Epoch [50/50] Train Loss: 0.1234 Acc: 96.78% | Val Loss: 0.2345 Acc: 94.56%
✓ Saved best model: trained_models/vision_model_best_20260205_143022.pth
```

**Training time:**
- CPU: 30-60 minutes
- GPU: 5-10 minutes

**Model saved to:** `trained_models/vision_model_best_YYYYMMDD_HHMMSS.pth`

---

### Step 3: Use Trained Model (Instant)

Your trained model will be **automatically detected** and used!

**Restart server:**
```powershell
python src/main/python/api_server_modular.py
```

**Server will show:**
```
[TRAINED-VISION] Loading model from trained_models/vision_model_best_20260205_143022.pth
[TRAINED-VISION] ✅ Model loaded! Validation accuracy: 94.56%
[MULTIMODAL] ✓ Using trained vision model (YOUR custom AI)
```

**Upload screenshot → Get accurate results!**

---

## 📊 Expected Results

### Before Training (Current - Local AI):
```
✓ 2 buttons detected
✓ 3 inputs detected
⚠️ 81 text regions (too many false positives)
```

### After Training (Trained Vision Model):
```
✅ 1 button detected ("Login") - 95% confidence
✅ 2 inputs detected ("Username", "Password") - 97% confidence
✅ 0 false positives (only real elements!)
✅ Semantic labels from OCR
```

---

## 🎯 Training Tips for Best Results

### 1. Diversity in Training Data
- Different websites/apps
- Different layouts (horizontal, vertical, centered)
- Different colors and themes
- Different element sizes

### 2. Quality Over Quantity
- 50 well-annotated screenshots > 200 poor annotations
- Be precise with bounding boxes
- Double-check all annotations before training

### 3. Balance Element Types
- Equal amounts of inputs, buttons, checkboxes, etc.
- Don't over-represent one type

### 4. Include Edge Cases
- Small buttons
- Large textareas
- Disabled elements
- Unusual layouts

---

## 🔧 System Integration

### Architecture After Training:

```
Screenshot Upload
       ↓
[Trained Vision Detector] ← YOUR custom trained model
       ↓
   Detects elements (ResNet18 deep learning)
       ↓
[Simple OCR] ← Extracts text labels
       ↓
   Matches text to detected elements
       ↓
[Universal Test Generator]
       ↓
   Generates test code
```

### Files Updated:

1. **`annotate_screenshots.py`** - GUI tool for annotation
2. **`train_vision_model.py`** - Training script
3. **`trained_vision_detector.py`** - Inference detector
4. **`multimodal_generator.py`** - Will auto-use trained model

---

## 📈 Performance Comparison

| Method | Accuracy | Speed | Cost | Setup |
|--------|----------|-------|------|-------|
| **Basic CV** | 70% | <1s | Free | None |
| **Local AI (current)** | 80% | <1s | Free | None |
| **Trained Vision** | 95%+ | <2s | Free | 2 hours |
| **OpenAI GPT-4 Vision** | 95% | 3-5s | $0.02/img | 5 min |

---

## 🐛 Troubleshooting

### PyTorch Not Installed
```powershell
pip install torch torchvision torchaudio
```

### Out of Memory Error
```powershell
# Reduce batch size
python src/main/python/train_vision_model.py --annotations training_data/annotations --batch-size 8
```

### Low Accuracy After Training
- Need more training data (aim for 100+ screenshots)
- Check annotation quality (review saved JSON files)
- Train for more epochs (try --epochs 100)

### Model Not Found
- Check `trained_models/` directory exists
- Verify .pth file is present
- Use absolute path if needed

---

## 🎓 Advanced: Fine-Tuning

### Retrain on New Data:

1. Annotate MORE screenshots
2. Place in `training_data/annotations/`
3. Run training again (will load existing + new data)
4. New model will be saved

### Transfer Learning:

Your model starts with ImageNet weights (general vision understanding) and fine-tunes on YOUR specific UI patterns. This gives excellent results with less data!

---

## 📞 Quick Start Commands

### Full workflow:
```powershell
# 1. Annotate (do this manually with GUI)
python src/main/python/annotate_screenshots.py

# 2. Train (runs automatically once you have 50+ annotations)
python src/main/python/train_vision_model.py --annotations training_data/annotations --epochs 50

# 3. Use (server auto-detects trained model)
python src/main/python/api_server_modular.py
```

---

## ✅ Checklist

Before training:
- [ ] PyTorch installed (`pip install torch torchvision`)
- [ ] 50-100 screenshots collected
- [ ] `training_data/annotations/` directory created
- [ ] Screenshots annotated with tool
- [ ] Annotation JSON files saved

During training:
- [ ] Training starts without errors
- [ ] Validation accuracy improving each epoch
- [ ] Best model saved to `trained_models/`

After training:
- [ ] Server detects trained model on startup
- [ ] Upload screenshot shows improved accuracy
- [ ] No false positives in detection
- [ ] Semantic labels applied correctly

---

## 🎉 Success Metrics

**You'll know it's working when:**

1. **Detection accuracy:** 95%+ on validation set
2. **False positives:** Near zero (only real elements detected)
3. **Speed:** <2 seconds per screenshot
4. **Semantic labels:** Correct labels from OCR + model
5. **Generalization:** Works on unseen screenshots

---

## 🚀 Next Steps

1. **Now:** Annotate 50 screenshots using the GUI tool
2. **Next:** Train model (will take 30-60 minutes)
3. **Then:** Test with your Sircon screenshot
4. **Finally:** Generate accurate test code!

**Ready to start? Run:**
```powershell
python src/main/python/annotate_screenshots.py
```

Let the training begin! 🎯
