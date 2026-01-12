# Dataset Files Usage Guide

## 📊 Overview

The three JSON dataset files in `src/resources/` are used for **training** the AI model, not for runtime code generation. They are preprocessed into binary format and then used to train an n-gram language model.

## 📁 Dataset Files

### 1. **selenium-methods-dataset.json**
**Purpose:** Complete catalog of Selenium WebDriver API methods and patterns

**Contains:**
- WebDriverListener event methods (before/after hooks)
- Locator strategies (By.id, By.xpath, By.cssSelector, etc.)
- Wait strategies (implicit/explicit waits, ExpectedConditions)
- Actions class (hover, drag-and-drop, keyboard actions)
- Select class (dropdown handling)
- Additional APIs (screenshots, cookies, JavaScript execution)

**Size:** 150+ methods with signatures, descriptions, and examples

### 2. **common-web-actions-dataset.json**
**Purpose:** Real-world user interaction patterns and common workflows

**Contains:**
- Login form interactions
- Search functionality
- Dropdown selections
- Checkbox/radio button handling
- File upload patterns
- Modal dialog interactions
- Tab/window navigation
- Alert handling
- Hover menus
- Form validation
- Scroll interactions

**Size:** Common web automation patterns with code examples

### 3. **element-locator-patterns.json**
**Purpose:** Element locator strategies and best practices

**Contains:**
- ID-based locators
- Name-based locators
- Class name locators
- XPath patterns
- CSS selector patterns
- Link text locators
- Partial link text
- Tag name locators

**Size:** Comprehensive locator examples and usage patterns

## 🔄 Data Flow Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: JSON Datasets (Training Data)                      │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌─────────────────────────────────────┐
        │  selenium-methods-dataset.json      │
        │  common-web-actions-dataset.json    │
        │  element-locator-patterns.json      │
        └─────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Tokenization (tokenize_dataset.py)                 │
│  - Loads all 3 JSON files                                  │
│  - Converts to structured text format                      │
│  - Uses tiktoken (GPT-4 tokenizer)                         │
│  - Generates token IDs                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌─────────────────────────────────────┐
        │  selenium_dataset.bin                │
        │  (Binary file with token IDs)        │
        └─────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Model Training                                     │
│  Option A: train_simple.py (N-gram model)                  │
│  Option B: train_slm.py (Transformer model)                │
│  - Reads selenium_dataset.bin                              │
│  - Trains language model                                   │
│  - Saves trained model                                     │
└─────────────────────────────────────────────────────────────┘
                           ↓
        ┌─────────────────────────────────────┐
        │  selenium_ngram_model.pkl            │
        │  (Trained model - pickled)           │
        └─────────────────────────────────────┘
                           ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Runtime Inference (API Server)                     │
│  - Loads selenium_ngram_model.pkl                          │
│  - Uses ImprovedSeleniumGenerator                          │
│  - Generates code suggestions                              │
│  - NO direct use of JSON files                             │
└─────────────────────────────────────────────────────────────┘
```

## 🔧 Detailed Usage

### 1. Tokenization Process

**File:** `src/main/python/tokenize_dataset.py`

```python
class DatasetTokenizer:
    def __init__(self, datasets_dir: str = "src/resources"):
        self.datasets_dir = datasets_dir
        self.tokenizer = tiktoken.get_encoding("cl100k_base")
        
    def process_all_datasets(self):
        dataset_files = [
            "selenium-methods-dataset.json",
            "common-web-actions-dataset.json", 
            "element-locator-patterns.json"
        ]
        # Loads each JSON file
        # Converts to text representation
        # Tokenizes using tiktoken
        # Saves to selenium_dataset.bin
```

**Run:**
```bash
python src/main/python/tokenize_dataset.py
```

**Output:**
- `src/resources/selenium_dataset.bin` - Binary file with token IDs
- Statistics about tokenization (total tokens, vocabulary size, etc.)

### 2. Model Training

**Option A: N-gram Model (Lightweight)**

**File:** `src/main/python/train_simple.py`

```python
class SimpleTransformerTrainer:
    def __init__(self, bin_file='src/resources/selenium_dataset.bin'):
        # Loads tokenized data
        # Trains n-gram language model (default: 4-grams)
        # No GPU required
