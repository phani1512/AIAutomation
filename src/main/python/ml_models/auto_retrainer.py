"""
On-Demand ML Training Module

Performs immediate ML retraining when user requests test case suggestions.
No automatic/scheduled retraining - only on-demand when needed.

Author: AI Automation Framework
Date: April 1, 2026
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class OnDemandTrainer:
    """On-demand ML training for immediate test case analysis."""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            # Navigate from ml_models/ → python/ → main/ → src/ → project_root/
            project_root = Path(__file__).resolve().parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.test_suites_dir = project_root / "test_suites"
        self.training_log_path = project_root / "resources" / "ml_data" / "logs" / "on_demand_training_log.json"
        self.training_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        logger.info(f"[ON-DEMAND-TRAINER] Initialized with test_suites at: {self.test_suites_dir}")
    
    def retrain_with_test_case(self, test_case_id: str) -> Dict:
        """
        Immediately retrain ML model with a specific test case.
        Used when user requests test case expansion/suggestions.
        
        Args:
            test_case_id: ID of the test case to train on
            
        Returns:
            Dict with training results
        """
        logger.info(f"[ON-DEMAND-TRAINER] Retraining with test case: {test_case_id}")
        
        try:
            # Trigger retraining
            result = self.trigger_retraining()
            
            if result['success']:
                logger.info(f"[ON-DEMAND-TRAINER] ✓ Retrained successfully for {test_case_id}")
            else:
                logger.error(f"[ON-DEMAND-TRAINER] ✗ Retraining failed: {result.get('error')}")
            
            return result
            
        except Exception as e:
            logger.error(f"[ON-DEMAND-TRAINER] Error: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def _count_tests_since(self, timestamp: str) -> int:
        """Count test cases added/modified since timestamp (for logging)."""
        cutoff_date = datetime.fromisoformat(timestamp)
        count = 0
        
        if not self.test_suites_dir.exists():
            logger.warning(f"[ON-DEMAND-TRAINER] Test suites directory not found: {self.test_suites_dir}")
            return 0
        
        for test_file in self.test_suites_dir.glob("*/*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(test_file.stat().st_mtime)
                if mtime > cutoff_date:
                    count += 1
            except Exception as e:
                logger.debug(f"[ON-DEMAND-TRAINER] Error checking {test_file}: {e}")
        
        return count
    
    def _load_last_training_info(self) -> Optional[Dict]:
        """Load info about last training run."""
        if not self.training_log_path.exists():
            return None
        
        try:
            with open(self.training_log_path, 'r', encoding='utf-8') as f:
                log = json.load(f)
            return log.get('last_training')
        except Exception as e:
            logger.error(f"[AUTO-RETRAIN] Error loading training log: {e}")
            return None
    
    def record_training(self, num_samples: int, results: Dict):
        """Record successful training run."""
        log_entry = {
            'last_training': {
                'timestamp': datetime.now().isoformat(),
                'num_samples': num_samples,
                'test_suites_scanned': self._count_all_tests(),
                'best_model': results.get('best_model', 'random_forest'),
                'f1_score': results.get('f1_score', 0.0),
                'accuracy': results.get('accuracy', 0.0)
            },
            'history': []
        }
        
        # Append to history
        if self.training_log_path.exists():
            try:
                with open(self.training_log_path, 'r', encoding='utf-8') as f:
                    existing_log = json.load(f)
                if 'last_training' in existing_log:
                    log_entry['history'] = existing_log.get('history', [])
                    log_entry['history'].append(existing_log['last_training'])
                    # Keep only last 20 training runs
                    log_entry['history'] = log_entry['history'][-20:]
            except Exception as e:
                logger.warning(f"[AUTO-RETRAIN] Could not load existing log: {e}")
        
        # Save updated log
        with open(self.training_log_path, 'w', encoding='utf-8') as f:
            json.dump(log_entry, f, indent=2)
        
        logger.info(f"[ON-DEMAND-TRAINER] ✓ Training logged: {num_samples} samples, F1: {results.get('f1_score', 0.0):.4f}")
    
    def _count_all_tests(self) -> int:
        """Count all test cases in test_suites/."""
        if not self.test_suites_dir.exists():
            return 0
        return len(list(self.test_suites_dir.glob("*/*.json")))
    
    def trigger_retraining(self) -> Dict:
        """Trigger on-demand retraining."""
        logger.info("[ON-DEMAND-TRAINER] ========================================")
        logger.info("[ON-DEMAND-TRAINER] Starting on-demand retraining...")
        logger.info("[ON-DEMAND-TRAINER] ========================================")
        
        try:
            # Import training modules
            from .training_data_extractor import TrainingDataExtractor
            from .semantic_model_trainer import SemanticModelTrainer
            
            # Extract training data from test_suites/
            extractor = TrainingDataExtractor(self.project_root)
            training_data = extractor.extract_all_training_data()
            
            total_samples = training_data['metadata']['total_samples']
            logger.info(f"[ON-DEMAND-TRAINER] Extracted {total_samples} training samples")
            
            if total_samples < 1:
                logger.warning(f"[ON-DEMAND-TRAINER] No training samples, skipping training")
                return {'success': False, 'error': 'No training data'}
            
            # Train models
            trainer = SemanticModelTrainer(self.project_root)
            results = trainer.train_and_save()
            
            # Record this training
            self.record_training(
                num_samples=total_samples,
                results=results
            )
            
            logger.info("[ON-DEMAND-TRAINER] ========================================")
            logger.info(f"[ON-DEMAND-TRAINER] ✓ Training completed: F1={results.get('f1_score', 0.0):.4f}")
            logger.info("[ON-DEMAND-TRAINER] ========================================")
            
            return {'success': True, 'results': results}
            
        except Exception as e:
            logger.error(f"[ON-DEMAND-TRAINER] ✗ Failed: {e}", exc_info=True)
            return {'success': False, 'error': str(e)}
    
    def get_training_status(self) -> Dict:
        """Get current training status and statistics."""
        last_training = self._load_last_training_info()
        current_test_count = self._count_all_tests()
        
        if not last_training:
            return {
                'has_trained': False,
                'current_test_count': current_test_count,
                'message': 'No training history found'
            }
        
        new_tests_count = self._count_tests_since(last_training['timestamp'])
        last_training_date = datetime.fromisoformat(last_training['timestamp'])
        days_since = (datetime.now() - last_training_date).days
        
        should_retrain, reason = self.should_retrain()
        
        return {
            'has_trained': True,
            'last_training_date': last_training['timestamp'],
            'days_since_training': days_since,
            'last_f1_score': last_training.get('f1_score', 0.0),
            'last_accuracy': last_training.get('accuracy', 0.0),
            'last_samples': last_training.get('num_samples', 0),
            'current_test_count': current_test_count,
            'new_tests_since_training': new_tests_count,
            'should_retrain': should_retrain,
            'reason': reason,
            'thresholds': {
                'new_tests': self.NEW_TESTS_THRESHOLD,
                'days': self.TIME_THRESHOLD_DAYS
            }
        }


# Singleton instance
_on_demand_trainer = None

def get_on_demand_trainer(project_root: Path = None) -> OnDemandTrainer:
    """Get singleton instance of OnDemandTrainer."""
    global _on_demand_trainer
    if _on_demand_trainer is None:
        _on_demand_trainer = OnDemandTrainer(project_root)
    return _on_demand_trainer
