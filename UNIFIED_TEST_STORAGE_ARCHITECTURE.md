# Unified Test Storage & Auto-Training Architecture

**Date:** April 1, 2026  
**Status:** Implementation Plan  
**Goal:** Unified test case storage in test_suites/ with auto-retraining

---

## 🎯 Current Problem

**What's Wrong:**
- ❌ Builder saves to: `test_cases/builder/`
- ❌ Recorder saves to: `test_cases/recorder/`
- ❌ Test Suites folder: Empty
- ❌ ML training reads from `test_cases/` only
- ❌ No auto-training when new tests added
- ❌ In production, no central storage for all test cases

**Why This is a Problem:**
1. Test cases scattered across multiple folders
2. ML model doesn't learn from newly saved tests
3. Test suites folder not used as single source of truth
4. No automatic model improvement over time

---

## ✅ Correct Architecture

### Single Source of Truth: `test_suites/`

```
test_suites/
├── builder/                      # Tests from Test Case Builder
│   ├── test_001_login.json
│   ├── test_002_registration.json
│   └── test_003_checkout.json
│
├── recorded/                     # All recorded tests (from all users)
│   ├── session_001_workflow.json
│   ├── session_002_form_fill.json
│   └── session_003_navigation.json
│   (Note: username stored in test metadata)
│
└── custom_smoke_tests/           # Custom organized suite
    ├── critical_path_001.json
    └── critical_path_002.json
```

**Benefits:**
- ✅ All test cases in ONE location
- ✅ Organized by functionality (suites)
- ✅ Easy for ML training to scan
- ✅ Easy for DB integration later
- ✅ Production-ready structure

---

## 🔧 Implementation Steps

### Step 1: Update Test Case Builder

**File:** `src/main/python/test_management/test_case_builder.py`

**Change:**
```python
# OLD: Save to test_cases/builder/
self.test_cases_dir = project_root / "test_cases" / "builder"

# NEW: Save to test_suites/{suite_name}/
def save_test_case(self, test_case: TestCase, suite_name: str = "default", filename: str = None):
    """Save test case to test_suites folder."""
    # Create suite folder if needed
    suite_dir = self.project_root / "test_suites" / suite_name
    suite_dir.mkdir(parents=True, exist_ok=True)
    
    if filename is None:
        safe_name = "".join(c if c.isalnum() or c in (' ', '_', '-') else '_' 
                           for c in test_case.name)
        filename = f"{test_case.test_case_id}_{safe_name}.json"
    
    filepath = suite_dir / filename
    
    # Add suite metadata
    test_case_dict = test_case.to_dict()
    test_case_dict['suite'] = suite_name
    test_case_dict['saved_to_suite_at'] = datetime.now().isoformat()
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(test_case_dict, f, indent=2, ensure_ascii=False)
    
    logger.info(f"[TEST BUILDER] Saved to suite '{suite_name}': {filepath}")
    return str(filepath)
```

### Step 2: Update Recorder Handler

**File:** `src/main/python/recorder/recorder_handler.py`

**Change:**
```python
# OLD: Save to test_cases/{username}/recorder/
test_dir = project_root / "test_cases" / f"user_{username}" / "recorder"

# NEW: Save to test_suites/recorded/
def save_test_case_to_disk():
    """Save recorded test to test_suites."""
    username = data.get('username', 'default_user')
    suite_name = "recorded"  # Flat structure, username in metadata
    
    # Save to test_suites/recorded/
    suite_dir = project_root / "test_suites" / suite_name
    suite_dir.mkdir(parents=True, exist_ok=True)
    
    test_file = suite_dir / f"{session_id}_{test_name}.json"
    
    # Add metadata
    session_copy['suite'] = suite_name
    session_copy['source'] = 'recorder'
    session_copy['saved_at'] = datetime.now().isoformat()
    
    with open(test_file, 'w', encoding='utf-8') as f:
        json.dump(session_copy, f, indent=2)
```

### Step 3: Update ML Training Data Extractor

**File:** `src/main/python/ml_models/training_data_extractor.py`

**Change:**
```python
# OLD: Read from test_cases/
self.test_cases_dir = project_root / "test_cases"

# NEW: Read from test_suites/
self.test_suites_dir = project_root / "test_suites"

def _extract_from_test_suites(self) -> List[Dict]:
    """Extract training samples from all test suites."""
    samples = []
    
    if not self.test_suites_dir.exists():
        logger.warning(f"[EXTRACTOR] Test suites directory not found: {self.test_suites_dir}")
        return samples
    
    # Scan all suites
    for suite_dir in self.test_suites_dir.iterdir():
        if not suite_dir.is_dir():
            continue
        
        suite_name = suite_dir.name
        
        # Scan all test cases in suite
        for test_file in suite_dir.glob("*.json"):
            try:
                with open(test_file, 'r', encoding='utf-8') as f:
                    test_data = json.load(f)
                
                # Extract features and labels
                sample = self._extract_sample_from_test(test_data, suite_name)
                if sample:
                    samples.append(sample)
                    
            except Exception as e:
                logger.warning(f"[EXTRACTOR] Error reading {test_file}: {e}")
    
    logger.info(f"[EXTRACTOR] Extracted {len(samples)} samples from test suites")
    return samples
```