```

**Run:**
```bash
python src/main/python/train_simple.py
```

**Output:**
- `selenium_ngram_model.pkl` - Trained n-gram model

**Option B: Transformer Model (Advanced)**

**File:** `src/main/python/train_slm.py`

```python
class SeleniumSLM(nn.Module):
    # Transformer-based language model
    # Requires PyTorch
    # GPU optional but recommended
    
dataset = SeleniumDataset(
    bin_file='src/resources/selenium_dataset.bin',
    context_length=256
)
```

**Run:**
```bash
python src/main/python/train_slm.py
```

### 3. Runtime Inference

**File:** `src/main/python/inference_improved.py`

```python
class ImprovedSeleniumGenerator:
    def __init__(self, model_path='selenium_ngram_model.pkl'):
        # Loads TRAINED model (NOT JSON files)
        self.model = NGramLanguageModel(n=4)
        self.model.load(model_path)
        
    def generate_clean(self, prompt, max_tokens=30):
        # Uses loaded model for code generation
        # Template-based + model predictions
```

**Usage in API Server:**
```python
# api_server_modular.py or api_server_improved.py
from inference_improved import ImprovedSeleniumGenerator

generator = ImprovedSeleniumGenerator('selenium_ngram_model.pkl')

# At runtime, JSON files are NOT used
# Only the trained model (.pkl file)
```

## 📝 Summary

### JSON Files → Binary File → Model → Runtime

| Phase | Files Used | Purpose |
|-------|-----------|---------|
| **Training Data** | `*.json` files | Source datasets with Selenium patterns |
| **Tokenization** | `tokenize_dataset.py` | Convert JSON → `selenium_dataset.bin` |
| **Model Training** | `train_simple.py` or `train_slm.py` | Train model on binary data → `.pkl` |
| **Runtime** | `inference_improved.py` | Load `.pkl` model, generate code |

### At Runtime (API Server):

✅ **Used:**
- `selenium_ngram_model.pkl` (trained model)

❌ **NOT Used:**
- `selenium-methods-dataset.json`
- `common-web-actions-dataset.json`
- `element-locator-patterns.json`
- `selenium_dataset.bin`

The JSON files are only needed if you want to:
1. Retrain the model
2. Update the training data
3. Experiment with different datasets

## 🔄 When to Update JSON Files

Update these files when:
- New Selenium API methods are released
- You want to add custom automation patterns
- You want to improve code generation quality
- You want to support new web interaction patterns

Then re-run the pipeline:
```bash
# Step 1: Tokenize updated JSON files
python src/main/python/tokenize_dataset.py

# Step 2: Retrain the model
python src/main/python/train_simple.py

# Step 3: Restart API server (auto-loads new model)
python src/main/python/api_server_modular.py
```

## 💡 Key Insights

1. **JSON files are training data only** - Like a textbook for the AI
2. **Binary file is preprocessed data** - Faster to load during training
3. **PKL file is the trained brain** - What the API server uses
4. **Runtime uses templates + model** - Hybrid approach for better quality

## 📊 File Sizes (Typical)

```
selenium-methods-dataset.json      ~500 KB
common-web-actions-dataset.json    ~300 KB
element-locator-patterns.json      ~200 KB
selenium_dataset.bin               ~2-5 MB (tokenized)
selenium_ngram_model.pkl           ~10-50 MB (trained model)
```

## 🎯 Conclusion

The JSON dataset files are **not used at runtime**. They are preprocessed into a binary format, then used to train the AI model. The API server only loads the trained model file (`.pkl`) for code generation.

Think of it like:
- **JSON files** = Textbooks
- **Tokenization** = Converting to study notes
- **Training** = Student learning from notes
- **Model file** = Student's knowledge (brain)
- **Runtime** = Student answering questions (no need for textbooks anymore)
