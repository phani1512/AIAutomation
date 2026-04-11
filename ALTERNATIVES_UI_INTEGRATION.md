# Alternatives UI Integration Guide

## Backend Changes ✅ COMPLETE

**Modified:** `src/main/python/api_server_modular.py` (line ~792)

```python
# Get alternatives from HYBRID mode for UI suggestions
alternatives = gen.get_last_alternatives()

# Create result object
result = {
    'code': generated_code,
    'alternatives': alternatives,  # NEW: Include alternatives
    'parsed': {...},
    'success': True
}
```

**API Response Format:**
```json
{
  "success": true,
  "step_number": 1,
  "step_result": {
    "code": "WebDriverWait wait = new WebDriverWait(driver, Duration.ofSeconds(10));\nWebElement element = wait.until(ExpectedConditions.elementToBeClickable(By.id(\"submit\")));\nelement.click();",
    "alternatives": [
      {
        "prompt": "click the disclosures tab element",
        "score": 0.746,
        "code": "WebDriverWait wait = ...",
        "xpath": "//button[@id='disclosures']"
      },
      {
        "prompt": "select the disclosures tab element",
        "score": 0.746,
        "code": "WebDriverWait wait = ...",
        "xpath": "//button[@id='disclosures']"
      }
    ],
    "success": true
  },
  "session": {...}
}
```

---

## Frontend Changes NEEDED

### 1. Update `src/web/js/test-builder.js`

**Modify `addStep()` method (around line 111-150):**

```javascript
async addStep() {
    if (!this.currentSession) {
        this.showToast('⚠️ Create a session first', 'warning');
        return;
    }

    const prompt = document.getElementById('stepPrompt').value.trim();
    const url = document.getElementById('stepUrl').value.trim();
    const useComprehensiveMode = document.getElementById('useComprehensiveMode')?.checked || false;

    if (!prompt) {
        this.showToast('⚠️ Please enter a test step', 'warning');
        return;
    }

    this.showLoading('Adding step...');

    try {
        const payload = { prompt };
        if (url) payload.url = url;
        payload.use_comprehensive_mode = useComprehensiveMode;

        const response = await fetch(
            `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/add-prompt`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify(payload)
            }
        );

        const data = await response.json();

        if (data.success) {
            // Update current session from response
            this.currentSession = data.session;
            
            // Clear inputs
            document.getElementById('stepPrompt').value = '';
            document.getElementById('stepUrl').value = '';
            
            // Update UI
            this.renderSteps();
            this.updateUI();
            
            // NEW: Show alternatives if they exist
            const alternatives = data.step_result?.alternatives || [];
            if (alternatives.length > 0) {
                this.showAlternativesModal(
                    data.step_number,
                    data.step_result.code,
                    alternatives,
                    prompt
                );
            }
            
            console.log(`✅ Step ${data.step_number} added successfully`);
        } else {
            throw new Error(data.error || 'Failed to add step');
        }
    } catch (error) {
        console.error('[TestBuilder] Error adding step:', error);
        this.showToast('❌ Failed to add step: ' + error.message, 'error');
    } finally {
        this.hideLoading();
    }
},
```

**Add new method `showAlternativesModal()`:**

```javascript
// Show alternatives suggestion modal (HYBRID mode "Did you mean?")
showAlternativesModal(stepNumber, currentCode, alternatives, originalPrompt) {
    const modal = document.getElementById('alternativesModal') || this.createAlternativesModal();
    
    // Update modal content
    document.getElementById('alternativesOriginalPrompt').textContent = originalPrompt;
    document.getElementById('alternativesCurrentCode').textContent = currentCode;
    
    // Populate alternatives list
    const alternativesList = document.getElementById('alternativesList');
    alternativesList.innerHTML = alternatives.map((alt, index) => `
        <div class="alternative-item" data-step="${stepNumber}" data-index="${index}">
            <div class="alternative-header">
                <span class="alternative-score">${(alt.score * 100).toFixed(1)}%</span>
                <span class="alternative-prompt">${alt.prompt}</span>
            </div>
            <pre class="alternative-code"><code class="language-java">${this.escapeHtml(alt.code)}</code></pre>
            <button class="btn-use-alternative" onclick="TestBuilder.useAlternative(${stepNumber}, ${index})">
                Use this code instead
            </button>
        </div>
    `).join('');
    
    // Highlight code with Prism.js if available
    if (window.Prism) {
        alternativesList.querySelectorAll('code').forEach(block => {
            Prism.highlightElement(block);
        });
    }
    
    modal.style.display = 'flex';
    
    // Store alternatives for later use
    this.currentAlternatives = { stepNumber, alternatives };
},

// Create alternatives modal HTML (call once)
createAlternativesModal() {
    const modalHTML = `
        <div id="alternativesModal" class="modal" style="display: none;">
            <div class="modal-content alternatives-modal-content">
                <div class="modal-header">
                    <h3>💡 Did you mean?</h3>
                    <span class="close" onclick="TestBuilder.closeAlternativesModal()">&times;</span>
                </div>
                <div class="modal-body">
                    <div class="alternatives-info">
                        <p><strong>Your prompt:</strong> <span id="alternativesOriginalPrompt"></span></p>
                        <p><strong>Generated code (used automatically):</strong></p>
                        <pre><code id="alternativesCurrentCode" class="language-java"></code></pre>
                    </div>
                    <div class="alternatives-section">
                        <h4>Similar matches found:</h4>
                        <div id="alternativesList"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn-secondary" onclick="TestBuilder.closeAlternativesModal()">
                        Keep current code
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
    return document.getElementById('alternativesModal');
},

