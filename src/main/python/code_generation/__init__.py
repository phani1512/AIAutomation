"""
Code generation package for test automation.

This package provides modular components for:
- Field analysis and detection
- Context-aware test data generation
- Semantic test modifications
- Test code generation (Python/Java)
"""

# Version info
__version__ = '1.0.0'
__author__ = 'AI Automation Team'

# Import key classes for easy access
from .field_analyzer import FieldAnalyzer
from .test_data_generator import TestDataGenerator
from .context_analyzer import ContextAnalyzer
from .semantic_modifier import SemanticModifier

__all__ = [
    'FieldAnalyzer',
    'TestDataGenerator',
    'ContextAnalyzer',
    'SemanticModifier',
]
