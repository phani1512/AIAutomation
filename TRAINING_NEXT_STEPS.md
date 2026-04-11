# 🎓 Training Guide: Page Helper Datasets

## ✅ You Have the Datasets - Now Let's Train!

Your new Page Helper datasets are ready. Here's your **complete training roadmap**.

---

## 🚀 Quick Start (5 Minutes)

### Option 1: Integrate with Existing Training Pipeline

```powershell
# Step 1: Integrate the new datasets
python src/main/python/integrate_page_helper_datasets.py

# Step 2: Tokenize (if needed)
python src/main/python/tokenize_dataset.py

# Step 3: Train your model
python src/main/python/train_simple.py

# Step 4: Test it
# Restart your server and try prompts like:
# "enter John in the Name field"
# "select USA from Country dropdown"
# "check the Terms checkbox"
```

### Option 2: Use for AI API Fine-Tuning (OpenAI/Anthropic)

```powershell
# Create fine-tuning format
python src/main/python/create_finetuning_data.py

# Then upload to OpenAI/Anthropic for fine-tuning
# See section below for details
```

---

## 📊 What Training Approach Should You Use?

Based on your framework, you have **3 options**:

### 1️⃣ **Local N-Gram Model** (Current Approach) ✅ RECOMMENDED TO START
- ✅ **Fast**: Train in seconds
- ✅ **No API costs**: Runs locally
- ✅ **Privacy**: Data stays local
- ⚠️ **Limited**: Pattern matching, not deep understanding
- 📈 **Best for**: Quick prototyping, pattern completion

**When to use**: Testing new patterns, rapid iteration

### 2️⃣ **Fine-Tune OpenAI/Anthropic Model** 💰
- ✅ **Powerful**: Deep language understanding
- ✅ **Flexible**: Handles variations well
- ✅ **Production-ready**: Reliable and robust
- ⚠️ **Costs $$$**: API charges apply
- ⚠️ **Requires API keys**: External dependency

**When to use**: Production deployment, high accuracy needs

### 3️⃣ **Hybrid Approach** 🎯 BEST LONG-TERM
- Use local model for common patterns (fast, free)
- Fall back to AI API for complex cases
- Best of both worlds

---

## 🔧 Detailed Setup: Option 1 (Local Training)

### Prerequisites
```powershell
# Verify you have required files
ls src/resources/page-helper-*.json
ls src/main/python/train_simple.py
```

### Step-by-Step Training

#### 1. **Integrate Datasets** (New Script Created)
```powershell
python src/main/python/integrate_page_helper_datasets.py
```

**This will**:
- ✅ Load your 45 patterns
- ✅ Load your 70 training examples
- ✅ Convert to your training format
- ✅ Merge with existing datasets
- ✅ Create `combined-training-dataset.json`
- ✅ Create `page-helper-prompts.json`

**Expected Output**:
```
✓ Loaded 45 patterns
✓ Loaded 70 training examples
✓ Converted 295 total training entries
✓ Saved combined dataset
```

#### 2. **Tokenize Dataset** (If Needed)
```powershell
python src/main/python/tokenize_dataset.py
```

**Expected**: `tokenized_dataset.json` created

#### 3. **Train Model**
```powershell
python src/main/python/train_simple.py
```

**Expected**: 
```
[TRAIN] Training model...
[TRAIN] Model saved to selenium_ngram_model.pkl
Training complete.
```

#### 4. **Restart Server**
```powershell
# Stop current server (Ctrl+C)
# Restart with:
python src/main/python/api_server_modular.py
```

#### 5. **Test It!**
Open: http://localhost:5001/web/

Try these prompts:
```
✅ "enter John in the Name field"
✅ "select United States from Country dropdown"
✅ "check the I agree checkbox"
✅ "click the Submit button"
✅ "verify Email field shows error"
✅ "search for John Doe in the table"
```

---

## 🤖 Detailed Setup: Option 2 (AI Fine-Tuning)

### For OpenAI GPT-4

First, create the fine-tuning script:

