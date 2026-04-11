# Development Scripts

This directory contains utility, test, and maintenance scripts organized by purpose.

**Location:** `src/scripts/` (moved from root-level `scripts/` for better organization)

All Python code is now under `src/`:
- `src/main/python/` - Main application code
- `src/scripts/` - Development and utility scripts

## Directory Structure

### 📁 debug/
Debug and diagnostic scripts for troubleshooting issues.
- `debug_500_error.py` - Debug 500 errors
- `debug_alternatives.py` - Debug alternative element selection
- `debug_flow.py` - Debug workflow flows
- `debug_select_option.py` - Debug select option functionality
- `debug_table_issue.py` - Debug table-related issues
- `design_decision_explanation.py` - Explain design decisions

### 📁 tests/
Test scripts for various features and components.
- `test_all_prompts.py` - Test all prompt types
- `test_alternatives_*.py` - Test alternative element handling
- `test_api_direct.py` - Direct API testing
- `test_browser_detection.py` - Browser detection tests
- `test_code_generation.py` - Code generation tests
- `test_fallback_*.py` - Fallback mechanism tests
- `test_language_conversion.py` - Language conversion tests
- `comprehensive_test.py` - Comprehensive system tests
- `comprehensive_workflow_test.py` - Workflow integration tests
- `complete_verification.py` - Complete verification suite

### 📁 validation/
Validation and verification scripts.
- `validate_button_patterns.py` - Validate button patterns in dataset
- `validate_dataset_structure.py` - Validate dataset structure
- `validate_dropdowns.py` - Validate dropdown patterns
- `verify_test_builder.py` - Verify test builder functionality

### 📁 dataset/
Dataset processing and enhancement scripts.
- `add_fallbacks_all_categories.py` - Add fallbacks to all categories
- `enhance_dataset_with_examples.py` - Enhance dataset with examples
- `expand_dataset_advanced.py` - Advanced dataset expansion
- `generalize_dataset.py` - Generalize dataset entries
- `normalize_xpath_patterns.py` - Normalize XPath patterns

### 📁 maintenance/
Cleanup and maintenance scripts.
- `aggressive_cleanup.py` - Aggressive cleanup of unused code
- `cleanup_whitespace.py` - Clean up whitespace
- `clean_inference.py` - Clean inference-related code
- `remove_all_helper_methods.py` - Remove helper methods
- `remove_all_placeholders.py` - Remove placeholder code
- `remove_corrupted_legacy.py` - Remove corrupted legacy code
- `remove_dead_code.py` - Remove dead code
- `remove_originals.py` - Remove original backup files
- `remove_orphaned_code.py` - Remove orphaned code
- `remove_problematic_entries.py` - Remove problematic dataset entries
- `remove_truncated_entries.py` - Remove truncated entries

### 📁 migration/
Migration and replacement scripts.
- `replace_dataset_methods.py` - Replace dataset methods
- `replace_universal_methods.py` - Replace universal methods
- `restore_templates.py` - Restore template files

### 📁 utils/
Utility and demonstration scripts.
- `demo_local_ai.py` - Demo local AI capabilities
- `enhanced_fuzzy_matcher.py` - Enhanced fuzzy matching
- `fuzzy_matching_demo.py` - Fuzzy matching demonstration
- `extract_all_prompts.py` - Extract all prompts from code
- `extract_nested_prompts.py` - Extract nested prompts
- `generate_doc_pdf.py` - Generate PDF documentation
- `quick_summary.py` - Quick project summary
- `search_producer_login.py` - Search producer login functionality
- `why_ml_training_would_fail.py` - Explain ML training limitations

### 📁 fixes/
One-off fix scripts for specific issues.
- `find_broken_code.py` - Find broken code patterns
- `find_click_on.py` - Find click_on method usage
- `fix_extra_parens.py` - Fix extra parentheses

### 📁 training/
Model training scripts.
- `retrain_model.py` - Retrain ML models

## Usage

All scripts are standalone and can be run from the project root:

```bash
# From project root
python src/scripts/debug/debug_500_error.py
python src/scripts/tests/test_all_prompts.py
python src/scripts/validation/validate_dataset_structure.py

# Or navigate to src/scripts first
cd src/scripts
python debug/debug_500_error.py
```

**Note:** If a script needs to import from the main application, it should add the parent path:
```python
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'main', 'python'))
from test_management.test_case_builder import TestCaseBuilder
```

## Notes

- Scripts maintain their original functionality and paths
- Main application code remains in `src/main/python/`
- These scripts are for development, testing, and maintenance purposes
- Most scripts are historical/deprecated but kept for reference
