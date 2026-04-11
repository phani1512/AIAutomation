#!/usr/bin/env python3
"""
ML Model Training & Improvement Script

Train or retrain your ML models to get even better test suggestions.

BEFORE TRAINING:
- Ensure you have test cases saved (recorder/builder/manual)
- Server should be stopped (models will be reloaded after training)

AFTER TRAINING:
- Restart server to load new models
- Test with: python demo_ml_suggestions.py
"""

import sys
import json
import logging
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root / "src" / "main" / "python"))

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

logger = logging.getLogger(__name__)


def check_prerequisites():
    """Check if training prerequisites are met."""
    print("\n🔍 Checking Prerequisites...")
    print("=" * 70)
    
    # Check training data exists
    training_data_path = project_root / "resources" / "ml_data" / "datasets" / "ml_training_data.json"
    
    if training_data_path.exists():
        with open(training_data_path, 'r') as f:
            data = json.load(f)
            sample_count = len(data.get('samples', []))
            print(f"✅ Training data found: {sample_count} samples")
    else:
        print(f"⚠️  Training data not found: {training_data_path}")
        print(f"   Creating sample training data...")
        return False
    
    # Check models directory
    models_dir = project_root / "resources" / "ml_data" / "models" / "ml_models"
    if models_dir.exists():
        print(f"✅ Models directory exists: {models_dir}")
    else:
        print(f"⚠️  Models directory not found, will create: {models_dir}")
    
    return True


def extract_training_data():
    """Extract training data from saved test cases."""
    print("\n📊 Extracting Training Data from Saved Tests...")
    print("=" * 70)
    
    try:
        from ml_models.training_data_extractor import TrainingDataExtractor
        
        extractor = TrainingDataExtractor(project_root)
        training_data = extractor.extract_all_training_data()
        
        sample_count = len(training_data.get('samples', []))
        print(f"✅ Extracted {sample_count} training samples")
        
        return sample_count > 0
        
    except Exception as e:
        print(f"❌ Error extracting training data: {e}")
        return False


def train_new_model():
    """Train a new ML model from scratch."""
    print("\n🎓 Training New ML Model...")
    print("=" * 70)
    
    try:
        from ml_models.semantic_model_trainer import SemanticModelTrainer
        
        trainer = SemanticModelTrainer(project_root)
        
        # Load training data
        print("📖 Loading training data...")
        X, y = trainer.load_training_data()
        
        # Train models
        print("🔧 Training RandomForest model...")
        trainer.train_random_forest(X, y)
        
        print("🔧 Training Gradient Boosting model...")
        trainer.train_gradient_boosting(X, y)
        
        # Evaluate and select best
        print("📊 Evaluating models...")
        trainer.evaluate_models(X, y)
        
        # Save best model
        print(f"💾 Saving best model: {trainer.best_model_name}...")
        trainer.save_best_model()
        
        print(f"\n✅ Training complete!")
        print(f"   Best Model: {trainer.best_model_name}")
        print(f"   Location: {trainer.models_dir}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error training model: {e}")
        import traceback
        traceback.print_exc()
        return False


def retrain_with_feedback():
    """Retrain existing model with user feedback."""
    print("\n🔄 Retraining with User Feedback...")
    print("=" * 70)
    
    try:
        from ml_models.model_retrainer import ModelRetrainer
        
        retrainer = ModelRetrainer(project_root)
        
        print("📊 Collecting user feedback...")
        feedback_count = len(retrainer.feedback_collector.export_training_samples())
        
        if feedback_count == 0:
            print("⚠️  No feedback data found. Using base training data only.")
            return train_new_model()
        
        print(f"✅ Found {feedback_count} feedback samples")
        print("🔧 Retraining model with feedback...")
        retrainer.retrain_with_feedback(feedback_weight=2.0)
        
        print("\n✅ Retraining complete!")
        return True
        
    except Exception as e:
        print(f"❌ Error retraining: {e}")
        import traceback
        traceback.print_exc()
        return False


def show_current_model_info():
    """Display current model information."""
    print("\n📋 Current Model Information")
    print("=" * 70)
    
    metadata_path = project_root / "resources" / "ml_data" / "models" / "ml_models" / "model_metadata.json"
    
    if metadata_path.exists():
        with open(metadata_path, 'r') as f:
            metadata = json.load(f)
        
        print(f"Model Type: {metadata.get('best_model', 'N/A')}")
        print(f"Version: {metadata.get('model_version', 'N/A')}")
        print(f"Feature Count: {metadata.get('feature_count', 'N/A')}")
        print(f"Scenario Labels: {len(metadata.get('scenario_labels', []))}")
        print(f"\n🏷️  Supported Scenarios:")
        for label in metadata.get('scenario_labels', []):
            print(f"   - {label}")
    else:
        print("⚠️  No model metadata found. Model may not be trained yet.")


def interactive_menu():
    """Show interactive training menu."""
    print("\n🤖 ML Model Training Tool")
    print("=" * 70)
    print("\nOptions:")
    print("1. Show current model information")
    print("2. Extract training data from saved tests")
    print("3. Train new model from scratch")
    print("4. Retrain with user feedback")
    print("5. Quick train (recommended for first time)")
    print("0. Exit")
    print()
    
    choice = input("Select option (0-5): ").strip()
    
    if choice == '1':
        show_current_model_info()
        return True
    elif choice == '2':
        extract_training_data()
        return True
    elif choice == '3':
        if check_prerequisites():
            train_new_model()
        else:
            print("\n⚠️  Prerequisites not met. Extracting training data first...")
            if extract_training_data():
                train_new_model()
        return True
    elif choice == '4':
        retrain_with_feedback()
        return True
    elif choice == '5':
        print("\n🚀 Quick Training (Recommended)")
        print("=" * 70)
        print("This will:")
        print("1. Extract training data from your saved tests")
        print("2. Train a new RandomForest model")
        print("3. Save the model for use\n")
        
        confirm = input("Continue? (y/n): ").strip().lower()
        if confirm == 'y':
            if extract_training_data():
                if train_new_model():
                    print("\n✅ SUCCESS! Restart server to use new model:")
                    print("   python src/main/python/api_server_modular.py")
        return True
    elif choice == '0':
        print("\n👋 Goodbye!")
        return False
    else:
        print("\n⚠️  Invalid option")
        return True


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("  ML MODEL TRAINING & IMPROVEMENT")
    print("  Get Better Test Suggestions")
    print("=" * 70)
    
    # Check Python version
    if sys.version_info < (3, 7):
        print("\n❌ Python 3.7+ required")
        sys.exit(1)
    
    # Interactive mode
    try:
        while interactive_menu():
            print("\n" + "-" * 70)
            input("\nPress Enter to continue...")
    except KeyboardInterrupt:
        print("\n\n👋 Interrupted. Goodbye!")
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
