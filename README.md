# AI Automation Testing Framework

Comprehensive AI-powered test automation framework with natural language processing, computer vision, self-healing locators, and semantic code analysis.

## 📂 Project Structure

```
AIAutomation/
│
├── src/                          # 💻 Source Code
│   ├── web/                     # 🌐 Web Frontend (UI)
│   │   ├── pages/               # HTML pages
│   │   ├── js/                  # JavaScript modules
│   │   ├── css/                 # Stylesheets
│   │   └── components/          # Reusable UI components
│   │
│   └── main/python/             # Main application
│   │   ├── core/               # Core engine & utilities
│   │   ├── ai_vision/          # Computer vision & OCR
│   │   ├── test_management/    # Test execution & management
│   │   ├── self_healing/       # Self-healing locators
│   │   ├── semantic_analysis/  # Semantic AI analysis
│   │   ├── generators/         # Code generators
│   │   ├── browser/            # Browser automation
│   │   ├── nlp/                # Natural language processing
│   │   ├── ml_training/        # ML model training
│   │   ├── recorder/           # Test recording
│   │   ├── code_generation/    # Code gen utilities
│   │   ├── api_server_modular.py  # 🚀 Main API server
│   │   └── auth_handler.py     # Authentication
│   │
│   └── scripts/                 # Development utilities
│       ├── debug/              # Debugging tools
│       ├── tests/              # Test scripts
│       ├── validation/         # Validators
│       ├── dataset/            # Dataset tools
│       ├── maintenance/        # Cleanup scripts
│       ├── utils/              # Utilities
│       └── training/           # Training scripts
│
├── resources/                    # 📊 Datasets & Models
│   ├── combined-training-dataset-final.json
│   ├── selenium_dataset.bin
│   ├── code-templates.json
│   └── ... (models, patterns, datasets)
│
├── execution_results/            # 🧪 Test Execution Outputs
│   ├── builder/
│   │   └── screenshots/        # Builder test failure screenshots
│   ├── recorder/
│   │   └── screenshots/        # Recorder test failure screenshots
│   └── README.md               # Execution results documentation
│
├── test_cases/                   # 💾 Saved Test Cases
│   ├── builder/                # Built test cases (JSON + exports)
│   │   ├── *.json             # Test definitions
│   │   └── exports/           # Generated code
│   ├── recorder/               # Recorded test cases (JSON)
│   │   └── *.json             # Recorded actions
│   └── README.md               # Test cases documentation
│
├── test_sessions/                # 📝 Test Sessions (Phase 0)
│
├── test_suites/                  # 📦 Test Suites
│   ├── *.json                 # Suite definitions
│   └── README.md               # Test suites documentation
│
└── ... (config files, docs, etc.)
```

## 🚀 Quick Start

### Start the Server

```bash
# Activate virtual environment
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Start the API server
python src/main/python/api_server_modular.py
```

Or use VS Code task: **"Start API Server"**

### Access the UI

Open your browser to:
- **Main Interface:** http://localhost:5000
- **Test Builder:** http://localhost:5000/pages/advanced-test-builder.html
- **Test Recorder:** http://localhost:5000/pages/recorder.html
- **Semantic Analysis:** http://localhost:5000/pages/semantic-analysis.html

## 🎯 Key Features

### 🧠 AI-Powered
- **Semantic Analysis:** 80%+ confidence code analysis
- **Natural Language Processing:** Generate tests from plain English
- **Computer Vision:** Screenshot-based element detection
- **ML Training:** Custom model training capabilities

### 🔧 Self-Healing
- Automatic locator repair when elements change
- Approval workflow for healing decisions
- Multiple fallback strategies
- Element identity tracking

### 📝 Test Creation
- **Test Builder:** Visual test case builder with prompts
- **Test Recorder:** Chrome extension for recording interactions
- **Multi-Prompt Suites:** Complex test scenarios
- **Code Generation:** Multiple language support (Python, Java, etc.)

### 🧪 Test Execution
- Built-in test executor (no Selenium grid needed)
- Smart browser management
- Screenshot capture on failure
- Detailed execution reports

## 📚 Documentation

- **[Source Code Organization](src/README.md)** - Overview of src/ structure
- **[Main Application Modules](src/main/python/README.md)** - Python modules documentation
- **[Development Scripts](src/scripts/README.md)** - Utility scripts guide
- **[Web Interface](src/web/README.md)** - Frontend documentation

### Quick Reference Guides
- [AI Vision Setup](AI_VISION_SETUP_GUIDE.md)
- [Natural Language Guide](NATURAL_LANGUAGE_GUIDE.md)
- [Self-Healing Tests](SELF_HEALING_TESTS.md)
- [Semantic Analysis](SEMANTIC_QUICK_REFERENCE.md)
- [Test Builder Guide](TEST_BUILDER_FIXES_SUMMARY.md)
- [Recorder Guide](RECORDER_QUICK_START.md)

## 🏗️ Architecture

### Backend (Python/Flask)
- **API Server:** `src/main/python/api_server_modular.py`
- **Modular Design:** 11 organized modules
- **RESTful Endpoints:** Code generation, test execution, browser control
- **ML Integration:** TensorFlow/PyTorch models

### Frontend (HTML/JS)
- **Location:** `src/web/`
- **Framework:** Vanilla JS with Bootstrap
- **Features:** Test Builder, Recorder, Semantic Analysis, Execution UI
- **Real-time:** WebSocket support for live updates

### Data & Resources
- **Datasets:** `resources/combined-training-dataset-final.json`
- **Models:** `resources/selenium_dataset.bin`
- **Templates:** `resources/code-templates.json`
- **Patterns:** `resources/element-locator-patterns.json`

## 🔧 Development

### Project Organization

All Python code is under `src/`:
- **Application:** `src/main/python/` - Main modules
- **Utilities:** `src/scripts/` - Development tools
- **Frontend:** `src/web/` - Web interface

### Importing Modules

```python
# New style (recommended)
from core.inference_improved import ImprovedSeleniumGenerator
from test_management.test_case_builder import get_test_case_builder
from semantic_analysis.semantic_analyzer_enhanced import get_analyzer

# Old style (backward compatible via __init__.py)
from inference_improved import ImprovedSeleniumGenerator
from test_case_builder import get_test_case_builder
```

### Running Scripts

```bash
# From project root
python src/scripts/validation/validate_dataset_structure.py
python src/scripts/tests/test_all_prompts.py
```

## 📊 Screenshot Organization

Test failure screenshots are organized by source:

```
execution_results/
├── builder/screenshots/     # Builder test failures
└── recorder/screenshots/    # Recorder test failures
```

Each screenshot includes source badge in the UI (🎬 Recorder / 🧪 Builder).

## 🎓 How It Works

1. **Input:** Natural language prompt or recorded actions
2. **Analysis:** AI analyzes intent and context
3. **Generation:** Creates robust test code with multiple strategies
4. **Execution:** Runs tests with self-healing capabilities
5. **Reporting:** Captures screenshots and detailed results

## 🛠️ Requirements

- Python 3.8+
- Chrome/Edge browser (for test execution)
- Virtual environment (recommended)

### Install Dependencies

```bash
pip install -r requirements.txt
```

## 📝 License

[Your License Here]

## 🤝 Contributing

[Contributing Guidelines]

---

**Status:** ✅ Production Ready  
**Version:** 3.0 (Organized & Optimized)  
**Last Updated:** March 31, 2026

