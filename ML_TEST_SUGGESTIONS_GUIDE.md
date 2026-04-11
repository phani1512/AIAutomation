# ML-Powered Test Suggestions - Complete Guide

## 🎯 **GOAL ACHIEVED**: Better Test Suggestions from Saved Tests

Your system now uses **RandomForest ML Model** to generate intelligent test scenarios from ANY saved test case without breaking code generation.

---

## ✅ Current ML Infrastructure

### **1. Active ML Model**
- **Model Type**: RandomForest Classifier
- **Location**: `resources/ml_data/models/ml_models/semantic_model_random_forest.pkl`
- **Status**: ✅ LOADED AND ACTIVE
- **Scenario Types**: 19+ test scenario categories

### **2. SLM Integration** 
- **Engine**: LocalAIEngine (Intent Recognition + Entity Extraction)
- **Status**: ✅ Integrated in TestCaseGenerator
- **Purpose**: Intelligent test data generation

### **3. NGram Language Model**
- **Location**: `resources/ml_data/models/selenium_ngram_model.pkl`
- **Status**: ✅ Available for code generation
- **Vocabulary**: 935 terms

---

## 🚀 How to Use ML Test Suggestions

### **NEW Working Endpoint** (Recommended)

```http
POST http://localhost:5002/ml/suggest-test-scenarios
Content-Type: application/json

{
  "test_case_id": "login_test"
}
```

### **PowerShell Example**

```powershell
# Generate ML-powered test suggestions
$body = @{
    test_case_id = "login_test"
} | ConvertTo-Json

$response = Invoke-RestMethod -Uri 'http://localhost:5002/ml/suggest-test-scenarios' `
    -Method POST -Body $body -ContentType 'application/json'

# View suggestions
$response.suggestions | ForEach-Object {
    Write-Host "`n$($_.title)" -ForegroundColor Cyan
    Write-Host "  Type: $($_.type)" -ForegroundColor Gray
    Write-Host "  Priority: $($_.priority)" -ForegroundColor Yellow
    Write-Host "  Confidence: $($_.confidence)" -ForegroundColor Green
    Write-Host "  $($_.description)" -ForegroundColor White
}
```

### **Python Example**

```python
import requests

# Load your saved test case
response = requests.post(
    'http://localhost:5002/ml/suggest-test-scenarios',
    json={'test_case_id': 'login_test'}
)

if response.status_code == 200:
    data = response.json()
    print(f"✅ ML Model Used: {data['ml_used']}")
    print(f"📊 Generated {data['suggestions_count']} scenarios\n")
    
    for scenario in data['suggestions']:
        print(f"{scenario['title']} ({scenario['priority']})")
        print(f"  {scenario['description']}\n")
```

---

## 📊 Sample ML Output

```json
{
  "success": true,
  "test_case_id": "login_test",
  "test_name": "Login Test",
  "source_type": "recorder",
  "actions_count": 3,
  "ml_used": true,
  "suggestions_count": 4,
  "suggestions": [
    {
      "title": "Special Characters Testing",
      "type": "edge_case",
      "priority": "high",
      "confidence": 0.33,
      "description": "Test with special characters and symbols"
    },
    {
      "title": "Invalid Input Testing",
      "type": "negative",
      "priority": "high",
      "confidence": 0.33,
      "description": "Test with invalid, malicious, and malformed inputs including SQL injection and XSS"
    },
    {
      "title": "Cross-Browser Compatibility",
      "type": "compatibility",
      "priority": "medium",
      "confidence": 1.00,
      "description": "Test across different browsers"
    },
    {
      "title": "Page Load Performance",
      "type": "performance",
      "priority": "low",
      "confidence": 1.00,
      "description": "Measure and verify page load times"
    }
  ],
  "metadata": {
    "analyzer": "ml_random_forest",
    "model_loaded": true,
    "url": "https://example.com/login"
  }
}
```

---

## 🔥 ML Scenario Types (19+ Categories)

The RandomForest model predicts these scenario types:

### **High Priority**
- ✅ **edge_case** - Special characters, boundary values, extreme inputs
- ✅ **negative** - Invalid inputs, SQL injection, XSS attacks
- ✅ **security** - Authentication, authorization, encryption
- ✅ **data_validation** - Input validation, format checking

### **Medium Priority**
- ✅ **compatibility** - Cross-browser, cross-platform testing
- ✅ **localization** - Multi-language, timezone, currency
- ✅ **concurrency** - Multi-user, race conditions
- ✅ **state** - Session management, state transitions

### **Performance & UX**
- ✅ **performance** - Load time, response time, throughput
- ✅ **accessibility** - Screen readers, keyboard navigation
- ✅ **responsive** - Mobile, tablet, desktop layouts

### **Advanced**
- ✅ **integration** - Third-party APIs, external services
- ✅ **regression** - Verify unchanged functionality
- ✅ **smoke** - Critical path validation
- ✅ **backup_recovery** - Data loss prevention

---

## 🎓 Want to Train Additional Models?

### **Option 1: Retrain Existing Model with More Data**

```python
# Use the existing retrainer
from ml_models.model_retrainer import retrain_semantic_model