```python
# src/main/python/create_finetuning_data.py
import json
from pathlib import Path

def create_openai_finetuning_data():
    """Convert Page Helper datasets to OpenAI fine-tuning format."""
    
    # Load training dataset
    with open('src/resources/page-helper-training-dataset.json', 'r') as f:
        training_data = json.load(f)
    
    # Convert to OpenAI format
    openai_data = []
    for example in training_data:
        openai_data.append({
            "messages": [
                {"role": "system", "content": "You are a Selenium test automation expert. Convert natural language instructions to Java Page Helper code."},
                {"role": "user", "content": example['input']},
                {"role": "assistant", "content": example['output']}
            ]
        })
    
    # Save in JSONL format (one JSON per line)
    with open('page-helper-finetuning.jsonl', 'w') as f:
        for item in openai_data:
            f.write(json.dumps(item) + '\n')
    
    print(f"✓ Created page-helper-finetuning.jsonl with {len(openai_data)} examples")
    print("\nNext steps:")
    print("1. Upload to OpenAI: openai files create --file page-helper-finetuning.jsonl --purpose fine-tune")
    print("2. Create fine-tune job: openai fine-tuning create --model gpt-4o-mini --file <file-id>")
    print("3. Monitor: openai fine-tuning list")

if __name__ == '__main__':
    create_openai_finetuning_data()
```

**Run it**:
```powershell
python src/main/python/create_finetuning_data.py
```

**Then upload to OpenAI**:
```powershell
# Install OpenAI CLI if needed
pip install openai

# Set API key
$env:OPENAI_API_KEY = "your-key"

# Upload file
openai files create --file page-helper-finetuning.jsonl --purpose fine-tune

# Create fine-tuning job (use the file-id from above)
openai fine-tuning create --model gpt-4o-mini --file file-abc123

# Monitor progress
openai fine-tuning list
```

**Cost Estimate**: ~$5-$20 for 70 examples (varies by tokens)

### For Anthropic Claude

```python
# Currently, Claude doesn't support fine-tuning in the same way
# But you can use these datasets with:
# 1. Few-shot prompting (include examples in prompt)
# 2. Retrieval Augmented Generation (RAG)
# 3. Prompt engineering with the patterns
```

---

## 🎯 Recommended Approach: Start Local, Scale to Cloud

### Phase 1: Local Validation (Week 1)
```powershell
# 1. Integrate datasets
python src/main/python/integrate_page_helper_datasets.py

# 2. Train local model
python src/main/python/train_simple.py

# 3. Test with real scenarios
# Use your web interface to test prompts

# 4. Measure accuracy
# Keep track of successful vs failed generations
```

### Phase 2: Optimize (Week 2)
- Review failed cases
- Add more training examples for weak areas
- Fine-tune prompts and patterns
- Re-train and test

### Phase 3: Production (Week 3+)
- If accuracy is good (>80%): Use local model
- If need better: Fine-tune OpenAI model
- Or use hybrid: local first, API fallback

---

## 📊 How to Measure Success

### Create a Test Suite

```python
# src/main/python/test_page_helper_training.py
import json
import requests

def test_page_helper_prompts():
    """Test model accuracy on Page Helper prompts."""
    
    # Load test prompts
    with open('src/resources/page-helper-prompts.json', 'r') as f:
        prompts = json.load(f)
    
    correct = 0
    total = len(prompts)
    
    for prompt_data in prompts:
        prompt = prompt_data['prompt']
        expected_method = prompt_data['expected_method']
        
        # Call your API
        response = requests.post('http://localhost:5001/generate', 
                                json={'prompt': prompt})
        
        if response.ok:
            generated_code = response.json().get('code', '')
            
            # Check if expected method is in generated code
            if expected_method in generated_code:
                correct += 1
                print(f"✓ {prompt[:50]}")
            else:
                print(f"✗ {prompt[:50]}")
                print(f"  Expected: {expected_method}")
                print(f"  Got: {generated_code[:100]}")
    
    accuracy = (correct / total) * 100
    print(f"\n📊 Accuracy: {accuracy:.1f}% ({correct}/{total})")
    
    return accuracy

if __name__ == '__main__':
    test_page_helper_prompts()
```

**Run tests**:
```powershell
python src/main/python/test_page_helper_training.py
```

**Target Metrics**:
- 🎯 **Good**: 70-80% accuracy
- 🌟 **Great**: 80-90% accuracy  
- 🚀 **Excellent**: 90%+ accuracy