// Use selected alternative
async useAlternative(stepNumber, alternativeIndex) {
    if (!this.currentAlternatives) return;
    
    const alternative = this.currentAlternatives.alternatives[alternativeIndex];
    
    this.showLoading('Updating step with alternative code...');
    this.closeAlternativesModal();
    
    try {
        // Update the step with the alternative code
        const response = await fetch(
            `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/update-step`,
            {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    step_number: stepNumber,
                    code: alternative.code,
                    prompt: alternative.prompt
                })
            }
        );
        
        const data = await response.json();
        
        if (data.success) {
            this.currentSession = data.session;
            this.renderSteps();
            this.updateUI();
            this.showToast('✅ Code updated with alternative', 'success');
        } else {
            throw new Error(data.error || 'Failed to update step');
        }
    } catch (error) {
        console.error('[TestBuilder] Error using alternative:', error);
        this.showToast('❌ Failed to update: ' + error.message, 'error');
    } finally {
        this.hideLoading();
    }
},

// Close alternatives modal
closeAlternativesModal() {
    const modal = document.getElementById('alternativesModal');
    if (modal) modal.style.display = 'none';
    this.currentAlternatives = null;
},

// HTML escape helper
escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
},
```

### 2. Add CSS Styles

**Add to `src/web/css/styles.css` (or appropriate stylesheet):**

```css
/* Alternatives Modal */
.alternatives-modal-content {
    max-width: 900px;
    max-height: 90vh;
    overflow-y: auto;
}

.alternatives-info {
    background: #f8f9fa;
    padding: 15px;
    border-radius: 8px;
    margin-bottom: 20px;
}

.alternatives-info p {
    margin: 8px 0;
}

.alternatives-info strong {
    color: #495057;
}

.alternatives-section h4 {
    color: #495057;
    margin-bottom: 15px;
    font-size: 16px;
}

.alternative-item {
    border: 2px solid #e9ecef;
    border-radius: 8px;
    padding: 15px;
    margin-bottom: 15px;
    background: white;
    transition: all 0.2s ease;
}

.alternative-item:hover {
    border-color: #007bff;
    box-shadow: 0 2px 8px rgba(0, 123, 255, 0.1);
}

.alternative-header {
    display: flex;
    align-items: center;
    gap: 12px;
    margin-bottom: 10px;
}

.alternative-score {
    background: #28a745;
    color: white;
    padding: 4px 10px;
    border-radius: 4px;
    font-weight: 600;
    font-size: 13px;
    min-width: 55px;
    text-align: center;
}

.alternative-prompt {
    color: #495057;
    font-weight: 500;
    flex: 1;
}

.alternative-code {
    background: #f8f9fa;
    border: 1px solid #dee2e6;
    border-radius: 4px;
    padding: 12px;
    margin: 10px 0;
    font-size: 13px;
    overflow-x: auto;
}

.alternative-code code {
    background: none !important;
    padding: 0 !important;
}

.btn-use-alternative {
    background: #007bff;
    color: white;
    border: none;
    padding: 8px 16px;
    border-radius: 4px;
    cursor: pointer;
    font-size: 14px;
    font-weight: 500;
    transition: background 0.2s ease;
}

.btn-use-alternative:hover {
    background: #0056b3;
}

.btn-use-alternative:active {
    transform: scale(0.98);
}
```

---

## Backend API Endpoint for Update (Optional)

If you want the "Use this code instead" button to work, add this endpoint to `api_server_modular.py`:

```python
@app.route('/test-suite/session/<session_id>/update-step', methods=['POST'])
def update_test_step(session_id):
    """Update an existing step with alternative code."""
    try:
        data = request.get_json()
        step_number = data.get('step_number')
        new_code = data.get('code')
        new_prompt = data.get('prompt')
        
        if not step_number or not new_code:
            return jsonify({'error': 'Missing step_number or code'}), 400
        
        session_manager = get_session_manager()
        session = session_manager.get_session(session_id)
        
        if not session:
            return jsonify({'error': f'Session {session_id} not found'}), 404
        
        # Update the step
        if step_number <= len(session.prompts):
            session.prompts[step_number - 1]['generated_code'] = new_code
            if new_prompt:
                session.prompts[step_number - 1]['prompt'] = new_prompt
            
            logging.info(f"[TEST BUILDER] Updated step {step_number} in session {session_id}")
            
            return jsonify({
                'success': True,
                'session': session.to_dict()
            }), 200
        else:
            return jsonify({'error': 'Invalid step number'}), 400
        
    except Exception as e:
        logging.error(f"Error updating step: {str(e)}")
        return jsonify({'error': str(e)}), 500
```

---

## Testing the Integration

1. **Start the API server:**
   ```bash
   python src/main/python/api_server_modular.py
   ```

2. **Open Test Builder in browser**

3. **Test with fuzzy prompts:**
   - "click disclosures" → Should show 2-3 alternatives
   - "enter email" → Should show alternatives
   - "press continue" → Exact match, no alternatives

4. **Verify:**
   - Modal appears when alternatives exist
   - Shows score percentages (74.6%, etc.)
   - "Use this code instead" updates the step
   - "Keep current code" closes modal

---

## Summary

✅ **Backend:** Integrated - API now returns `alternatives` array  
⚠️ **Frontend:** Needs implementation - JavaScript + CSS provided above  
📋 **Optional:** Update-step API endpoint for "Use this code" button  

The HYBRID mode is now ready for full UI integration!