### Step 4: Add Auto-Retraining Logic

**New File:** `src/main/python/ml_models/auto_retrainer.py`

```python
"""
Auto-Retraining Module

Monitors test_suites/ for new test cases and triggers retraining when needed.
"""

import json
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional

logger = logging.getLogger(__name__)


class AutoRetrainer:
    """Monitors test cases and triggers auto-retraining."""
    
    def __init__(self, project_root: Path = None):
        if project_root is None:
            project_root = Path(__file__).parent.parent.parent.parent.parent
        
        self.project_root = project_root
        self.test_suites_dir = project_root / "test_suites"
        self.training_log_path = project_root / "resources" / "ml_data" / "logs" / "auto_training_log.json"
        self.training_log_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Thresholds for triggering retraining
        self.NEW_TESTS_THRESHOLD = 50  # Retrain after 50 new tests
        self.TIME_THRESHOLD_DAYS = 30  # Retrain after 30 days
    
    def should_retrain(self) -> tuple[bool, str]:
        """
        Check if retraining should be triggered.
        
        Returns:
            (should_retrain: bool, reason: str)
        """
        # Load training history
        last_training = self._load_last_training_info()
        
        if not last_training:
            return (True, "No previous training found")
        
        # Count new test cases since last training
        new_tests_count = self._count_tests_since(last_training['timestamp'])
        
        if new_tests_count >= self.NEW_TESTS_THRESHOLD:
            return (True, f"{new_tests_count} new tests added (threshold: {self.NEW_TESTS_THRESHOLD})")
        
        # Check time since last training
        last_training_date = datetime.fromisoformat(last_training['timestamp'])
        days_since = (datetime.now() - last_training_date).days
        
        if days_since >= self.TIME_THRESHOLD_DAYS:
            return (True, f"{days_since} days since last training (threshold: {self.TIME_THRESHOLD_DAYS})")
        
        return (False, f"No retraining needed ({new_tests_count} new tests, {days_since} days)")
    
    def _count_tests_since(self, timestamp: str) -> int:
        """Count test cases added/modified since timestamp."""
        cutoff_date = datetime.fromisoformat(timestamp)
        count = 0
        
        if not self.test_suites_dir.exists():
            return 0
        
        for test_file in self.test_suites_dir.glob("*/*.json"):
            try:
                # Check file modification time
                mtime = datetime.fromtimestamp(test_file.stat().st_mtime)
                if mtime > cutoff_date:
                    count += 1
            except Exception as e:
                logger.debug(f"Error checking {test_file}: {e}")
        
        return count
    
    def _load_last_training_info(self) -> Optional[Dict]:
        """Load info about last training run."""
        if not self.training_log_path.exists():
            return None
        
        try:
            with open(self.training_log_path, 'r') as f:
                log = json.load(f)
            return log.get('last_training')
        except Exception as e:
            logger.error(f"Error loading training log: {e}")
            return None
    
    def record_training(self, num_samples: int, results: Dict):
        """Record successful training run."""
        log_entry = {
            'last_training': {
                'timestamp': datetime.now().isoformat(),
                'num_samples': num_samples,
                'test_suites_scanned': self._count_all_tests(),
                'best_model': results.get('best_model'),
                'f1_score': results.get('f1_score')
            },
            'history': []
        }
        
        # Append to history
        if self.training_log_path.exists():
            try:
                with open(self.training_log_path, 'r') as f:
                    existing_log = json.load(f)
                if 'last_training' in existing_log:
                    log_entry['history'] = existing_log.get('history', [])
                    log_entry['history'].append(existing_log['last_training'])
            except Exception as e:
                logger.warning(f"Could not load existing log: {e}")
        
        # Save updated log
        with open(self.training_log_path, 'w') as f:
            json.dump(log_entry, f, indent=2)
        
        logger.info(f"[AUTO-RETRAIN] Training logged: {num_samples} samples, F1: {results.get('f1_score')}")
    
    def _count_all_tests(self) -> int:
        """Count all test cases in test_suites/."""
        if not self.test_suites_dir.exists():
            return 0
        return len(list(self.test_suites_dir.glob("*/*.json")))
    
    def trigger_retraining(self) -> Dict:
        """Trigger automatic retraining."""
        from .training_data_extractor import TrainingDataExtractor
        from .semantic_model_trainer import SemanticModelTrainer
        
        logger.info("[AUTO-RETRAIN] Starting automatic retraining...")
        
        try:
            # Extract training data
            extractor = TrainingDataExtractor(self.project_root)
            training_data = extractor.extract_all_training_data()
            
            # Train models
            trainer = SemanticModelTrainer(self.project_root)
            results = trainer.train_and_save()
            
            # Record this training
            self.record_training(
                num_samples=training_data['metadata']['total_samples'],
                results=results
            )
            
            logger.info("[AUTO-RETRAIN] ✓ Automatic retraining completed successfully")
            return {'success': True, 'results': results}
            
        except Exception as e:
            logger.error(f"[AUTO-RETRAIN] Failed: {e}")
            return {'success': False, 'error': str(e)}
```