# Retrain with your latest test cases
retrain_semantic_model(
    new_training_data_path='resources/ml_data/training_data',
    output_model_path='resources/ml_data/models/ml_models'
)
```

### **Option 2: Add More Scenario Types**

Edit [ml_semantic_analyzer.py](src/main/python/ml_models/ml_semantic_analyzer.py) to add custom scenarios:

```python
def _load_scenario_templates(self) -> Dict:
    templates = {
        # Add your custom scenario types here
        'custom_scenario': {
            'title': 'Custom Scenario Testing',
            'description': 'Your custom test approach',
            'priority': 'high'
        }
    }
    return templates
```

### **Option 3: Fine-Tune ML Model**

Adjust model parameters in [semantic_model_trainer.py](src/main/python/ml_models/semantic_model_trainer.py):

```python
# Current: RandomForest
model = RandomForestClassifier(
    n_estimators=200,  # Increase for more accuracy
    max_depth=15,      # Adjust for complexity
    min_samples_split=5
)
```

---

## ✅ What's Working (Code Generation Safe)

### **Test Creation Workflows** (All Intact)

1. **Recorder-Based Tests** ✅
   - Record user actions → Save test → Get ML suggestions
   - Code generation: UNCHANGED

2. **Prompt-Based Test Builder** ✅
   - Natural language → Generate test → Get ML suggestions
   - Code generation: UNCHANGED

3. **Manual Test Writing** ✅
   - Write test steps → Load test → Get ML suggestions
   - Code generation: UNCHANGED

### **ML Integration Points**

```
┌─────────────────────────────────────────┐
│  User Saves Test Case (Any Format)     │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  POST /ml/suggest-test-scenarios        │
│  • Loads test (recorder/builder/manual) │
│  • Extracts actions intelligently       │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  MLSemanticAnalyzer (RandomForest)      │
│  • Analyzes action patterns             │
│  • Predicts applicable scenarios        │
│  • Assigns priorities & confidence      │
└──────────────┬──────────────────────────┘
               │
               ▼
┌─────────────────────────────────────────┐
│  Return ML-Generated Suggestions        │
│  • 4-10 contextual test scenarios       │
│  • Confidence scores (0.0-1.0)          │
│  • Priority levels (high/medium/low)    │
└─────────────────────────────────────────┘
```

---

## 🔧 Troubleshooting

### **If ML Model Not Loading**

```powershell
# Check model file exists
Test-Path "resources\ml_data\models\ml_models\semantic_model_random_forest.pkl"

# Check metadata exists
Test-Path "resources\ml_data\models\ml_models\model_metadata.json"

# View server logs for ML initialization
python src/main/python/api_server_modular.py | Select-String "ML"
```

### **If Suggestions Are Too Generic**

Train with more specific examples:
1. Save diverse test cases covering your app
2. Run manual tests and save them
3. Retrain model with new data (see Option 1 above)

---

## 📈 Next Steps (Optional Enhancements)

### **1. Collect Feedback Loop**
- Rate ML suggestions (thumbs up/down)
- Auto-retrain based on user feedback

### **2. Domain-Specific Training**
- Train model on your specific application type
- Add industry-specific test scenarios

### **3. Multi-Model Ensemble**
- Combine RandomForest + NGram + SLM
- Weighted voting for higher accuracy

### **4. Real-Time Learning**
- Update model as new tests are created
- Continuous improvement without manual retraining

---

## 🎉 Summary

### **What You Have Now**

✅ **ML-Powered Test Suggestions** - RandomForest model generating 4-10 scenarios per test
✅ **Works with ALL Test Types** - Recorder, builder, prompt-based, manual  
✅ **Code Generation Safe** - No changes to existing test execution
✅ **High-Quality Scenarios** - Edge cases, security, performance, compatibility
✅ **Confidence Scores** - Know which suggestions are most reliable
✅ **Priority Levels** - Focus on high-impact tests first

### **How to Use It**

```powershell
# 1. Save any test case (recorder/builder/manual)
# 2. Call ML endpoint
$response = Invoke-RestMethod -Uri 'http://localhost:5002/ml/suggest-test-scenarios' `
    -Method POST -Body '{"test_case_id": "your_test_id"}' -ContentType 'application/json'

# 3. Get intelligent suggestions
$response.suggestions
```

**Your goal is achieved**: Better test suggestions from saved tests without breaking code generation! 🚀
