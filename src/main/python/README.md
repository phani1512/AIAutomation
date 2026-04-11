# Python Modules Organization

This directory contains the main application code organized into logical modules.

## 📂 Module Structure

### 🎯 core/
Core utilities, patterns, and engine components.
- `action_suggestion_engine.py` - AI-powered action suggestions
- `dataset_matcher.py` - Dataset matching and lookup
- `fallback_strategy.py` - Fallback strategy generation
- `inference_improved.py` - ML inference engine
- `local_ai_engine.py` - Local AI processing
- `locator_utils.py` - Locator utility functions
- `universal_patterns.py` - Universal test patterns

### 👁️ ai_vision/
Computer vision, OCR, and screenshot analysis.
- `ai_vision_detector.py` - AI-powered element detection
- `annotate_screenshots.py` - Screenshot annotation
- `custom_ocr_engine.py` - Custom OCR implementation
- `local_ai_vision.py` - Local AI vision processing
- `ocr_text_extractor.py` - OCR text extraction
- `screenshot_handler_enhanced.py` - Screenshot capture and handling
- `simple_ocr.py` - Simple OCR implementation
- `trained_vision_detector.py` - Trained vision model
- `visual_element_detector.py` - Visual element detection

### 🧪 test_management/
Test case building, execution, and management.
- `test_case_builder.py` - Test case builder/editor
- `test_data_generator.py` - Test data generation
- `test_executor.py` - Test execution engine
- `test_file_manager.py` - Test file management
- `test_session_manager.py` - Session management
- `test_suite_handler.py` - Test suite handling
- `test_suite_runner.py` - Test suite execution

### 🔧 self_healing/
Self-healing locators and approval workflows.
- `advanced_self_healing.py` - Advanced self-healing logic  
- `element_resolver.py` - Element resolution strategies
- `healing_approval.py` - Healing approval workflow
- `self_healing_locator.py` - Self-healing locator engine

### 🧠 semantic_analysis/
Semantic analysis and intelligent matching.
- `intelligent_analyzer.py` - Intelligent code analysis
- `intelligent_prompt_matcher.py` - Prompt matching
- `semantic_analyzer_enhanced.py` - Enhanced semantic analyzer (80%+ confidence)
- `semantic_analyzer_optimized.py` - Optimized analyzer
- `semantic_handler.py` - Semantic analysis handler

### ⚙️ generators/
Code and test generators.
- `code_generator.py` - Main code generator
- `comprehensive_code_generator.py` - Comprehensive code gen
- `comprehensive_test_generator.py` - Comprehensive test gen
- `direct_test_generator.py` - Direct test generation
- `fallback_code_generator.py` - Fallback code generation
- `generation_handler.py` - Generation request handler
- `generation_handler_reference.py` - Reference implementation
- `multimodal_generator.py` - Multimodal generation (vision + NLP)
- `page_object_generator.py` - Page Object Model generation
- `simple_screenshot_test_generator.py` - Screenshot-based tests
- `smart_locator_generator.py` - Smart locator generation
- `universal_test_generator.py` - Universal test generator

### 🌐 browser/
Browser automation and management.
- `browser_executor.py` - Browser execution engine
- `browser_handler.py` - Browser request handler
- `smart_browser_manager.py` - Smart browser session management
- `url_monitor.py` - URL monitoring and tracking

### 💬 nlp/
Natural language processing and template handling.
- `language_converter.py` - Language conversion (Java/Python/etc)
- `natural_language_processor.py` - NLP for test generation
- `smart_prompt_handler.py` - Smart prompt processing
- `template_engine.py` - Template rendering
- `template_parameter_extractor.py` - Extract parameters from templates

### 🤖 ml_training/
Machine learning training and dataset management.
- `create_finetuning_data.py` - Create fine-tuning datasets
- `integrate_page_helper_datasets.py` - Page helper integration  
- `test_page_helper_training.py` - Page helper training
- `train_simple.py` - Simple model training
- `train_vision_model.py` - Vision model training
- `validate_and_clean_datasets.py` - Dataset validation/cleanup

### 📹 recorder/
Test recording functionality.
- `recorder_handler.py` - Test recorder request handler

### 📝 code_generation/
Code generation utilities (already organized).
- `context_analyzer.py` - Context analysis
- `field_analyzer.py` - Form field analysis
- `semantic_modifier.py` - Semantic code modification
- `test_data_generator.py` - Test data generation

### 📄 Root Level
Main server and authentication.
- `api_server_modular.py` - **Main API server** (Flask app)
- `auth_handler.py` - Authentication handler

## 🔗 Import Examples

All modules are accessible via their package paths:

```python
# Core utilities
from core.dataset_matcher import DatasetMatcher
from core.fallback_strategy import FallbackStrategyGenerator
from core.inference_improved import ImprovedSeleniumGenerator

# Test management
from test_management.test_case_builder import get_test_case_builder
from test_management.test_executor import execute_test
from test_management.test_suite_runner import get_test_runner

# AI Vision
from ai_vision.screenshot_handler_enhanced import screenshot_bp
from ai_vision.visual_element_detector import VisualElementDetector

# Self-healing
from self_healing.healing_approval import get_approval_workflow
from self_healing.element_resolver import ElementResolver

# Semantic analysis
from semantic_analysis.semantic_analyzer_enhanced import get_analyzer
from semantic_analysis.intelligent_prompt_matcher import get_matcher

# Generators
from generators.code_generator import generate_code
from generators.multimodal_generator import MultimodalGenerator

# Browser
from browser.browser_executor import BrowserExecutor
from browser.smart_browser_manager import SmartBrowserManager

# NLP
from nlp.natural_language_processor import NaturalLanguageProcessor
from nlp.smart_prompt_handler import SmartPromptHandler

# Recorder
from recorder.recorder_handler import RecorderHandler
```

## 📋 Migration Notes

### Previous Structure
All files were in the flat `src/main/python/` directory.

### New Structure  
Files are organized into logical modules by functionality.

### Backward Compatibility
- All `__init__.py` files use `from .module import *` to re-export
- Main `api_server_modular.py` imports updated to use new paths
- External scripts should update imports to use new module paths

## 🚀 Running the Server

The main entry point remains the same:

```bash
python src/main/python/api_server_modular.py
```

Or use the provided task:
```bash
# VS Code Task: "Start API Server"
```

## 📊 Statistics

- **Total Modules**: 11 organized folders
- **Total Files**: ~65 Python files
- **Root Files**: 2 (api_server_modular.py, auth_handler.py)
- **Organized Files**: ~63 files in modules

## ✅ Verification

All imports have been updated and verified. The application should work exactly as before with improved code organization.