### Step 5: Add Auto-Retrain Check to API Server

**File:** `src/main/python/api_server_modular.py`

**Add after test case saving:**

```python
from ml_models.auto_retrainer import AutoRetrainer

# Initialize auto-retrainer
auto_retrainer = AutoRetrainer()

# Add this after successful test case save
def check_and_retrain():
    """Check if auto-retraining should be triggered."""
    try:
        should_retrain, reason = auto_retrainer.should_retrain()
        
        if should_retrain:
            logger.info(f"[AUTO-RETRAIN] Triggering retraining: {reason}")
            
            # Trigger async retraining (don't block the save request)
            import threading
            def retrain_async():
                result = auto_retrainer.trigger_retraining()
                if result['success']:
                    logger.info("[AUTO-RETRAIN] ✓ Model retrained successfully")
                else:
                    logger.error(f"[AUTO-RETRAIN] ✗ Retraining failed: {result.get('error')}")
            
            thread = threading.Thread(target=retrain_async, daemon=True)
            thread.start()
        else:
            logger.debug(f"[AUTO-RETRAIN] {reason}")
            
    except Exception as e:
        logger.error(f"[AUTO-RETRAIN] Check failed: {e}")

# Call this after test save
@app.route('/recorder/save-test-case', methods=['POST'])
def save_recorder_test():
    result = recorder_handler.save_test_case_to_disk()
    
    # Check if retraining needed
    check_and_retrain()
    
    return result
```

---

## 🎯 Migration Plan

### Phase 1: Create Unified Storage (NOW)

1. ✅ Create auto_retrainer.py
2. ✅ Update test_case_builder.py to save to test_suites/
3. ✅ Update recorder_handler.py to save to test_suites/
4. ✅ Update training_data_extractor.py to read from test_suites/

### Phase 2: Migrate Existing Tests (OPTIONAL)

```powershell
# Script to migrate existing tests to test_suites/
cd C:\Users\valaboph\AIAutomation

# Move builder tests
New-Item -ItemType Directory -Path "test_suites\builder_migrated" -Force
Get-ChildItem "test_cases\builder" -Filter "*.json" -Recurse | 
    Copy-Item -Destination "test_suites\builder_migrated"

# Move recorder tests (flat structure, username in metadata)
Get-ChildItem "test_cases" -Filter "*.json" -Recurse | 
    Where-Object { $_.DirectoryName -like "*recorder*" } |
    ForEach-Object {
        $dest = "test_suites\recorded"
        New-Item -ItemType Directory -Path $dest -Force
        Copy-Item $_.FullName -Destination $dest
    }

# Retrain with all migrated tests
.\setup_ml_semantic_analysis.bat
```

### Phase 3: Enable Auto-Retraining (AFTER TESTING)

1. Test auto-retrainer with threshold = 5 tests (for testing)
2. Verify it triggers correctly
3. Set production thresholds (50 tests, 30 days)
4. Deploy to production

### Phase 4: DB Integration (FUTURE)

```python
# Example DB integration (future)
class TestSuiteDatabase:
    def save_test_to_db(self, test_case: Dict):
        """Save to database AND file system."""
        # Save to DB
        db.tests.insert(test_case)
        
        # Also save to file for ML training
        suite_dir = Path("test_suites") / test_case['suite']
        suite_dir.mkdir(exist_ok=True)
        with open(suite_dir / f"{test_case['id']}.json", 'w') as f:
            json.dump(test_case, f)
```

---

## ✅ Benefits of This Architecture

### 1. Single Source of Truth
- All tests in `test_suites/`
- Easy to backup, version control
- Clear organization by functionality

### 2. Automatic Learning
- ML model learns from every saved test
- No manual retraining needed
- Model improves over time

### 3. Production Ready
- Scalable storage structure
- Easy DB integration later
- Organized for teams

### 4. Better Suggestions
- Semantic analysis learns YOUR patterns
- Suggestions match YOUR test style
- Continuously improving accuracy

---

## 📊 Expected Results

**After Implementation:**

```
Week 1: Save 10 tests → ML reads them
Week 2: Save 30 tests → Still using old model
Week 3: Save 20 tests (total 60) → AUTO-RETRAIN TRIGGERED!
Week 4: Semantic suggestions now 95% relevant to YOUR tests
```

**Metrics:**
- Current: 90% accuracy on 641 samples
- After 100 your tests: 92-93% accuracy
- After 500 your tests: 95%+ accuracy on YOUR specific patterns

---

## 🚀 Next Steps

**To implement this:**

1. **Review this document** - Make sure the architecture makes sense
2. **I can implement** - Say "implement unified storage" and I'll make all the code changes
3. **Test** - Save a few tests and verify they go to test_suites/
4. **Migrate** - Move existing tests (optional)
5. **Enable auto-retrain** - Turn on automatic retraining

**Want me to implement this now?**
