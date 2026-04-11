#!/usr/bin/env python
"""
ML Semantic Analysis - Quick Setup Script

Extracts training data and trains ML models.
Run this once to enable ML-powered semantic analysis.
"""

import sys
import os
from pathlib import Path

def main():
    print("\n" + "="*60)
    print("  ML Semantic Analysis - Quick Setup")
    print("="*60 + "\n")
    
    # Change to ml_models directory
    script_dir = Path(__file__).parent
    ml_models_dir = script_dir / "src" / "main" / "python" / "ml_models"
    
    if not ml_models_dir.exists():
        print(f"❌ ERROR: ml_models directory not found at {ml_models_dir}")
        return 1
    
    os.chdir(ml_models_dir)
    
    # Step 1: Extract training data
    print("[1/2] Extracting training data from all sources...")
    print()
    
    try:
        from training_data_extractor import TrainingDataExtractor
        
        extractor = TrainingDataExtractor()
        training_data = extractor.extract_all_training_data()
        extractor.save_training_data(training_data)
        
        print(f"\n✓ Extracted {training_data['metadata']['total_samples']} training samples")
    except Exception as e:
        print(f"\n❌ ERROR: Training data extraction failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    print("\n" + "="*60 + "\n")
    
    # Step 2: Train models
    print("[2/2] Training ML models (this may take 2-5 minutes)...")
    print()
    
    try:
        from semantic_model_trainer import SemanticModelTrainer
        
        trainer = SemanticModelTrainer()
        results = trainer.train_and_save()
        
        print("\n" + "="*60)
        print("  SETUP COMPLETE!")
        print("="*60)
        print(f"\nBest Model: {trainer.best_model_name}")
        print(f"Training Samples: {len(trainer.mlb.classes_)} scenario types learned")
        print("\nNext steps:")
        print("  1. Restart the API server")
        print("  2. Look for: '[INIT] ✓ ML Semantic Analyzer loaded successfully'")
        print("  3. Use Semantic Analysis page to test")
        print("\nFor more information, see: ML_SEMANTIC_ANALYSIS_README.md")
        print()
        
    except Exception as e:
        print(f"\n❌ ERROR: Model training failed: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
