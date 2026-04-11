# Source Code Organization

This directory contains all Python source code for the AI Automation Testing Framework.

## 📂 Directory Structure

**Note:** This README describes the `src/` directory only. See project root for the complete structure.

```
src/
├── web/                 # Web frontend (HTML/JS/CSS)
│   ├── pages/          # HTML pages
│   ├── js/             # JavaScript modules
│   ├── css/            # Stylesheets
│   └── components/     # Reusable UI components
│
├── main/
│   └── python/          # Main application code
│       ├── core/        # Core utilities & patterns
│       ├── ai_vision/   # Vision, OCR, screenshots
│       ├── test_management/  # Test cases & execution
│       ├── self_healing/     # Self-healing locators
│       ├── semantic_analysis/  # Semantic analysis
│       ├── generators/  # Code generators
│       ├── browser/     # Browser automation
│       ├── nlp/         # Natural language processing
│       ├── ml_training/ # ML training & datasets
│       ├── recorder/    # Test recording
│       ├── code_generation/  # Code generation utilities
│       ├── api_server_modular.py  # Main Flask API server
│       └── auth_handler.py  # Authentication
│
└── scripts/             # Development & utility scripts
    ├── debug/          # Debugging tools
    ├── tests/          # Test scripts
    ├── validation/     # Validation tools
    ├── dataset/        # Dataset processing
    ├── maintenance/    # Cleanup scripts
    ├── migration/      # Migration scripts
    ├── utils/          # Utilities
    ├── fixes/          # Fix scripts
    └── training/       # Model training tools
```

**Other project folders (at root level):**
- `resources/` - Datasets, models, templates
- `execution_results/` - Test execution outputs
  - `builder/screenshots/` - Builder test failure screenshots
  - `recorder/screenshots/` - Recorder test failure screenshots
- `test_cases/` - Saved test cases

## 🎯 Main Application

**Entry Point:** `src/main/python/api_server_modular.py`

**Web Interface:** See `src/web/README.md`

The main application is organized into logical modules:

### Core Modules
- **core/** - Core engine, inference, dataset matching, patterns
- **ai_vision/** - Computer vision, OCR, screenshot analysis
- **test_management/** - Test case building, execution, session management
- **self_healing/** - Self-healing locators and approval workflows
- **semantic_analysis/** - Semantic code analysis (80%+ confidence)
- **generators/** - Code and test generators
- **browser/** - Browser automation and management
- **nlp/** - Natural language processing and templates
- **ml_training/** - Model training and dataset tools
- **recorder/** - Test recording functionality
- **code_generation/** - Code generation helpers

### Running the Application

```bash
# From project root
python src/main/python/api_server_modular.py

# Or use VS Code task: "Start API Server"
```

### Importing Modules

All modules support both old-style and new-style imports via `__init__.py` re-exports:

```python
# New style (recommended)
from core.inference_improved import ImprovedSeleniumGenerator
from test_management.test_case_builder import get_test_case_builder
from semantic_analysis.semantic_analyzer_enhanced import get_analyzer

# Old style (backward compatible)
from inference_improved import ImprovedSeleniumGenerator
from test_case_builder import get_test_case_builder
from semantic_analyzer_enhanced import get_analyzer
```

## 🔧 Development Scripts

**Location:** `src/scripts/`

These are standalone utility and development scripts, organized by category:

```bash
# Run from project root
python src/scripts/validation/validate_dataset_structure.py
python src/scripts/tests/test_all_prompts.py
python src/scripts/utils/demo_local_ai.py
```

See [src/scripts/README.md](scripts/README.md) for full documentation.

## 🌐 Web Interface

**Location:** `web/` (at project root)

Contains the web-based UI for the test automation framework:
- Test Builder
- Test Recorder  
- Semantic Analysis
- Test Execution
- Results Viewer

Access at: `http://localhost:5000` when server is running.

## 📊 Resources

**Location:** `resources/` (at project root)

Contains datasets, trained models, and other resources used by the application.

## 🏗️ Organization Principles

1. **Separation of Concerns** - Code organized by functionality
2. **Module Independence** - Each module is self-contained
3. **Backward Compatibility** - Old imports still work via re-exports
4. **Clear Structure** - Easy to navigate and understand
5. **Standard Layout** - Follows Python best practices

## 📝 Documentation

- **This file:** Source code organization overview
- **Main application modules:** See `src/main/python/README.md`
- **Development scripts:** See `src/scripts/README.md`
- **Code generation:** See `src/main/python/code_generation/README.md`
- **Web interface:** See `web/README.md`

## ✅ Benefits of This Organization

- ✅ Clear separation between application code and utilities
- ✅ Easy to find specific functionality
- ✅ Modular architecture supports better testing
- ✅ New developers can navigate the codebase easily
- ✅ Follows standard Python project structure
- ✅ Maintains backward compatibility with existing code
