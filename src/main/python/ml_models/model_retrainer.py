"""
Automated Model Retraining Script

Retrains ML models with feedback data to continuously improve accuracy.

Usage:
    python model_retrainer.py              # Retrain with all data
    python model_retrainer.py --feedback-only  # Retrain with feedback only
    python model_retrainer.py --schedule   # Run on schedule ( cron/task scheduler)
"""

import argparse
import logging
from pathlib import Path
from datetime import datetime
import json

from .training_data_extractor import TrainingDataExtractor
from .semantic_model_trainer import SemanticModelTrainer
from .feedback_collector import FeedbackCollector

logger = logging.getLogger(__name__)


class ModelRetrainer:
    """Automated model retraining with feedback integration."""
    
    def __init__(self, project_root: Path = None):
        """Initialize retrainer."""
        if project_root is None:
            # Go up 5 levels: ml_models → python → main → src → project_root
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.extractor = TrainingDataExtractor(project_root)
        self.trainer = SemanticModelTrainer(project_root)
        self.feedback_collector = FeedbackCollector(project_root)
        
        self.retraining_log_path = project_root / "resources" / "ml_data" / "logs" / "retraining_log.json"
    
    def retrain_with_feedback(self, feedback_weight: float = 2.0):
        """
        Retrain model incorporating user feedback.
        
        Args:
            feedback_weight: Weight multiplier for feedback samples (higher = more influence)
        """
        logger.info("[RETRAINER] Starting model retraining with feedback...")
        
        # Step 1: Extract base training data
        logger.info("[RETRAINER] Step 1: Extracting training data...")
        training_data = self.extractor.extract_all_training_data()
        
        # Step 2: Add feedback samples
        logger.info("[RETRAINER] Step 2: Incorporating user feedback...")
        feedback_samples = self.feedback_collector.export_training_samples()
        
        # Weight feedback samples (duplicate to increase importance)
        weighted_feedback = []
        for sample in feedback_samples:
            for _ in range(int(feedback_weight)):
                weighted_feedback.append(sample.copy())
        
        training_data['samples'].extend(weighted_feedback)
        training_data['metadata']['source_breakdown']['feedback'] = len(feedback_samples)
        training_data['metadata']['feedback_samples_weighted'] = len(weighted_feedback)
        training_data['metadata']['total_samples'] = len(training_data['samples'])
        
        logger.info(f"[RETRAINER] Added {len(feedback_samples)} feedback samples (weighted: {len(weighted_feedback)})")
        logger.info(f"[RETRAINER] Total training samples: {training_data['metadata']['total_samples']}")
        
        # Step 3: Save augmented training data
        logger.info("[RETRAINER] Step 3: Saving augmented training data...")
        self.extractor.save_training_data(training_data)
        
        # Step 4: Retrain models
        logger.info("[RETRAINER] Step 4: Retraining ML models...")
        results = self.trainer.train_and_save()
        
        # Step 5: Log retraining
        self._log_retraining(training_data['metadata'], results)
        
        logger.info("[RETRAINER] ✓ Model retraining complete!")
        
        return {
            'success': True,
            'training_samples': training_data['metadata']['total_samples'],
            'feedback_samples': len(feedback_samples),
            'best_model': self.trainer.best_model_name,
            'performance': results[self.trainer.best_model_name]
        }
    
    def retrain_from_scratch(self):
        """Retrain model from scratch with all data."""
        logger.info("[RETRAINER] Starting full model retraining from scratch...")
        
        # Extract all training data
        training_data = self.extractor.extract_all_training_data()
        self.extractor.save_training_data(training_data)
        
        # Train models
        results = self.trainer.train_and_save()
        
        # Log retraining
        self._log_retraining(training_data['metadata'], results)
        
        logger.info("[RETRAINER] ✓ Full model retraining complete!")
        
        return {
            'success': True,
            'training_samples': training_data['metadata']['total_samples'],
            'best_model': self.trainer.best_model_name,
            'performance': results[self.trainer.best_model_name]
        }
    
    def _log_retraining(self, training_metadata: dict, results: dict):
        """Log retraining session."""
        # Load existing log
        if self.retraining_log_path.exists():
            with open(self.retraining_log_path, 'r') as f:
                log = json.load(f)
        else:
            log = {'retraining_sessions': []}
        
        # Add new entry
        entry = {
            'timestamp': datetime.now().isoformat(),
            'training_samples': training_metadata.get('total_samples', 0),
            'source_breakdown': training_metadata.get('source_breakdown', {}),
            'best_model': self.trainer.best_model_name,
            'performance': results.get(self.trainer.best_model_name, {}),
            'all_models': results
        }
        
        log['retraining_sessions'].append(entry)
        log['last_retraining'] = entry['timestamp']
        log['total_retrainings'] = len(log['retraining_sessions'])
        
        # Save log
        self.retraining_log_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.retraining_log_path, 'w') as f:
            json.dump(log, f, indent=2)
        
        logger.info(f"[RETRAINER] Logged retraining session #{log['total_retrainings']}")
    
    def get_retraining_history(self) -> dict:
        """Get history of all retraining sessions."""
        if not self.retraining_log_path.exists():
            return {'retraining_sessions': [], 'total_retrainings': 0}
        
        with open(self.retraining_log_path, 'r') as f:
            return json.load(f)
    
    def should_retrain(self, min_feedback_samples: int = 100, 
                      days_since_last: int = 7) -> bool:
        """
        Determine if model should be retrained.
        
        Args:
            min_feedback_samples: Minimum feedback samples to trigger retraining
            days_since_last: Days since last retraining
        
        Returns:
            True if retraining recommended
        """
        # Check feedback count
        feedback_summary = self.feedback_collector.get_feedback_summary()
        total_feedback = feedback_summary['total_ratings']
        
        if total_feedback >= min_feedback_samples:
            logger.info(f"[RETRAINER] Retraining recommended: {total_feedback} feedback samples")
            return True
        
        # Check time since last retraining
        history = self.get_retraining_history()
        if history['total_retrainings'] > 0:
            last_retraining = history['last_retraining']
            last_date = datetime.fromisoformat(last_retraining)
            days_elapsed = (datetime.now() - last_date).days
            
            if days_elapsed >= days_since_last:
                logger.info(f"[RETRAINER] Retraining recommended: {days_elapsed} days since last retraining")
                return True
        
        logger.info(f"[RETRAINER] Retraining not needed yet (feedback: {total_feedback}, days: {days_elapsed if history['total_retrainings'] > 0 else 'N/A'})")
        return False


