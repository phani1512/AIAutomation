"""
ML Models Package for Semantic Analysis

Provides machine learning-powered semantic analysis that learns
from your testing patterns and continuously improves with feedback.

Components:
- training_data_extractor: Extract training data from all sources
- semantic_model_trainer: Train ML models
- ml_semantic_analyzer: ML-powered semantic analyzer
- feedback_collector: Collect user feedback
- model_retrainer: Automated retraining

Quick Start:
    # Extract training data
    from ml_models.training_data_extractor import TrainingDataExtractor
    extractor = TrainingDataExtractor()
    training_data = extractor.extract_all_training_data()
    extractor.save_training_data(training_data)
    
    # Train models
    from ml_models.semantic_model_trainer import SemanticModelTrainer
    trainer = SemanticModelTrainer()
    trainer.train_and_save()
    
    # Use ML analyzer
    from ml_models.ml_semantic_analyzer import MLSemanticAnalyzer
    analyzer = MLSemanticAnalyzer()
    scenarios = analyzer.suggest_scenarios(actions, context=context)
"""

__version__ = '1.0.0'
__author__ = 'AI Automation Team'

# Import main classes for easy access
from .training_data_extractor import TrainingDataExtractor
from .semantic_model_trainer import SemanticModelTrainer
from .ml_semantic_analyzer import MLSemanticAnalyzer
from .feedback_collector import FeedbackCollector
from .model_retrainer import ModelRetrainer

__all__ = [
    'TrainingDataExtractor',
    'SemanticModelTrainer',
    'MLSemanticAnalyzer',
    'FeedbackCollector',
    'ModelRetrainer'
]