---

## 🔄 Continuous Improvement Loop

```
1. Train → 2. Test → 3. Collect Failed Cases → 4. Add Examples → Repeat
   ↑                                                              ↓
   └──────────────────────────────────────────────────────────────┘
```

### After Each Training Round:

1. **Test all categories**
   - Input fields, dropdowns, checkboxes, etc.
   - Easy, medium, hard examples

2. **Document failures**
   ```json
   {
     "failed_prompt": "check the remember me box",
     "expected": "setCheckboxOn(\"Remember Me\");",
     "got": "clickButton(\"Remember Me\");",
     "reason": "confused checkbox with button"
   }
   ```

3. **Add targeted examples**
   - Add 3-5 similar examples to training set
   - Focus on the specific failure pattern

4. **Re-train and re-test**

---

## 💡 Pro Tips

### 1. **Start Small, Iterate Fast**
```powershell
# Don't wait to perfect the dataset
# Train → Test → Improve → Repeat
python src/main/python/integrate_page_helper_datasets.py && python src/main/python/train_simple.py
```

### 2. **Use Both Datasets**
- `page-helper-patterns-dataset.json` → Pattern matching
- `page-helper-training-dataset.json` → Context understanding

### 3. **Monitor Performance by Category**
```
Input Fields:    85% ✓ Good
Dropdowns:       78% ✓ Good
Checkboxes:      92% ✓ Excellent
Tables:          65% ⚠️ Needs work → Add more examples
```

### 4. **Combine Approaches**
```python
def generate_code(prompt):
    # Try local model first (fast, free)
    local_result = local_model.generate(prompt)
    
    if confidence(local_result) > 0.8:
        return local_result
    else:
        # Fall back to AI API (accurate, costs $)
        return openai_api.generate(prompt)
```

---

## 🎬 Quick Start Commands (Copy-Paste Ready)

```powershell
# Full training pipeline in one go:
python src/main/python/integrate_page_helper_datasets.py ; `
python src/main/python/tokenize_dataset.py ; `
python src/main/python/train_simple.py

# Then restart server
# Ctrl+C to stop current server, then:
python src/main/python/api_server_modular.py
```

---

## 📚 What Each File Does

| File | Purpose | When to Use |
|------|---------|-------------|
| `integrate_page_helper_datasets.py` | Merges new datasets with existing | First time setup, after adding patterns |
| `tokenize_dataset.py` | Prepares data for n-gram model | Before training local model |
| `train_simple.py` | Trains local n-gram model | After tokenization |
| `create_finetuning_data.py` | Creates OpenAI format | When using AI API fine-tuning |
| `test_page_helper_training.py` | Validates model accuracy | After each training round |

---

## 🚨 Troubleshooting

### Issue: "Model not improving"
**Solution**: 
1. Check if datasets loaded correctly
2. Add more examples for failing categories
3. Try AI API fine-tuning instead

### Issue: "Prompts not recognized"
**Solution**:
1. Check prompt variations match user input style
2. Add more natural language variations
3. Review tokenization output

### Issue: "Generated code is wrong"
**Solution**:
1. Review training examples for that pattern
2. Add explicit examples showing correct usage
3. Check if placeholder system is working

---

## ✅ Success Checklist

Before declaring victory, verify:

- [ ] Integration script runs successfully
- [ ] Training completes without errors  
- [ ] Server starts with new model
- [ ] Can generate code for basic prompts
- [ ] Accuracy test shows >70% success
- [ ] All 17 categories tested
- [ ] Edge cases handled
- [ ] Documentation updated

---

## 🎯 Your Next Action

**RIGHT NOW**:
```powershell
python src/main/python/integrate_page_helper_datasets.py
```

**See the results**, then decide:
- ✅ Local model sufficient? → Use it!
- ⚠️ Need better accuracy? → Consider AI fine-tuning
- 🎯 Want best of both? → Hybrid approach

---

## 📞 Need Help?

- Check `PAGE_HELPER_DATASETS_README.md` for details
- Review `PAGE_HELPER_QUICK_REFERENCE.md` for patterns
- See `TROUBLESHOOTING_PROMPTS.md` for common issues

---

**Start training now!** 🚀 Your datasets are ready to go!