def main():
    """Main entry point for retraining script."""
    parser = argparse.ArgumentParser(description='Retrain semantic analysis ML models')
    parser.add_argument('--feedback-only', action='store_true',
                       help='Retrain with feedback data only')
    parser.add_argument('--from-scratch', action='store_true',
                       help='Full retraining from scratch')
    parser.add_argument('--check', action='store_true',
                       help='Check if retraining is recommended')
    parser.add_argument('--auto', action='store_true',
                       help='Automatically retrain if recommended')
    parser.add_argument('--feedback-weight', type=float, default=2.0,
                       help='Weight for feedback samples (default: 2.0)')
    
    args = parser.parse_args()
    
    # Setup logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    retrainer = ModelRetrainer()
    
    # Check mode
    if args.check:
        should_retrain = retrainer.should_retrain()
        print(f"\n{'=' * 60}")
        print(f"Retraining Status: {'RECOMMENDED' if should_retrain else 'NOT NEEDED'}")
        print(f"{'=' * 60}")
        
        feedback_summary = retrainer.feedback_collector.get_feedback_summary()
        print(f"\nFeedback Statistics:")
        print(f"  Total Ratings: {feedback_summary['total_ratings']}")
        print(f"  Useful: {feedback_summary['rating_distribution']['useful']}")
        print(f"  Not Relevant: {feedback_summary['rating_distribution']['not_relevant']}")
        print(f"  Test Results: {feedback_summary['total_test_results']}")
        print(f"  User Suggestions: {feedback_summary['total_user_suggestions']}")
        
        history = retrainer.get_retraining_history()
        print(f"\nRetraining History:")
        print(f"  Total Retrainings: {history['total_retrainings']}")
        if history['total_retrainings'] > 0:
            print(f"  Last Retraining: {history['last_retraining']}")
        
        return
    
    # Auto mode
    if args.auto:
        if retrainer.should_retrain():
            print("\n✓ Retraining recommended - starting...")
            args.feedback_only = True
        else:
            print("\n✓ Retraining not needed - skipping")
            return
    
    # Execute retraining
    try:
        if args.from_scratch:
            print("\n" + "=" * 60)
            print("FULL MODEL RETRAINING")
            print("=" * 60)
            result = retrainer.retrain_from_scratch()
        else:
            print("\n" + "=" * 60)
            print("MODEL RETRAINING WITH FEEDBACK")
            print("=" * 60)
            result = retrainer.retrain_with_feedback(args.feedback_weight)
        
        print("\n" + "=" * 60)
        print("RETRAINING COMPLETE")
        print("=" * 60)
        print(f"\nTraining Samples: {result['training_samples']}")
        if 'feedback_samples' in result:
            print(f"Feedback Samples: {result['feedback_samples']}")
        print(f"Best Model: {result['best_model']}")
        print(f"\nPerformance:")
        for metric, value in result['performance'].items():
            print(f"  {metric}: {value:.4f}")
        
        print("\n✓ Models updated and saved!")
        print("   Restart API server to load new models")
    
    except Exception as e:
        logger.error(f"[RETRAINER] Error during retraining: {e}")
        import traceback
        traceback.print_exc()
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
