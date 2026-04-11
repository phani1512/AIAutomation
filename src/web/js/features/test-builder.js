// Test Builder Module - Multi-Prompt Test Suite Creator (Phase 0)
// Manages test sessions, steps, and test case creation

const TestBuilder = {
    // State
    currentSession: null,
    sessions: [],
    testCases: [],
    
    // API base URL
    get API_BASE() {
        return window.API_BASE_URL || 'http://localhost:5003';
    },

    // Initialize the test builder
    async init() {
        console.log('[TestBuilder] Initializing...');
        await this.loadSessions();
        await this.loadTestCases();
        this.updateStats();
        this.updateTestsGeneratedCounter(); // Load counter from localStorage
        this.updateUI(); // Show appropriate view based on session state
    },

    // Create new session
    async newSession() {
        this.showNewTestModal();
    },

    // Show new test modal
    showNewTestModal() {
        const modal = document.getElementById('newTestModal');
        modal.style.display = 'flex';
        
        // Clear previous values
        document.getElementById('newTestName').value = '';
        document.getElementById('newTestDescription').value = '';
        
        // Focus on name input
        setTimeout(() => {
            document.getElementById('newTestName').focus();
        }, 100);
    },

    // Close modal
    closeModal() {
        document.getElementById('newTestModal').style.display = 'none';
    },

    // Create session with API
    async createSession() {
        const name = document.getElementById('newTestName').value.trim();
        const description = document.getElementById('newTestDescription').value.trim();

        if (!name) {
            this.showToast('⚠️ Please enter a test name', 'warning');
            return;
        }

        this.closeModal();
        this.showLoading();

        try {
            const response = await fetch(`${this.API_BASE}/test-suite/session/start`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ name, description: description || `Test: ${name}` })
            });

            const data = await response.json();

            if (data.success) {
                this.currentSession = data.session;
                this.updateUI();
                this.showToast('✅ Test session created!', 'success');
                await this.loadSessions(); // Refresh sessions list
            } else {
                throw new Error(data.error || 'Failed to create session');
            }
        } catch (error) {
            console.error('[TestBuilder] Error creating session:', error);
            this.showToast('❌ Failed to create session: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Add step to current session
    async addStep() {
        if (!this.currentSession) {
            this.showToast('⚠️ Please create a test session first', 'warning');
            return;
        }

        const prompt = document.getElementById('stepPrompt').value.trim();
        const url = document.getElementById('stepUrl').value.trim();
        const value = document.getElementById('stepValue').value.trim();
        const useComprehensiveMode = document.getElementById('useComprehensiveMode')?.checked || false;

        if (!prompt) {
            this.showToast('⚠️ Please enter a test step', 'warning');
            return;
        }

        this.showLoading('Adding step');

        try {
            const payload = { prompt };
            if (url) payload.url = url;
            if (value) payload.value = value;  // NEW: Include data value
            // NEW: Include comprehensive mode preference
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
                document.getElementById('stepValue').value = '';  // Clear value field too
                
                // Update UI
                this.renderSteps();
                this.updateUI();
                
                // Silent success - just update step count (no popup)
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

    // Add step and continue (keeps focus on input)
    async addStepAndContinue() {
        await this.addStep();
        // Focus back on prompt input
        setTimeout(() => {
            document.getElementById('stepPrompt').focus();
        }, 100);
    },

    // Remove step
    async removeStep(stepNumber) {
        if (!this.currentSession) return;

        if (!confirm(`Remove step ${stepNumber}?`)) return;

        this.showLoading('Removing step');

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/remove-prompt`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ step_number: stepNumber })
                }
            );

            const data = await response.json();

            if (data.success) {
                this.currentSession = data.session;
                this.renderSteps();
                this.updateUI();
                this.showToast('✅ Step removed', 'success');
            } else {
                throw new Error(data.error || 'Failed to remove step');
            }
        } catch (error) {
            console.error('[TestBuilder] Error removing step:', error);
            this.showToast('❌ Failed to remove step: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Edit step (inline editing)
    async editStep(stepNumber) {
        if (!this.currentSession) return;

        const step = this.currentSession.prompts.find(s => s.step === stepNumber);
        if (!step) return;

        // Enable inline editing mode
        const stepElement = document.querySelector(`[data-step="${stepNumber}"]`);
        if (!stepElement) return;

        const promptDiv = stepElement.querySelector('.step-prompt-text');
        const editButtons = stepElement.querySelector('.edit-buttons');
        const actionButtons = stepElement.querySelector('.action-buttons');

        if (!promptDiv) return;

        // Store original value
        const originalPrompt = step.prompt;
        
        // Make editable
        promptDiv.contentEditable = true;
        promptDiv.focus();
        promptDiv.style.outline = '2px solid var(--primary-color)';
        promptDiv.style.padding = '8px';
        promptDiv.style.borderRadius = '4px';
        promptDiv.style.background = 'var(--bg-tertiary)';
        
        // Show edit buttons, hide action buttons
        if (editButtons) editButtons.style.display = 'flex';
        if (actionButtons) actionButtons.style.display = 'none';

        // Select all text for easy editing
        const range = document.createRange();
        range.selectNodeContents(promptDiv);
        const selection = window.getSelection();
        selection.removeAllRanges();
        selection.addRange(range);
    },

    // Save inline edit
    async saveStepEdit(stepNumber) {
        if (!this.currentSession) return;

        const step = this.currentSession.prompts.find(s => s.step === stepNumber);
        if (!step) return;

        const stepElement = document.querySelector(`[data-step="${stepNumber}"]`);
        if (!stepElement) return;

        const promptDiv = stepElement.querySelector('.step-prompt-text');
        if (!promptDiv) return;

        const newPrompt = promptDiv.textContent.trim();
        
        // If empty or unchanged, cancel
        if (!newPrompt || newPrompt === step.prompt) {
            this.cancelStepEdit(stepNumber);
            return;
        }

        this.showLoading('Updating step');

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/update-prompt`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        step_number: stepNumber,
                        prompt: newPrompt,
                        url: step.url || null
                    })
                }
            );

            const data = await response.json();

            if (data.success) {
                this.currentSession = data.session;
                this.renderSteps();
                this.updateUI();
                this.showToast('✅ Step updated', 'success');
            } else {
                throw new Error(data.error || 'Failed to update step');
            }
        } catch (error) {
            console.error('[TestBuilder] Error updating step:', error);
            this.showToast('❌ Failed to update step: ' + error.message, 'error');
            this.renderSteps();  // Restore original content
        } finally {
            this.hideLoading();
        }
    },

    // Cancel inline edit
    cancelStepEdit(stepNumber) {
        // Just re-render to restore original state
        this.renderSteps();
    },

    // Move step up
    async moveStepUp(stepNumber) {
        if (!this.currentSession || stepNumber <= 1) return;

        await this.reorderStep(stepNumber, stepNumber - 1);
    },

    // Move step down
    async moveStepDown(stepNumber) {
        if (!this.currentSession || stepNumber >= this.currentSession.prompts.length) return;

        await this.reorderStep(stepNumber, stepNumber + 1);
    },

    // Reorder step (generic)
    async reorderStep(fromStep, toStep) {
        this.showLoading('Reordering');

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/reorder-prompt`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ from_step: fromStep, to_step: toStep })
                }
            );

            const data = await response.json();

            if (data.success) {
                this.currentSession = data.session;
                console.log('[TestBuilder] Steps reordered, new order:', this.currentSession.prompts.map(p => `${p.step}: ${p.prompt}`));
                this.renderSteps();
                this.updateUI();
                // Removed toast notification as requested
            } else {
                throw new Error(data.error || 'Failed to reorder steps');
            }
        } catch (error) {
            console.error('[TestBuilder] Error reordering steps:', error);
            this.showToast('❌ Failed to reorder: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Render steps in UI
    renderSteps() {
        const container = document.getElementById('testStepsList');
        const noStepsMsg = document.getElementById('noStepsMessage');

        // Exit early if elements don't exist (e.g., on different page)
        if (!container || !noStepsMsg) {
            console.log('[TestBuilder] Steps container not found, skipping renderSteps');
            return;
        }

        if (!this.currentSession || !this.currentSession.prompts || this.currentSession.prompts.length === 0) {
            container.innerHTML = '';
            noStepsMsg.style.display = 'block';
            return;
        }

        noStepsMsg.style.display = 'none';

        container.innerHTML = this.currentSession.prompts.map((step, index) => `
            <div class="test-step-item" data-step="${step.step}" style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid var(--primary-color);">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                    <div style="font-weight: 600; color: var(--primary-color);">
                        Step ${step.step}
                    </div>
                    <div class="action-buttons" style="display: flex; gap: 5px;">
                        <button onclick="TestBuilder.editStep(${step.step})" class="btn" style="background: #3b82f6; padding: 4px 8px; font-size: 0.8em;" title="Edit step">
                            ✏️
                        </button>
                        <button onclick="TestBuilder.moveStepUp(${step.step})" class="btn" style="background: #8b5cf6; padding: 4px 8px; font-size: 0.8em;" title="Move up" ${index === 0 ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                            ↑
                        </button>
                        <button onclick="TestBuilder.moveStepDown(${step.step})" class="btn" style="background: #8b5cf6; padding: 4px 8px; font-size: 0.8em;" title="Move down" ${index === this.currentSession.prompts.length - 1 ? 'disabled style="opacity: 0.5; cursor: not-allowed;"' : ''}>
                            ↓
                        </button>
                        <button onclick="TestBuilder.removeStep(${step.step})" class="btn" style="background: #ef4444; padding: 4px 8px; font-size: 0.8em;" title="Delete step">
                            🗑️
                        </button>
                    </div>
                    <div class="edit-buttons" style="display: none; gap: 5px;">
                        <button onclick="TestBuilder.saveStepEdit(${step.step})" class="btn" style="background: #10b981; padding: 4px 12px; font-size: 0.8em;" title="Save changes">
                            ✓ Save
                        </button>
                        <button onclick="TestBuilder.cancelStepEdit(${step.step})" class="btn" style="background: #6b7280; padding: 4px 12px; font-size: 0.8em;" title="Cancel editing">
                            ✗ Cancel
                        </button>
                    </div>
                </div>
                <div class="step-prompt-text" style="color: var(--text-primary); margin-bottom: 8px; font-size: 0.95em; cursor: text;">
                    ${this.escapeHtml(step.prompt)}
                </div>
                ${step.url ? `<div style="font-size: 0.85em; color: var(--text-secondary); margin-bottom: 8px;">
                    🔗 <code style="background: rgba(0,0,0,0.2); padding: 2px 6px; border-radius: 4px;">${this.escapeHtml(step.url)}</code>
                </div>` : ''}
                ${step.value ? `<div style="font-size: 0.85em; color: #3b82f6; margin-bottom: 8px;">
                    📝 Data: <code style="background: rgba(59, 130, 246, 0.15); padding: 2px 6px; border-radius: 4px; color: #3b82f6;">${this.escapeHtml(step.value)}</code>
                </div>` : ''}
                ${step.parsed && step.parsed.match_strategy ? this.renderMatchStrategy(step.parsed) : ''}
                ${step.parsed ? `<div style="font-size: 0.85em; color: var(--success-color);">
                    ✓ Understood: ${step.parsed.action} → ${step.parsed.element || 'element'}
                </div>` : ''}
                ${step.resolved_element === null && step.parsed ? `<div style="font-size: 0.85em; color: #f59e0b; margin-top: 5px;">
                    ⚠️ Element not found on current page (will be resolved during execution)
                </div>` : ''}
            </div>
        `).join('');
    },

    // Preview code in modal (like Recorder)
    async previewCode() {
        console.log('[TestBuilder] previewCode() called');
        console.log('[TestBuilder] currentSession:', this.currentSession);
        console.log('[TestBuilder] Current step order:', this.currentSession?.prompts?.map(p => `${p.step}: ${p.prompt}`));
        
        if (!this.currentSession) {
            this.showToast('⚠️ No active session', 'warning');
            return;
        }

        if (!this.currentSession.prompts || this.currentSession.prompts.length === 0) {
            this.showToast('⚠️ Add some steps first', 'warning');
            return;
        }

        console.log('[TestBuilder] Opening code preview modal...');
        
        // Open the modal with code preview
        await this.openBuilderPreviewModal();
    },

    // Hide code preview card
    hideCodePreview() {
        const card = document.getElementById('codePreviewCard');
        card.style.display = 'none';
        console.log('[TestBuilder] Code preview card hidden');
    },

    // Update preview in the card
    async updatePreviewCard() {
        const language = document.getElementById('previewLanguageCard').value;
        const codeElement = document.getElementById('codePreviewCardContent');

        console.log('[TestBuilder] Updating preview for language:', language);
        codeElement.textContent = 'Loading code preview...';
        codeElement.style.color = '#94a3b8'; // Light gray for loading text

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/preview?language=${language}`
            );
            
            if (!response.ok) {
                throw new Error(`HTTP ${response.status}: ${response.statusText}`);
            }
            
            const data = await response.json();

            if (data.success && data.code) {
                console.log('[TestBuilder] Code loaded successfully, length:', data.code.length);
                codeElement.textContent = data.code;
                codeElement.className = `language-${language}`;
                codeElement.style.color = '#e2e8f0'; // Reset to light color for code
                
                // Apply syntax highlighting if Prism is available
                if (typeof Prism !== 'undefined') {
                    console.log('[TestBuilder] Applying Prism syntax highlighting...');
                    Prism.highlightElement(codeElement);
                } else {
                    console.warn('[TestBuilder] Prism not available for syntax highlighting');
                }
            } else {
                throw new Error(data.error || 'No code returned from API');
            }
        } catch (error) {
            console.error('[TestBuilder] Error generating code preview:', error);
            codeElement.textContent = `// Error loading code preview\n// ${error.message}\n\n// Please check:\n// 1. Server is running\n// 2. Session has valid steps\n// 3. Browser console for details`;
            codeElement.style.color = '#f87171'; // Red for error
        }
    },

    // Open Builder Preview Modal (like Recorder)
    async openBuilderPreviewModal(initialLanguage = 'python') {
        // Remove existing modal if any
        this.closeBuilderPreviewModal();
        
        const languageMap = {
            'python': 'python',
            'java': 'java',
            'javascript': 'javascript',
            'cypress': 'javascript'
        };
        
        const langClass = languageMap[initialLanguage] || 'python';
        
        // Fetch code for initial language
        let initialCode = '// Loading code preview...';
        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/preview?language=${initialLanguage}`
            );
            const data = await response.json();
            if (data.success && data.code) {
                initialCode = data.code;
            } else {
                initialCode = `// Error: ${data.error || 'Failed to generate code'}`;
            }
        } catch (error) {
            initialCode = `// Error loading code preview\n// ${error.message}`;
        }
        
        const modal = document.createElement('div');
        modal.id = 'builderPreviewModal';
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 9999;
            backdrop-filter: blur(5px);
        `;
        
        const testStepsHtml = this.currentSession.prompts.map((p, i) => `
            <div style="padding: 8px; margin: 4px 0; background: var(--accent-bg, rgba(124, 58, 237, 0.1)); border-left: 3px solid var(--accent, #7C3AED); border-radius: 4px;">
                <strong style="color: var(--accent, #7C3AED);">${i + 1}.</strong> ${this.escapeHtml(p.prompt)}
                ${p.value ? `<span style="color: var(--success, #10b981); margin-left: 10px;">→ "${this.escapeHtml(p.value)}"</span>` : ''}
            </div>
        `).join('');
        
        modal.innerHTML = `
            <div style="width: 90%; max-width: 1200px; height: 90vh; background: var(--bg-secondary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden;">
                <!-- Modal Header -->
                <div id="builderModalHeader" style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 2px solid var(--border-color);">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">
                        👁️ Code Preview - ${this.escapeHtml(this.currentSession.name)}
                    </h3>
                    <div id="builderModalActions" style="display: flex; gap: 8px; align-items: center;">
                        <button onclick="window.TestBuilder.executeFromModal()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                            ▶️ Execute
                        </button>
                        <button onclick="window.TestBuilder.editBuilderCode()" style="padding: 8px 16px; background: #F59E0B; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                            ✏️ Edit
                        </button>
                        <button onclick="window.TestBuilder.copyBuilderPreviewCode()" style="padding: 8px 16px; background: #7C3AED; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                            📋 Copy
                        </button>
                        <button onclick="window.TestBuilder.exportBuilderPreviewCode()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                            💾 Export
                        </button>
                        <button onclick="window.TestBuilder.closeBuilderPreviewModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">
                            ✕
                        </button>
                    </div>
                </div>
                
                <!-- Test Steps Summary -->
                <div style="padding: 16px 24px; border-bottom: 1px solid var(--border-color); max-height: 150px; overflow-y: auto;">
                    <h4 style="margin: 0 0 10px 0; color: var(--text-primary); font-size: 14px; font-weight: 600;">📝 Test Steps (${this.currentSession.prompts.length}):</h4>
                    <div style="font-size: 13px;">
                        ${testStepsHtml}
                    </div>
                </div>
                
                <!-- Language Selector -->
                <div style="padding: 8px 24px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 10px;">
                    <label style="color: var(--text-primary); font-weight: 600; font-size: 13px;">Language:</label>
                    <select id="builderPreviewLanguageSelect" onchange="window.TestBuilder.switchBuilderPreviewLanguage(this.value)" style="padding: 4px 8px; border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color); font-size: 12px; cursor: pointer; font-weight: 500; max-width: 200px;">
                        <option value="python" ${initialLanguage === 'python' ? 'selected' : ''}>🐍 Python</option>
                        <option value="java" ${initialLanguage === 'java' ? 'selected' : ''}>☕ Java</option>
                        <option value="javascript" ${initialLanguage === 'javascript' ? 'selected' : ''}>🟨 JavaScript</option>
                        <option value="cypress" ${initialLanguage === 'cypress' ? 'selected' : ''}>🌲 Cypress</option>
                    </select>
                </div>
                
                <!-- Modal Body: Code Viewer (Read-only) -->
                <div id="builderModalViewMode" class="code-modal-body" style="flex: 1; overflow: auto; padding: 0;">
                    <pre style="margin: 0; padding: 24px; height: 100%;"><code id="builderModalCodeContent" class="language-${langClass}" style="font-size: 14px; line-height: 1.6; display: block; white-space: pre;">${this.escapeHtml(initialCode)}</code></pre>
                </div>
                
                <!-- Modal Body: Code Editor (Edit mode) -->
                <div id="builderModalEditMode" style="display: none; flex: 1; overflow: hidden; padding: 24px;">
                    <textarea id="builderModalCodeEditor" style="width: 100%; height: 100%; padding: 16px; background: var(--code-bg); color: var(--code-text); border: 2px solid var(--border-color); border-radius: 8px; font-family: 'JetBrains Mono', 'Fira Code', 'Courier New', Consolas, monospace; font-size: 14px; line-height: 1.6; resize: none; box-sizing: border-box;">${initialCode}</textarea>
                </div>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        // Store current language globally
        window.builderPreviewCurrentLanguage = initialLanguage;
        window.builderPreviewCurrentCode = initialCode;
        window.builderPreviewEditMode = false;  // Track edit mode
        
        // Apply syntax highlighting if available
        if (typeof Prism !== 'undefined') {
            const codeElement = document.getElementById('builderModalCodeContent');
            if (codeElement) {
                Prism.highlightElement(codeElement);
            }
        }
        
        // Close on background click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                this.closeBuilderPreviewModal();
            }
        });
        
        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape' && !window.builderPreviewEditMode) {
                this.closeBuilderPreviewModal();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
        
        console.log('[TestBuilder] Preview modal opened');
    },
    
    // Edit Builder Code
    editBuilderCode() {
        console.log('[TestBuilder] Entering edit mode');
        window.builderPreviewEditMode = true;
        
        // Hide view mode, show edit mode
        const viewMode = document.getElementById('builderModalViewMode');
        const editMode = document.getElementById('builderModalEditMode');
        
        if (viewMode) viewMode.style.display = 'none';
        if (editMode) editMode.style.display = 'flex';
        
        // Update action buttons
        const actionsDiv = document.getElementById('builderModalActions');
        if (actionsDiv) {
            actionsDiv.innerHTML = `
                <button onclick="window.TestBuilder.saveBuilderCodeEdits()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ✅ Save Changes
                </button>
                <button onclick="window.TestBuilder.cancelBuilderCodeEdit()" style="padding: 8px 16px; background: #6B7280; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ❌ Cancel
                </button>
            `;
        }
        
        // Focus on the editor
        const editor = document.getElementById('builderModalCodeEditor');
        if (editor) {
            editor.focus();
        }
    },
    
    // Cancel Builder Code Edit
    cancelBuilderCodeEdit() {
        console.log('[TestBuilder] Cancelling edit mode');
        window.builderPreviewEditMode = false;
        
        // Show view mode, hide edit mode
        const viewMode = document.getElementById('builderModalViewMode');
        const editMode = document.getElementById('builderModalEditMode');
        
        if (viewMode) viewMode.style.display = 'block';
        if (editMode) editMode.style.display = 'none';
        
        // Restore original action buttons
        const actionsDiv = document.getElementById('builderModalActions');
        if (actionsDiv) {
            actionsDiv.innerHTML = `
                <button onclick="window.TestBuilder.executeFromModal()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ▶️ Execute
                </button>
                <button onclick="window.TestBuilder.editBuilderCode()" style="padding: 8px 16px; background: #F59E0B; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ✏️ Edit
                </button>
                <button onclick="window.TestBuilder.copyBuilderPreviewCode()" style="padding: 8px 16px; background: #7C3AED; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    📋 Copy
                </button>
                <button onclick="window.TestBuilder.exportBuilderPreviewCode()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    💾 Export
                </button>
                <button onclick="window.TestBuilder.closeBuilderPreviewModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">
                    ✕
                </button>
            `;
        }
        
        // Reset editor content to original
        const editor = document.getElementById('builderModalCodeEditor');
        if (editor) {
            editor.value = window.builderPreviewCurrentCode;
        }
    },
    
    // Save Builder Code Edits
    async saveBuilderCodeEdits() {
        console.log('[TestBuilder] Saving edited code');
        
        const editor = document.getElementById('builderModalCodeEditor');
        if (!editor) {
            this.showToast('❌ Editor not found', 'error');
            return;
        }
        
        const editedCode = editor.value;
        const language = window.builderPreviewCurrentLanguage;
        
        if (!editedCode || editedCode.trim() === '') {
            this.showToast('⚠️ Cannot save empty code', 'warning');
            return;
        }
        
        // Update the current code
        window.builderPreviewCurrentCode = editedCode;
        
        // Exit edit mode
        window.builderPreviewEditMode = false;
        
        // Update view mode with edited code
        const codeElement = document.getElementById('builderModalCodeContent');
        if (codeElement) {
            codeElement.textContent = editedCode;
            // Re-apply syntax highlighting
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(codeElement);
            }
        }
        
        // Show view mode, hide edit mode
        const viewMode = document.getElementById('builderModalViewMode');
        const editMode = document.getElementById('builderModalEditMode');
        
        if (viewMode) viewMode.style.display = 'block';
        if (editMode) editMode.style.display = 'none';
        
        // Restore action buttons
        const actionsDiv = document.getElementById('builderModalActions');
        if (actionsDiv) {
            actionsDiv.innerHTML = `
                <button onclick="window.TestBuilder.executeFromModal()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ▶️ Execute
                </button>
                <button onclick="window.TestBuilder.editBuilderCode()" style="padding: 8px 16px; background: #F59E0B; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    ✏️ Edit
                </button>
                <button onclick="window.TestBuilder.copyBuilderPreviewCode()" style="padding: 8px 16px; background: #7C3AED; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    📋 Copy
                </button>
                <button onclick="window.TestBuilder.exportBuilderPreviewCode()" style="padding: 8px 16px; background: #10B981; color: white; border: none; border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                    💾 Export
                </button>
                <button onclick="window.TestBuilder.closeBuilderPreviewModal()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">
                    ✕
                </button>
            `;
        }
        
        this.showToast('✅ Changes saved! Code will be used when saving to Test Suite', 'success');
    },
    
    // Close Builder Preview Modal
    closeBuilderPreviewModal() {
        const modal = document.getElementById('builderPreviewModal');
        if (modal) {
            modal.remove();
        }
    },
    
    // Switch language in Builder Preview Modal
    async switchBuilderPreviewLanguage(language) {
        console.log('[TestBuilder] Switching to language:', language);
        
        const codeElement = document.getElementById('builderModalCodeContent');
        
        if (!codeElement) return;
        
        const languageMap = {
            'python': 'python',
            'java': 'java',
            'javascript': 'javascript',
            'cypress': 'javascript'
        };
        
        // Show loading
        codeElement.textContent = 'Loading code preview...';
        codeElement.className = `language-${languageMap[language]}`;
        
        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/preview?language=${language}`
            );
            
            const data = await response.json();
            
            if (data.success && data.code) {
                codeElement.textContent = data.code;
                window.builderPreviewCurrentCode = data.code;
                window.builderPreviewCurrentLanguage = language;
                
                // Re-apply syntax highlighting
                if (typeof Prism !== 'undefined') {
                    Prism.highlightElement(codeElement);
                }
            } else {
                throw new Error(data.error || 'Failed to generate code');
            }
        } catch (error) {
            console.error('[TestBuilder] Error switching language:', error);
            codeElement.textContent = `// Error loading ${language} code\n// ${error.message}`;
            codeElement.style.color = '#f87171';
        }
    },
    
    // Copy code from Builder Preview Modal
    copyBuilderPreviewCode() {
        // Get code from editor if in edit mode, otherwise from stored code
        const code = window.builderPreviewEditMode 
            ? document.getElementById('builderModalCodeEditor')?.value
            : window.builderPreviewCurrentCode;
        
        if (!code || code.includes('Error loading') || code.includes('Loading code preview')) {
            this.showToast('⚠️ No code to copy yet', 'warning');
            return;
        }
        
        navigator.clipboard.writeText(code).then(() => {
            this.showToast('📋 Code copied to clipboard!', 'success');
            console.log('[TestBuilder] Code copied, length:', code.length);
        }).catch(err => {
            console.error('[TestBuilder] Copy failed:', err);
            this.showToast('❌ Failed to copy code', 'error');
        });
    },
    
    // Export code from Builder Preview Modal
    exportBuilderPreviewCode() {
        // Get code from editor if in edit mode, otherwise from stored code
        const code = window.builderPreviewEditMode 
            ? document.getElementById('builderModalCodeEditor')?.value
            : window.builderPreviewCurrentCode;
        const language = window.builderPreviewCurrentLanguage || 'python';
        const testName = this.currentSession.name || 'TestCase';
        
        if (!code || code.includes('Error loading') || code.includes('Loading code preview')) {
            this.showToast('⚠️ No code to export yet', 'warning');
            return;
        }
        
        const extensionMap = {
            'python': '.py',
            'java': '.java',
            'javascript': '.js',
            'cypress': '.cy.js'
        };
        
        const extension = extensionMap[language] || '.py';
        const filename = `${testName.replace(/\s+/g, '_')}${extension}`;
        
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        
        this.showToast(`💾 Exported as ${filename}`, 'success');
    },
    
    // Execute test from modal
    async executeFromModal() {
        console.log('[TestBuilder] executeFromModal() called');
        // Close modal first
        this.closeBuilderPreviewModal();
        // Then execute test
        await this.executeTest();
    },

    // Copy code from card
    copyCodeFromCard() {
        const code = document.getElementById('codePreviewCardContent').textContent;
        
        if (code.includes('Error loading') || code.includes('Loading code preview')) {
            this.showToast('⚠️ No code to copy yet', 'warning');
            return;
        }
        
        navigator.clipboard.writeText(code).then(() => {
            this.showToast('📋 Code copied to clipboard!', 'success');
            console.log('[TestBuilder] Code copied, length:', code.length);
        }).catch(err => {
            console.error('[TestBuilder] Copy failed:', err);
            this.showToast('❌ Failed to copy code', 'error');
        });
    },

    // Update code preview
    async updatePreview() {
        const language = document.getElementById('previewLanguage').value;
        const codeElement = document.getElementById('codePreviewContent');
        
        codeElement.textContent = 'Loading...';
        codeElement.className = `language-${language}`;

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/preview?language=${language}`
            );

            const data = await response.json();

            if (data.success) {
                codeElement.textContent = data.code;
                // Re-highlight with Prism.js if available
                if (window.Prism) {
                    Prism.highlightElement(codeElement);
                }
            } else {
                throw new Error(data.error || 'Failed to generate preview');
            }
        } catch (error) {
            console.error('[TestBuilder] Error generating preview:', error);
            codeElement.textContent = '// Error generating code preview\n' + error.message;
        }
    },

    // Copy code to clipboard
    copyCode() {
        const code = document.getElementById('codePreviewContent').textContent;
        navigator.clipboard.writeText(code).then(() => {
            this.showToast('📋 Code copied to clipboard!', 'success');
        }).catch(err => {
            console.error('Copy failed:', err);
            this.showToast('❌ Failed to copy code', 'error');
        });
    },

    // Close code preview modal
    closeCodePreview() {
        document.getElementById('codePreviewModal').style.display = 'none';
    },

    // Save test case
    saveTestCase() {
        console.log('[TestBuilder] saveTestCase() called');
        console.log('[TestBuilder] currentSession:', this.currentSession);
        if (!this.currentSession) {
            this.showToast('⚠️ No active session', 'warning');
            return;
        }

        if (!this.currentSession.prompts || this.currentSession.prompts.length === 0) {
            this.showToast('⚠️ Add some steps first', 'warning');
            return;
        }

        document.getElementById('saveTestModal').style.display = 'flex';
        
        // Set current session name and default values
        document.getElementById('testName').value = this.currentSession.name || 'Untitled Test';
        document.getElementById('testTags').value = 'automation,generated';
        document.getElementById('testPriority').value = 'high';
    },

    // Close save modal
    closeSaveModal() {
        document.getElementById('saveTestModal').style.display = 'none';
    },

    // Confirm save
    async confirmSave() {
        const testName = document.getElementById('testName').value.trim();
        const tagsInput = document.getElementById('testTags').value.trim();
        const priority = document.getElementById('testPriority').value;
        const testType = document.getElementById('testType').value || 'regression';

        if (!testName) {
            this.showToast('⚠️ Please enter a test name', 'warning');
            return;
        }

        const tags = tagsInput ? tagsInput.split(',').map(t => t.trim()).filter(t => t) : [];

        this.closeSaveModal();
        this.showLoading(`Saving ${testName}`);

        try {
            const response = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/save`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ name: testName, tags, priority, test_type: testType })
                }
            );

            const data = await response.json();

            if (data.success) {
                // Update session with test_case_id to prevent duplicate saves
                this.currentSession.test_case_id = data.test_case.test_case_id;
                
                // Show success message with test name (not just ID)
                this.showToast(`✅ Test case "${data.test_case.name}" saved!`, 'success');
                
                // Update dashboard: INCREMENT only Tests Generated counter
                if (typeof window.incrementTestsGenerated === 'function') {
                    window.incrementTestsGenerated();
                    console.log('[TestBuilder] Dashboard: Test Generated counter incremented');
                }
                
                // DO NOT call addActivityLog here - it marks test as "passed" without execution!
                // addActivityLog should ONLY be called when test is actually executed
                
                // Reload test cases in Test Builder
                await this.loadTestCases();
                
                // Reload Test Suite if it's open
                if (typeof window.loadTestCases === 'function') {
                    console.log('[TestBuilder] Reloading Test Suite after save');
                    await window.loadTestCases();
                }
                
                // Close the save modal
                this.closeSaveModal();
                
                // Show permanent success notification
                setTimeout(() => {
                    alert(`✅ Test Case Saved Successfully!\n\nTest ID: ${data.test_case.test_case_id}\nName: ${data.test_case.name}\n\nYou can now find it in the Test Suite page.`);
                }, 300);
            } else {
                throw new Error(data.error || 'Failed to save test case');
            }
        } catch (error) {
            console.error('[TestBuilder] Error saving test case:', error);
            this.showToast('❌ Failed to save: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Open semantic analysis for current session
    async openSemanticAnalysis() {
        console.log('[TestBuilder] openSemanticAnalysis() called');
        console.log('[TestBuilder] currentSession:', this.currentSession);
        if (!this.currentSession) {
            this.showToast('⚠️ Please create and save a test session first', 'warning');
            return;
        }

        // Check if session has steps
        if (!this.currentSession.prompts || this.currentSession.prompts.length === 0) {
            this.showToast('⚠️ Add some test steps first', 'warning');
            return;
        }

        // Check if test case is saved (has test_case_id)
        if (!this.currentSession.test_case_id) {
            const confirmSave = confirm('💡 Your test needs to be saved before analyzing with AI.\n\nWould you like to save it now?\n\nClick OK to save, or Cancel to go back.');
            if (!confirmSave) {
                return;
            }
            
            // Show save modal and inform user to try again after saving
            this.saveTestCase();
            alert('ℹ️ After saving, click "AI Analysis" again to generate test variations.');
            return;
        }

        // Store test case ID (not session ID) for semantic analysis page to use
        sessionStorage.setItem('semanticAnalysisSessionId', this.currentSession.test_case_id);
        sessionStorage.setItem('semanticAnalysisSessionName', this.currentSession.name);
        
        this.showToast('📊 Opening AI Semantic Analysis...', 'success');
        
        // Navigate to semantic analysis page
        setTimeout(() => {
            if (typeof navigateTo === 'function') {
                navigateTo('semantic');
            } else if (typeof window.navigateTo === 'function') {
                window.navigateTo('semantic');
            } else {
                // Fallback: direct navigation
                window.location.hash = '#semantic';
            }
        }, 500);
    },

    // Execute test
    async executeTest() {
        console.log('[TestBuilder] executeTest() called');
        console.log('[TestBuilder] currentSession:', this.currentSession);
        if (!this.currentSession) {
            this.showToast('⚠️ No active session', 'warning');
            return;
        }

        if (!this.currentSession.prompts || this.currentSession.prompts.length === 0) {
            this.showToast('⚠️ Add some steps first', 'warning');
            return;
        }

        // Execute without saving (test first, save later if successful)
        this.showLoading('Running test', true); // true = show cancel button

        // Create AbortController for cancellation
        this.executionAbortController = new AbortController();

        try {
            // Execute session directly without saving
            const execResponse = await fetch(
                `${this.API_BASE}/test-suite/session/${this.currentSession.session_id}/execute`,
                {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ headless: false }),
                    signal: this.executionAbortController.signal
                }
            );

            if (!execResponse.ok) {
                const errorText = await execResponse.text();
                console.error('[TestBuilder] Execute API error:', execResponse.status, errorText);
                throw new Error(`Server error (${execResponse.status}): ${errorText}`);
            }

            const execData = await execResponse.json();
            
            // Debug log for screenshot data
            console.log('[TestBuilder Screenshot Debug] execData:', execData);
            console.log('[TestBuilder Screenshot Debug] execData.result:', execData.result);
            console.log('[TestBuilder Screenshot Debug] execData.execution_result:', execData.execution_result);

            if (execData.success) {
                const result = execData.result || execData.execution_result || {};
                const duration = result.duration || 0;
                const status = result.status || 'passed';
                const screenshots = result.screenshots || [];
                
                console.log('[TestBuilder Screenshot Debug] screenshots array:', screenshots);
                
                // Build toast message
                let message = `✅ Test execution ${status}! Duration: ${duration.toFixed(2)}s`;
                if (screenshots.length > 0) {
                    message += `\n📸 ${screenshots.length} error screenshot${screenshots.length > 1 ? 's' : ''} captured`;
                }
                message += '\n💡 Save the test if you want to run it in Test Suite';
                
                this.showToast(message, status === 'passed' ? 'success' : 'warning');
                
                // Display screenshots if any errors occurred
                if (screenshots.length > 0) {
                    this.displayExecutionScreenshots(screenshots);
                }
                
                // Log activity to dashboard timeline
                if (typeof window.addActivityLog === 'function') {
                    const testName = this.currentSession.name || 'Untitled Test';
                    window.addActivityLog(
                        `Test Builder: ${testName}`,
                        status === 'passed' ? 'passed' : 'failed',
                        duration * 1000, // Convert to ms
                        `Executed ${this.currentSession.prompts.length} steps`
                    );
                }
                
                // Don't save automatically - let user decide to save after successful execution
            } else {
                throw new Error(execData.error || 'Test execution failed');
            }
        } catch (error) {
            if (error.name === 'AbortError') {
                console.log('[TestBuilder] Test execution cancelled by user');
                this.showToast('⚠️ Test execution cancelled', 'warning');
            } else {
                console.error('[TestBuilder] Error executing test:', error);
                this.showToast('❌ Execution failed: ' + error.message, 'error');
            }
        } finally {
            this.executionAbortController = null;
            this.hideLoading();
        }
    },

    // Cancel test execution
    cancelExecution() {
        console.log('[TestBuilder] cancelExecution called');
        if (this.executionAbortController) {
            console.log('[TestBuilder] Aborting test execution...');
            this.executionAbortController.abort();
            this.executionAbortController = null;
            // Immediately hide loading
            this.hideLoading();
            this.showToast('⚠️ Test execution cancelled', 'warning');
        } else {
            console.log('[TestBuilder] No execution to cancel');
            this.hideLoading();
        }
    },

    // Clear current session
    async clearSession() {
        if (this.currentSession) {
            if (!confirm('Clear current test session? Unsaved changes will be lost.')) {
                return;
            }
            
            // Delete session from server
            try {
                await fetch(`${this.API_BASE}/test-suite/session/${this.currentSession.session_id}`, {
                    method: 'DELETE'
                });
            } catch (error) {
                console.error('[TestBuilder] Error deleting session:', error);
            }
        }
        
        this.currentSession = null;
        this.updateUI();
        await this.loadSessions(); // Refresh sessions list
        this.showToast('🗑️ Session cleared', 'info');
    },

    // Load all sessions
    async loadSessions() {
        try {
            const response = await fetch(`${this.API_BASE}/test-suite/sessions`);
            const data = await response.json();

            if (data.success) {
                this.sessions = data.sessions || [];
                this.renderSessions();
                this.updateStats();
            }
        } catch (error) {
            console.error('[TestBuilder] Error loading sessions:', error);
            const container = document.getElementById('activeSessions');
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                        Error loading sessions
                    </div>
                `;
            }
        }
    },

    // Render sessions list
    renderSessions() {
        const container = document.getElementById('activeSessions');
        const countBadge = document.getElementById('activeSessionCount');

        // Exit early if elements don't exist (e.g., on different page)
        if (!container) {
            console.log('[TestBuilder] activeSessions container not found, skipping render');
            return;
        }

        if (this.sessions.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 30px 20px; color: var(--text-secondary); opacity: 0.7;">
                    <div style="font-size: 2.5em; margin-bottom: 10px;">⏱️</div>
                    <div style="font-size: 0.9em;">No active sessions</div>
                </div>
            `;
            if (countBadge) countBadge.textContent = '0';
            return;
        }

        // Update count badge
        if (countBadge) countBadge.textContent = this.sessions.length;

        container.innerHTML = this.sessions.map(session => `
            <div class="session-item" 
                 onclick="TestBuilder.loadSession('${session.session_id}')"
                 style="padding: 14px; background: var(--bg-primary); border-radius: 10px; margin-bottom: 10px; 
                        border: 1px solid var(--border-color); border-left: 4px solid #fb923c; 
                        cursor: pointer; transition: all 0.3s;"
                 onmouseover="this.style.transform='translateX(4px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'; this.style.borderColor='#fb923c'"
                 onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-color)'">
                
                <div style="font-weight: 700; color: #fb923c; font-size: 0.85em; margin-bottom: 8px;">
                    🔗 ${session.session_id.substring(0, 8)}
                </div>
                
                <div style="font-size: 0.9em; color: var(--text-primary); margin-bottom: 8px; font-weight: 500;">
                    ${this.escapeHtml(session.name)}
                </div>
                
                <div style="display: flex; align-items: center; gap: 8px; font-size: 0.75em; color: var(--text-secondary);">
                    <span style="display: flex; align-items: center; gap: 4px;">
                        <span style="font-size: 1.2em;">📝</span>
                        <strong>${session.prompt_count}</strong> steps
                    </span>
                </div>
            </div>
        `).join('');
    },

    // Load specific session
    async loadSession(sessionId) {
        this.showLoading('Loading session');

        try {
            const response = await fetch(`${this.API_BASE}/test-suite/session/${sessionId}`);
            const data = await response.json();

            if (data.success) {
                this.currentSession = data.session;
                this.renderSteps();
                this.updateUI();
                this.showToast('✅ Session loaded', 'success');
            } else {
                throw new Error(data.error || 'Failed to load session');
            }
        } catch (error) {
            console.error('[TestBuilder] Error loading session:', error);
            this.showToast('❌ Failed to load session: ' + error.message, 'error');
        } finally {
            this.hideLoading();
            this.hideLoading();
        }
    },

    // Load all test cases
    async loadTestCases() {
        try {
            const response = await fetch(`${this.API_BASE}/test-suite/test-cases`);
            const data = await response.json();

            if (data.success) {
                this.testCases = data.test_cases || [];
                
                // Sort by timestamp descending (newest first)
                this.testCases.sort((a, b) => {
                    const timeA = a.created_at || a.timestamp || 0;
                    const timeB = b.created_at || b.timestamp || 0;
                    return timeB - timeA;  // Descending order (newest first)
                });
                
                this.renderTestCases();
                this.updateStats();
                console.log('[TestBuilder] Loaded test cases:', this.testCases.length);
            }
        } catch (error) {
            console.error('[TestBuilder] Error loading test cases:', error);
            const container = document.getElementById('savedTestCases');
            if (container) {
                container.innerHTML = `
                    <div style="text-align: center; padding: 20px; color: var(--text-secondary);">
                        Error loading test cases
                    </div>
                `;
            }
        }
    },

    // Render test cases list
    renderTestCases() {
        const container = document.getElementById('savedTestCases');
        const countBadge = document.getElementById('savedTestCount');

        // Exit early if elements don't exist (e.g., on different page)
        if (!container) {
            console.log('[TestBuilder] savedTestCases container not found, skipping render');
            return;
        }

        if (this.testCases.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 30px 20px; color: var(--text-secondary); opacity: 0.7;">
                    <div style="font-size: 2.5em; margin-bottom: 10px;">📋</div>
                    <div style="font-size: 0.9em;">No saved tests yet</div>
                </div>
            `;
            if (countBadge) countBadge.textContent = '0';
            return;
        }

        // Update count badge
        if (countBadge) countBadge.textContent = this.testCases.length;

        container.innerHTML = this.testCases.map(tc => `
            <div class="test-case-item" onclick="TestBuilder.viewTestCase('${tc.test_case_id}')" 
                 style="padding: 14px; background: var(--bg-primary); border-radius: 10px; margin-bottom: 10px; 
                        border: 1px solid var(--border-color); border-left: 4px solid ${this.getPriorityColor(tc.priority)}; 
                        cursor: pointer; transition: all 0.3s; position: relative; overflow: hidden;"
                 onmouseover="this.style.transform='translateX(4px)'; this.style.boxShadow='0 4px 12px rgba(0,0,0,0.15)'; this.style.borderColor='${this.getPriorityColor(tc.priority)}'"
                 onmouseout="this.style.transform='translateX(0)'; this.style.boxShadow='none'; this.style.borderColor='var(--border-color)'">
                
                <!-- Priority indicator -->
                <div style="position: absolute; top: 10px; right: 10px;">
                    <span style="font-size: 0.7em; padding: 4px 8px; background: ${this.getPriorityColor(tc.priority)}; 
                                 color: white; border-radius: 12px; font-weight: 600; text-transform: uppercase; 
                                 letter-spacing: 0.5px; box-shadow: 0 2px 4px rgba(0,0,0,0.2);">
                        ${tc.priority}
                    </span>
                </div>
                
                <!-- Test ID -->
                <div style="font-weight: 700; color: var(--primary-color); font-size: 0.95em; margin-bottom: 8px; padding-right: 80px;">
                    ${tc.test_case_id}
                </div>
                
                <!-- Test Name -->
                <div style="font-size: 0.9em; color: var(--text-primary); margin-bottom: 10px; line-height: 1.4; font-weight: 500;">
                    ${this.escapeHtml(tc.name)}
                </div>
                
                <!-- Metadata -->
                <div style="display: flex; align-items: center; gap: 12px; font-size: 0.75em; color: var(--text-secondary);">
                    <span style="display: flex; align-items: center; gap: 4px;">
                        <span style="font-size: 1.2em;">📝</span>
                        <strong>${tc.step_count}</strong> steps
                    </span>
                    <span style="opacity: 0.5;">•</span>
                    <span style="display: flex; align-items: center; gap: 4px;">
                        <span style="font-size: 1.2em;">🏷️</span>
                        ${tc.tags.slice(0, 2).join(', ')}${tc.tags.length > 2 ? '...' : ''}
                    </span>
                </div>
            </div>
        `).join('');
    },

    // View test case details
    async viewTestCase(testCaseId) {
        console.log('[TestBuilder] Viewing test case:', testCaseId);
        
        try {
            const response = await fetch(`${this.API_BASE}/test-suite/test-cases/${testCaseId}`);
            const data = await response.json();
            
            if (data.success && data.test_case) {
                const tc = data.test_case;
                console.log('[ViewTest] Test case data:', tc);
                
                // Show code modal like Recorder does
                this.showCodeModal(tc);
            } else {
                this.showToast('❌ Failed to load test case details', 'error');
            }
        } catch (error) {
            console.error('[TestBuilder] Error viewing test case:', error);
            this.showToast('❌ Error loading test case: ' + error.message, 'error');
        }
    },

    // Show code modal (like Recorder)
    showCodeModal(testCase) {
        const modal = document.createElement('div');
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.8); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        const pythonCode = testCase.generated_code?.python || '# Python code not generated';
        const javaCode = testCase.generated_code?.java || '// Java code not generated';
        const jsCode = testCase.generated_code?.javascript || '// JavaScript code not generated';
        const cypressCode = testCase.generated_code?.cypress || '// Cypress code not generated';
        
        const stepsHtml = testCase.steps ? testCase.steps.map((s, i) => 
            `<div style="padding: 8px; margin: 4px 0; background: var(--accent-bg, rgba(124, 58, 237, 0.1)); border-left: 3px solid var(--accent, #7C3AED); border-radius: 4px;">
                <strong style="color: var(--accent, #7C3AED);">${i + 1}.</strong> ${s.prompt}
                ${s.value ? `<span style="color: var(--success, #10b981); margin-left: 10px;">→ "${s.value}"</span>` : ''}
            </div>`
        ).join('') : '<div>No steps</div>';
        
        modal.innerHTML = `
            <div style="width: 90%; max-width: 1200px; height: 90vh; background: var(--bg-secondary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden;">
                <!-- Modal Header -->
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 2px solid var(--border-color);">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">📋 ${testCase.name}</h3>
                    <button onclick="this.closest('.modal-overlay-custom').remove()" style="padding: 8px 16px; background: transparent; border: 1px solid var(--border-color); color: var(--text-primary); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">✕</button>
                </div>
                
                <!-- Test Details -->
                <div style="padding: 16px 24px; border-bottom: 1px solid var(--border-color);">
                    <p style="margin: 5px 0; color: var(--text-secondary); font-size: 13px;"><strong>ID:</strong> ${testCase.test_case_id} &nbsp;&nbsp; <strong>Priority:</strong> ${testCase.priority} &nbsp;&nbsp; <strong>Tags:</strong> ${testCase.tags.join(', ')}</p>
                </div>
                
                <!-- Test Steps Summary -->
                <div style="padding: 16px 24px; border-bottom: 1px solid var(--border-color); max-height: 150px; overflow-y: auto;">
                    <h4 style="margin: 0 0 10px 0; color: var(--text-primary); font-size: 14px; font-weight: 600;">📝 Test Steps (${testCase.steps?.length || 0}):</h4>
                    <div style="font-size: 13px;">
                        ${stepsHtml}
                    </div>
                </div>
                
                <!-- Language Selector -->
                <div style="padding: 8px 24px; border-bottom: 1px solid var(--border-color); display: flex; align-items: center; gap: 10px;">
                    <label style="color: var(--text-primary); font-weight: 600; font-size: 13px;">Language:</label>
                    <select id="codeLanguageSelect" onchange="window.TestBuilder.switchCodeLanguage(this.value)" style="padding: 4px 8px; border-radius: 4px; background: var(--bg-secondary); color: var(--text-primary); border: 1px solid var(--border-color); font-size: 12px; cursor: pointer; font-weight: 500; max-width: 200px;">
                        <option value="python">🐍 Python</option>
                        <option value="java">☕ Java</option>
                        <option value="javascript">🟨 JavaScript</option>
                        <option value="cypress">🌲 Cypress</option>
                    </select>
                </div>
                
                <!-- Code Viewer -->
                <div class="code-modal-body" style="flex: 1; overflow: auto; padding: 0;">
                    <pre style="margin: 0; padding: 24px; height: 100%;"><code id="codeDisplay" class="language-python" style="font-size: 14px; line-height: 1.6; display: block; white-space: pre;">${this.escapeHtml(pythonCode)}</code></pre>
                </div>
                
                <div style="display: none;" id="codeDataHolder" data-python="${this.escapeHtml(pythonCode)}" data-java="${this.escapeHtml(javaCode)}" data-javascript="${this.escapeHtml(jsCode)}" data-cypress="${this.escapeHtml(cypressCode)}"></div>
            </div>
        `;
        
        modal.className = 'modal-overlay-custom';
        document.body.appendChild(modal);
    },
    
    // Switch code language in modal
    switchCodeLanguage(lang) {
        const codeDisplay = document.getElementById('codeDisplay');
        const dataHolder = document.getElementById('codeDataHolder');
        if (codeDisplay && dataHolder) {
            const code = dataHolder.getAttribute(`data-${lang}`);
            codeDisplay.textContent = code || `// ${lang} code not generated`;
        }
    },
    
    // Escape HTML for display
    escapeHtml(text) {
        const map = {
            '&': '&amp;',
            '<': '&lt;',
            '>': '&gt;',
            '"': '&quot;',
            "'": '&#039;'
        };
        return text.replace(/[&<>"']/g, m => map[m]);
    },

    // Display execution screenshots in a modal
    displayExecutionScreenshots(screenshots) {
        if (!screenshots || screenshots.length === 0) return;

        const modal = document.createElement('div');
        modal.style.cssText = `
            position: fixed;
            top: 0;
            left: 0;
            width: 100vw;
            height: 100vh;
            background: rgba(0, 0, 0, 0.85);
            display: flex;
            align-items: center;
            justify-content: center;
            z-index: 10000;
            backdrop-filter: blur(5px);
        `;

        const screenshotsHtml = screenshots.map((s, i) => {
            // Handle screenshot paths - supports both builder and recorder
            let screenshotPath = s.path || s.filepath || '';
            
            // If path is absolute, convert to relative web path
            if (screenshotPath.includes('execution_results')) {
                screenshotPath = screenshotPath
                    .replace(/\\/g, '/')  // Convert backslashes
                    .split('execution_results/').pop();  // Get part after execution_results/
                screenshotPath = `execution_results/${screenshotPath}`;
            }
            
            // Ensure path starts with / for web access
            const webPath = screenshotPath.startsWith('/') ? screenshotPath : `/${screenshotPath}`;
            
            const description = s.error ? `Step ${s.step}: ${s.error}` : (s.description || `Screenshot ${i + 1}`);
            const source = s.source === 'recorder' ? '🎬 Recorder' : '🧪 Builder';
            
            return `
            <div style="margin-bottom: 15px; padding: 12px; background: var(--bg-secondary); border-radius: 8px; border-left: 4px solid #ef4444;">
                <div style="font-weight: 600; color: var(--text-primary); margin-bottom: 4px;">
                    ${description}
                </div>
                <div style="font-size: 0.85em; color: var(--text-secondary); margin-bottom: 8px;">
                    ${source} • ${s.timestamp ? new Date(s.timestamp).toLocaleString() : ''}
                </div>
                <a href="${webPath}" target="_blank" style="display: inline-block; padding: 8px 16px; background: #3b82f6; color: white; text-decoration: none; border-radius: 6px; font-size: 14px;">
                    📸 Open Screenshot
                </a>
            </div>
        `;
        }).join('');

        modal.innerHTML = `
            <div style="width: 90%; max-width: 600px; background: var(--bg-primary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); overflow: hidden;">
                <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 2px solid var(--border-color); background: var(--bg-secondary);">
                    <h3 style="margin: 0; color: var(--text-primary); font-size: 18px; font-weight: 600;">
                        📸 Failure Screenshots (${screenshots.length})
                    </h3>
                    <button onclick="this.closest('div[style*=\"position: fixed\"]').remove()" style="background: #ef4444; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 16px; font-weight: 600;">
                        ✕
                    </button>
                </div>
                <div style="padding: 24px; max-height: 400px; overflow-y: auto;">
                    ${screenshotsHtml}
                </div>
                <div style="padding: 16px 24px; background: var(--bg-tertiary); border-top: 1px solid var(--border-color); color: var(--text-secondary); font-size: 14px;">
                    💡 Builder: <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">execution_results/builder/screenshots/</code><br>
                    💡 Recorder: <code style="background: rgba(0,0,0,0.3); padding: 2px 6px; border-radius: 4px;">execution_results/recorder/screenshots/</code>
                </div>
            </div>
        `;

        document.body.appendChild(modal);

        // Close on outside click
        modal.addEventListener('click', (e) => {
            if (e.target === modal) {
                modal.remove();
            }
        });

        // Close on Escape key
        const escapeHandler = (e) => {
            if (e.key === 'Escape') {
                modal.remove();
                document.removeEventListener('keydown', escapeHandler);
            }
        };
        document.addEventListener('keydown', escapeHandler);
    },

    // Update UI based on current state
    updateUI() {
        const noSessionState = document.getElementById('noSessionState');
        const activeSessionState = document.getElementById('activeSessionState');
        const sessionInfo = document.getElementById('sessionInfo');

        // Exit early if elements don't exist (e.g., on different page)
        if (!noSessionState || !activeSessionState || !sessionInfo) {
            console.log('[TestBuilder] UI elements not found, skipping updateUI');
            return;
        }

        if (this.currentSession) {
            noSessionState.style.display = 'none';
            activeSessionState.style.display = 'block';
            sessionInfo.style.display = 'block';

            // Update session info with null checks
            const testNameEl = document.getElementById('currentTestName');
            const sessionIdEl = document.getElementById('currentSessionId');
            const stepCountEl = document.getElementById('currentStepCount');
            
            if (testNameEl) testNameEl.textContent = this.currentSession.name || 'Untitled Test';
            if (sessionIdEl) sessionIdEl.textContent = this.currentSession.session_id || '-';
            if (stepCountEl) stepCountEl.textContent = this.currentSession.prompt_count || 0;

            // Render steps
            this.renderSteps();
        } else {
            noSessionState.style.display = 'block';
            activeSessionState.style.display = 'none';
            sessionInfo.style.display = 'none';
        }
    },

    // Update stats
    updateStats() {
        const totalTests = this.testCases.length;
        const activeSessions = this.sessions.length;
        
        const statTotalTestsEl = document.getElementById('statTotalTests');
        const statActiveSessionsEl = document.getElementById('statActiveSessions');
        
        if (statTotalTestsEl) statTotalTestsEl.textContent = totalTests;
        if (statActiveSessionsEl) statActiveSessionsEl.textContent = activeSessions;
        
        console.log('[TestBuilder] Stats updated - Total Tests:', totalTests, 'Active Sessions:', activeSessions);
    },

    // Helper: Get priority color
    getPriorityColor(priority) {
        const colors = {
            low: '#6b7280',
            medium: '#3b82f6',
            high: '#f59e0b',
            critical: '#ef4444'
        };
        return colors[priority] || colors.medium;
    },

    // Helper: Render match strategy badge
    renderMatchStrategy(parsed) {
        const strategy = parsed.match_strategy;
        const confidence = parsed.confidence;
        
        if (!strategy) return '';
        
        const strategyInfo = {
            'exact': {
                icon: '✓',
                label: 'Exact Match',
                color: '#10b981',
                bgColor: 'rgba(16, 185, 129, 0.1)',
                tooltip: '100% match from dataset'
            },
            'template': {
                icon: '📋',
                label: 'Template Match',
                color: '#3b82f6',
                bgColor: 'rgba(59, 130, 246, 0.1)',
                tooltip: 'Matched pattern with extracted parameters'
            },
            'fuzzy': {
                icon: '≈',
                label: 'Similar Match',
                color: '#f59e0b',
                bgColor: 'rgba(245, 158, 11, 0.1)',
                tooltip: 'Found similar pattern in dataset'
            },
            'ml': {
                icon: '🤖',
                label: 'ML Inference',
                color: '#8b5cf6',
                bgColor: 'rgba(139, 92, 246, 0.1)',
                tooltip: 'Generated using machine learning'
            }
        };
        
        const info = strategyInfo[strategy] || strategyInfo['ml'];
        const confidencePercent = Math.round(confidence * 100);
        
        return `<div style="font-size: 0.85em; margin-bottom: 8px;">
            <span style="background: ${info.bgColor}; color: ${info.color}; padding: 3px 8px; border-radius: 4px; font-weight: 500;" title="${info.tooltip}">
                ${info.icon} ${info.label} ${confidencePercent}%
            </span>
        </div>`;
    },

    // Helper: Escape HTML
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    },

    // UI Helpers
    showLoading(message = 'Loading...', showCancelButton = false) {
        const loading = document.getElementById('loading');
        const overlay = document.getElementById('loadingOverlay');
        
        if (loading) {
            const messageDiv = document.getElementById('loadingMessage');
            if (messageDiv) {
                messageDiv.textContent = message;
            }
            loading.style.display = 'flex';
            
            // Show overlay
            if (overlay) {
                overlay.style.display = 'block';
            }
            
            // Show/hide cancel button
            const cancelBtn = document.getElementById('cancelExecutionBtn');
            if (cancelBtn) {
                cancelBtn.style.display = showCancelButton ? 'block' : 'none';
                
                // Remove old event listener and add new one
                const newCancelBtn = cancelBtn.cloneNode(true);
                cancelBtn.parentNode.replaceChild(newCancelBtn, cancelBtn);
                newCancelBtn.addEventListener('click', () => {
                    console.log('[TestBuilder] Cancel button clicked');
                    this.cancelExecution();
                });
            }
        }
    },

    hideLoading() {
        const loading = document.getElementById('loading');
        const overlay = document.getElementById('loadingOverlay');
        
        if (loading) {
            loading.style.display = 'none';
        }
        
        // Hide overlay
        if (overlay) {
            overlay.style.display = 'none';
        }
        
        // Hide cancel button when loading is hidden
        const cancelBtn = document.getElementById('cancelExecutionBtn');
        if (cancelBtn) {
            cancelBtn.style.display = 'none';
        }
    },

    showToast(message, type = 'info') {
        // Use existing toast system if available, otherwise console
        if (window.showMessage) {
            window.showMessage(message, type);
        } else {
            console.log(`[TestBuilder] ${type.toUpperCase()}: ${message}`);
            alert(message);
        }
    },

    // ===== QUICK TEST (BROWSER CONTROL) METHODS =====
    
    // Switch between tabs
    switchTab(tabName) {
        const multiStepContent = document.getElementById('multiStepContent');
        const quickTestContent = document.getElementById('quickTestContent');
        const tabMultiStep = document.getElementById('tabMultiStep');
        const tabQuickTest = document.getElementById('tabQuickTest');

        if (tabName === 'multiStep') {
            multiStepContent.style.display = 'block';
            quickTestContent.style.display = 'none';
            tabMultiStep.classList.add('active');
            tabQuickTest.classList.remove('active');
            tabMultiStep.style.borderBottomColor = 'var(--primary-color)';
            tabMultiStep.style.color = 'var(--primary-color)';
            tabQuickTest.style.borderBottomColor = 'transparent';
            tabQuickTest.style.color = 'var(--text-secondary)';
        } else if (tabName === 'quickTest') {
            multiStepContent.style.display = 'none';
            quickTestContent.style.display = 'block';
            tabMultiStep.classList.remove('active');
            tabQuickTest.classList.add('active');
            tabQuickTest.style.borderBottomColor = 'var(--primary-color)';
            tabQuickTest.style.color = 'var(--primary-color)';
            tabMultiStep.style.borderBottomColor = 'transparent';
            tabMultiStep.style.color = 'var(--text-secondary)';
        }
    },

    // Initialize browser for quick testing
    async initializeBrowser() {
        const browserType = document.getElementById('quickBrowserType').value;
        const headless = document.getElementById('quickHeadlessMode').checked;
        
        this.showLoading('Initializing');
        
        try {
            const response = await fetch(`${this.API_BASE}/browser/initialize`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ browser: browserType, headless })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.browserInitialized = true;
                const statusDiv = document.getElementById('quickBrowserStatus');
                const statusText = document.getElementById('quickBrowserStatusText');
                statusDiv.style.display = 'block';
                statusText.textContent = '✅ Browser Ready';
                statusText.style.color = 'var(--success)';
                
                this.showToast('✅ Browser initialized successfully!', 'success');
            } else {
                throw new Error(data.message || data.error || 'Failed to initialize browser');
            }
        } catch (error) {
            console.error('[TestBuilder] Browser initialization error:', error);
            this.showToast('❌ Error: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Execute quick test command
    async executeQuickTest() {
        if (!this.browserInitialized) {
            this.showToast('Please initialize browser first', 'warning');
            return;
        }
        
        const prompt = document.getElementById('quickTestPrompt').value.trim();
        const url = document.getElementById('quickTestUrl').value.trim();
        
        if (!prompt) {
            this.showToast('Please enter a test command', 'warning');
            return;
        }
        
        this.showLoading('Running');
        
        try {
            // Generate code from prompt
            const generateResponse = await fetch(`${this.API_BASE}/generate`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ 
                    prompt: url ? `Navigate to ${url} then ${prompt}` : prompt,
                    language: 'python',
                    execute: false,
                    with_fallbacks: true,      // Enable self-healing with multiple selectors
                    compact_mode: true          // Generate compact code (70% smaller, perfect for DB/CI-CD)
                })
            });
            
            const generateData = await generateResponse.json();
            const code = generateData.code || generateData.generated;
            
            if (!code) {
                throw new Error('No code generated from prompt');
            }
            
            // Execute the generated code
            const executeResponse = await fetch(`${this.API_BASE}/browser/execute`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ code: code })
            });
            
            const executeData = await executeResponse.json();
            
            // Show result
            const resultDiv = document.getElementById('quickTestResult');
            const resultContent = document.getElementById('quickTestResultContent');
            resultDiv.style.display = 'block';
            resultContent.textContent = JSON.stringify(executeData, null, 2);
            
            if (executeData.success) {
                this.showToast('✅ Command executed successfully!', 'success');
            } else {
                this.showToast('⚠️ Execution completed with issues', 'warning');
            }
            
            // Add to history
            this.addToRecentCommands(prompt, url, executeData.success);
            
        } catch (error) {
            console.error('[TestBuilder] Quick test execution error:', error);
            this.showToast('❌ Error: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Close browser
    async closeBrowser() {
        this.showLoading('Closing');
        
        try {
            const response = await fetch(`${this.API_BASE}/browser/close`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.browserInitialized = false;
                const statusDiv = document.getElementById('quickBrowserStatus');
                statusDiv.style.display = 'none';
                
                // Clear result
                const resultDiv = document.getElementById('quickTestResult');
                resultDiv.style.display = 'none';
                
                this.showToast('✅ Browser closed', 'success');
            }
        } catch (error) {
            console.error('[TestBuilder] Browser close error:', error);
            this.showToast('❌ Error: ' + error.message, 'error');
        } finally {
            this.hideLoading();
        }
    },

    // Add command to recent history
    addToRecentCommands(prompt, url, success) {
        if (!this.recentCommands) {
            this.recentCommands = [];
        }
        
        this.recentCommands.unshift({
            prompt,
            url,
            success,
            timestamp: new Date().toLocaleString()
        });
        
        // Keep only last 10 commands
        if (this.recentCommands.length > 10) {
            this.recentCommands = this.recentCommands.slice(0, 10);
        }
        
        this.renderRecentCommands();
    },

    // Render recent commands list
    renderRecentCommands() {
        const container = document.getElementById('recentCommands');
        
        if (!this.recentCommands || this.recentCommands.length === 0) {
            container.innerHTML = `
                <div style="text-align: center; padding: 40px 20px; color: var(--text-secondary);">
                    No commands executed yet
                </div>
            `;
            return;
        }
        
        container.innerHTML = this.recentCommands.map(cmd => `
            <div style="padding: 12px; background: var(--bg-secondary); border-radius: 6px; margin-bottom: 8px; border-left: 3px solid ${cmd.success ? 'var(--success)' : 'var(--error)'};">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 6px;">
                    <span style="font-size: 1.2em;">${cmd.success ? '✅' : '❌'}</span>
                    <div style="flex: 1; font-size: 0.85em; color: var(--text-primary); font-weight: 500;">
                        ${this.escapeHtml(cmd.prompt)}
                    </div>
                </div>
                ${cmd.url ? `
                    <div style="font-size: 0.75em; color: var(--text-secondary); margin-bottom: 4px;">
                        🌐 ${this.escapeHtml(cmd.url)}
                    </div>
                ` : ''}
                <div style="font-size: 0.7em; color: var(--text-secondary);">
                    ${cmd.timestamp}
                </div>
            </div>
        `).join('');
    },

    // Update tests generated counter from localStorage
    updateTestsGeneratedCounter() {
        try {
            const stats = window.loadStats ? window.loadStats() : null;
            const testsGenerated = stats ? (stats.testsGenerated || 0) : 0;
            const counterEl = document.getElementById('builderTestsGenerated');
            if (counterEl) {
                counterEl.textContent = testsGenerated;
                console.log('[TestBuilder] Updated tests generated counter:', testsGenerated);
            }
        } catch (error) {
            console.error('[TestBuilder] Error updating counter:', error);
        }
    },

    // Show animated increment feedback
    showCounterIncrement() {
        const counterEl = document.getElementById('builderTestsGenerated');
        if (counterEl) {
            // Add pulse animation
            counterEl.style.transform = 'scale(1.3)';
            counterEl.style.color = 'var(--success-color)';
            setTimeout(() => {
                counterEl.style.transform = 'scale(1)';
                counterEl.style.color = 'var(--primary-color)';
            }, 300);
        }
    }
};

// Initialize when page loads
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        if (window.location.hash === '#testBuilder' || window.location.hash === '#test-builder') {
            TestBuilder.init();
        }
    });
} else {
    if (window.location.hash === '#testBuilder' || window.location.hash === '#test-builder') {
        TestBuilder.init();
    }
}

// Export for use in other modules
if (typeof window !== 'undefined') {
    window.TestBuilder = TestBuilder;
    console.log('[TestBuilder] Exported to window.TestBuilder');
    console.log('[TestBuilder] Available methods:', Object.keys(TestBuilder).filter(k => typeof TestBuilder[k] === 'function'));
}
