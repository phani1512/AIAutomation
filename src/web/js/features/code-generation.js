// Code Generation Features

// Store current alternatives for modal
let currentAlternatives = null;
let currentGeneratedCode = null;
let currentPrompt = null;

async function generateCode() {
    const promptInput = document.getElementById('promptInput');
    const languageSelector = document.getElementById('languageSelector');
    
    if (!promptInput) {
        console.error('Prompt input element not found - page may not be loaded yet');
        return;
    }
    
    const prompt = promptInput.value.trim();
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }

    const language = languageSelector ? languageSelector.value : 'java';
    console.log(`[CODE GEN] Generating ${language} code for: ${prompt}`);

    showLoading(true);
    const startTime = Date.now();

    try {
        const response = await authenticatedFetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                prompt,
                language: language,
                with_fallbacks: true,  // Include fallback selectors for robust code generation
                comprehensive_mode: true  // Enable all possible code variations for the prompt
            })
        });

        const data = await response.json();
        const endTime = Date.now();
        
        // NEW: Handle alternatives from HYBRID mode
        const alternatives = data.alternatives || [];
        console.log(`[ALTERNATIVES] Found ${alternatives.length} alternatives`);
        
        if (alternatives.length > 0) {
            // Store for modal
            currentAlternatives = alternatives;
            currentGeneratedCode = data.generated || data.code || '';
            currentPrompt = prompt;
        }
        
        displayResult(data.generated || data.code, endTime - startTime, data.tokens_generated || 0, language, alternatives);
    } catch (error) {
        displayError('Failed to generate code: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayResult(text, timeMs, tokens = 0, language = 'java', alternatives = []) {
    const codeElement = document.getElementById('resultContent');
    if (!codeElement) {
        console.error('Result content element not found - page may not be loaded yet');
        return;
    }
    
    // DEBUG: Log the generated code and alternatives details
    console.log(`[CODE GEN RESULT] Language: ${language}`);
    console.log(`[CODE GEN RESULT] Code length: ${text.length} chars`);
    console.log(`[CODE GEN RESULT] Alternatives: ${alternatives.length}`);
    console.log(`[CODE GEN RESULT] First 100 chars of code: ${text.substring(0, 100)}...`);
    if (alternatives.length > 0) {
        console.log(`[CODE GEN RESULT] Alternative prompts:`, alternatives.map(a => a.prompt));
    }
    console.log(`[CODE GEN] ✅ Generated code length: ${text.length} characters`);
    console.log(`[CODE GEN] First 200 chars: ${text.substring(0, 200)}`);
    if (text.length < 100) {
        console.warn(`[CODE GEN] ⚠️ WARNING: Code is suspiciously short! Full code: ${text}`);
    } else {
        console.log(`[CODE GEN] ✅ Code looks comprehensive (${text.length} chars)`);
    }
    
    codeElement.textContent = text;
    
    // Use the specified language for syntax highlighting
    codeElement.className = `language-${language}`;
    console.log(`[CODE GEN] Setting syntax highlight to: ${language}`);
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    // Safely update button visibility (elements might not be loaded yet)
    const copyBtn = document.getElementById('copyBtn');
    const validateBtn = document.getElementById('validateBtn');
    const saveSnippetBtn = document.getElementById('saveSnippetBtn');
    const exportBtn = document.getElementById('exportBtn');
    const validationResults = document.getElementById('validationResults');
    
    if (copyBtn) copyBtn.style.display = 'inline-flex';
    if (validateBtn) validateBtn.style.display = 'inline-flex';
    if (saveSnippetBtn) saveSnippetBtn.style.display = 'inline-flex';
    if (exportBtn) exportBtn.style.display = 'inline-flex';
    if (validationResults) validationResults.style.display = 'none';
    
    // Update stats
    window.stats.totalRequests++;
    window.stats.totalTokens += tokens;
    window.stats.totalTime += timeMs;
    
    // Save stats to localStorage
    if (typeof window.saveStats === 'function') {
        window.saveStats();
    }
    
    // Update main stats display (safely in case elements aren't loaded)
    const totalRequestsEl = document.getElementById('totalRequests');
    const tokensGeneratedEl = document.getElementById('tokensGenerated');
    const avgTimeEl = document.getElementById('avgTime');
    
    if (totalRequestsEl) totalRequestsEl.textContent = window.stats.totalRequests;
    if (tokensGeneratedEl) tokensGeneratedEl.textContent = window.stats.totalTokens;
    if (avgTimeEl) {
        avgTimeEl.textContent = window.stats.totalTime > 0 ? 
            Math.round(window.stats.totalTime / window.stats.totalRequests) + 'ms' : '0ms';
    }
    
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput ? promptInput.value.trim() : 'Test';
    
    // Add to activity timeline (but don't count as "test generated")
    // This is just raw code generation, not a saved test case from recorder/builder
    if (typeof window.addActivityLog === 'function') {
        window.addActivityLog(
            prompt.substring(0, 50) + (prompt.length > 50 ? '...' : ''),
            'code_generated',
            timeMs,
            `Code generated in ${language}`
        );
    }
    
    if (typeof window.updateDashboardStats === 'function') {
        window.updateDashboardStats();
    }
    
    // NEW: Show alternatives modal if alternatives exist
    if (alternatives && alternatives.length > 0) {
        setTimeout(() => showAlternativesModal(text, alternatives, prompt), 500);
    }
}

function displayError(message) {
    const resultContent = document.getElementById('resultContent');
    if (resultContent) {
        resultContent.textContent = `Error: ${message}`;
    }
    
    // Safely hide buttons (elements might not be loaded yet)
    const copyBtn = document.getElementById('copyBtn');
    const validateBtn = document.getElementById('validateBtn');
    const saveSnippetBtn = document.getElementById('saveSnippetBtn');
    const exportBtn = document.getElementById('exportBtn');
    const validationResults = document.getElementById('validationResults');
    
    if (copyBtn) copyBtn.style.display = 'none';
    if (validateBtn) validateBtn.style.display = 'none';
    if (saveSnippetBtn) saveSnippetBtn.style.display = 'none';
    if (exportBtn) exportBtn.style.display = 'none';
    if (validationResults) validationResults.style.display = 'none';
}

function copyResult() {
    const resultContent = document.getElementById('resultContent');
    if (!resultContent) {
        console.error('Result content element not found');
        return;
    }
    
    const text = resultContent.textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => {
                btn.textContent = originalText;
            }, 2000);
        }
    });
}

function exportCode() {
    const resultContent = document.getElementById('resultContent');
    if (!resultContent) {
        console.error('Result content element not found');
        return;
    }
    
    const code = resultContent.textContent;
    
    let extension = '.java';
    let filename = 'GeneratedTest';
    
    if (code.includes('from selenium') || code.includes('import pytest')) {
        extension = '.py';
        filename = 'test_generated';
    } else if (code.includes('const ') || code.includes('let ')) {
        extension = '.js';
        filename = 'generated_test';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        extension = '.cs';
        filename = 'GeneratedTest';
    }

    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    modal.innerHTML = `
        <div class="modal">
            <div class="modal-header">
                <h3 class="modal-title">💾 Export Code to File</h3>
                <button class="modal-close" onclick="this.closest('.modal-overlay').remove()">&times;</button>
            </div>
            <div class="modal-body">
                <div class="form-group">
                    <label for="exportFilename">Filename:</label>
                    <input type="text" id="exportFilename" value="${filename}" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                </div>
                <div class="form-group" style="margin-top: 15px;">
                    <label for="exportExtension">File Type:</label>
                    <select id="exportExtension" style="width: 100%; padding: 10px; border: 2px solid var(--border-color); border-radius: 6px; background: var(--input-bg); color: var(--text-primary);">
                        <option value=".java" ${extension === '.java' ? 'selected' : ''}>Java (.java)</option>
                        <option value=".py" ${extension === '.py' ? 'selected' : ''}>Python (.py)</option>
                        <option value=".js" ${extension === '.js' ? 'selected' : ''}>JavaScript (.js)</option>
                        <option value=".cs" ${extension === '.cs' ? 'selected' : ''}>C# (.cs)</option>
                        <option value=".txt" ${extension === '.txt' ? 'selected' : ''}>Text (.txt)</option>
                    </select>
                </div>
            </div>
            <div class="modal-footer">
                <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="background: var(--color-gray-500);">
                    Cancel
                </button>
                <button class="btn" onclick="downloadCodeFile()" style="background: var(--color-primary-600);">
                    💾 Download
                </button>
            </div>
        </div>
    `;
    document.body.appendChild(modal);
}

function downloadCodeFile() {
    const filenameInput = document.getElementById('exportFilename');
    const extensionSelect = document.getElementById('exportExtension');
    const resultContent = document.getElementById('resultContent');
    
    if (!filenameInput || !extensionSelect || !resultContent) {
        console.error('Required elements not found');
        return;
    }
    
    const filename = filenameInput.value.trim();
    const extension = extensionSelect.value;
    const code = resultContent.textContent;
    
    if (!filename) {
        alert('Please enter a filename');
        return;
    }

    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = filename + extension;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);

    document.querySelector('.modal-overlay').remove();
    showNotification(`✅ File exported: ${filename}${extension}`);
}

function saveToSnippets() {
    const resultContent = document.getElementById('resultContent');
    if (!resultContent) {
        console.error('Result content element not found');
        return;
    }
    
    const code = resultContent.textContent;
    if (!code || code === 'Your generated code will appear here...') {
        alert('No code to save');
        return;
    }

    showAddSnippetModal(code);
}

function setPrompt(text) {
    const promptInput = document.getElementById('promptInput');
    if (promptInput) {
        promptInput.value = text;
    }
}

function validateCode() {
    const code = document.getElementById('resultContent')?.textContent;
    if (!code || code === 'Your generated code will appear here...') {
        alert('No code to validate');
        return;
    }
    
    showNotification('⏳ Validating code...');
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    }
    
    // Basic validation
    const issues = [];
    if (code.length < 10) {
        issues.push('Code is too short');
    }
    
    if (language === 'java' && !code.includes('class ')) {
        issues.push('Missing class definition');
    }
    
    if (issues.length > 0) {
        showNotification('⚠️ Validation found ' + issues.length + ' issue(s): ' + issues.join(', '));
    } else {
        showNotification('✅ Code validation passed!');
    }
}

async function executeCurrentTest() {
    const code = document.getElementById('resultContent')?.textContent;
    if (!code || code === 'Your generated code will appear here...') {
        alert('No code to execute. Generate code first.');
        return;
    }
    
    showNotification('⏳ Executing test...');
    
    try {
        // This would connect to a test execution service
        await new Promise(resolve => setTimeout(resolve, 1000));
        showNotification('✅ Test execution feature coming soon!');
    } catch (error) {
        showNotification('❌ Execution failed: ' + error.message);
    }
}

// Expose functions to window object for inline onclick handlers
window.generateCode = generateCode;
window.displayResult = displayResult;
window.displayError = displayError;
window.copyResult = copyResult;
window.exportCode = exportCode;
window.downloadCodeFile = downloadCodeFile;
window.saveToSnippets = saveToSnippets;
window.setPrompt = setPrompt;
window.validateCode = validateCode;
window.executeCurrentTest = executeCurrentTest;

// Initialize: Check for pending generated test data from semantic analysis
function checkPendingGeneratedTest() {
    const pendingData = sessionStorage.getItem('pendingGeneratedTest');
    if (pendingData) {
        try {
            const data = JSON.parse(pendingData);
            const promptInput = document.getElementById('promptInput');
            
            if (promptInput) {
                promptInput.value = data.prompt || '';
                displayResult(data.code || '', 0, 0);
                sessionStorage.removeItem('pendingGeneratedTest');
                console.log('[CODE-GEN] Loaded pending test data from semantic analysis');
            }
        } catch (err) {
            console.error('[CODE-GEN] Error loading pending test data:', err);
            sessionStorage.removeItem('pendingGeneratedTest');
        }
    }
}

// Check for pending data when page becomes active
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', checkPendingGeneratedTest);
} else {
    checkPendingGeneratedTest();
}

// Also check when navigating back to this page
window.addEventListener('pageshow', checkPendingGeneratedTest);

// ============================================================================
// ALTERNATIVES UI (HYBRID Mode - "Did you mean?")
// ============================================================================

function showAlternativesModal(currentCode, alternatives, originalPrompt) {
    console.log('[ALTERNATIVES] Showing modal with', alternatives.length, 'alternatives');
    
    // Create modal if it doesn't exist
    let modal = document.getElementById('alternativesModal');
    if (!modal) {
        createAlternativesModal();
        modal = document.getElementById('alternativesModal');
    }
    
    // Update modal content
    document.getElementById('alternativesOriginalPrompt').textContent = originalPrompt;
    const currentCodeEl = document.getElementById('alternativesCurrentCode');
    currentCodeEl.textContent = currentCode;
    
    // Highlight current code with Prism if available
    if (window.Prism) {
        currentCodeEl.className = 'language-java';
        Prism.highlightElement(currentCodeEl);
    }
    
    // Populate alternatives list
    const alternativesList = document.getElementById('alternativesList');
    alternativesList.innerHTML = alternatives.map((alt, index) => {
        const score = ((alt.score || 0) * 100).toFixed(1);
        const promptVariations = alt.prompt_variations || [];
        const hasVariations = promptVariations.length > 0;
        
        // Build variations section if available
        let variationsHTML = '';
        if (hasVariations) {
            const showCount = 5; // Initially show first 5
            const displayVariations = promptVariations.slice(0, showCount);
            const remainingVariations = promptVariations.slice(showCount);
            const remainingCount = remainingVariations.length;
            
            variationsHTML = `
                <div class="alternative-variations" style="margin-top: var(--space-2); padding: var(--space-3); background: var(--bg-tertiary); border-radius: var(--radius-sm); font-size: var(--text-sm);">
                    <strong style="color: var(--text-secondary);">📝 Also works with (${promptVariations.length} total):</strong>
                    <ul id="variations-list-${index}" style="margin: var(--space-2) 0 0 var(--space-4); color: var(--text-secondary); list-style: disc;">
                        ${displayVariations.map(v => `<li>${escapeHtml(v)}</li>`).join('')}
                    </ul>
                    ${remainingCount > 0 ? `
                        <ul id="variations-hidden-${index}" style="display: none; margin: var(--space-2) 0 0 var(--space-4); color: var(--text-secondary); list-style: disc;">
                            ${remainingVariations.map(v => `<li>${escapeHtml(v)}</li>`).join('')}
                        </ul>
                        <div style="margin-top: var(--space-2);">
                            <a href="#" onclick="toggleVariations(${index}); return false;" 
                               id="variations-toggle-${index}"
                               data-remaining-count="${remainingCount}"
                               style="color: var(--color-primary); text-decoration: underline; cursor: pointer; font-weight: 500;">
                                ▼ Show ${remainingCount} more variations
                            </a>
                        </div>
                    ` : ''}
                </div>
            `;
        }
        
        return `
            <div class="alternative-item">
                <div class="alternative-header">
                    <span class="alternative-score">${score}%</span>
                    <span class="alternative-prompt">${escapeHtml(alt.prompt || '')}</span>
                    ${alt.xpath ? `<span class="alternative-selector" style="margin-left: var(--space-2); font-size: var(--text-sm); color: var(--text-tertiary); font-family: monospace;">Selector: ${escapeHtml(alt.xpath)}</span>` : ''}
                </div>
                ${variationsHTML}
                <pre class="alternative-code"><code class="language-java">${escapeHtml(alt.code || '')}</code></pre>
                <button class="btn-use-alternative" onclick="useAlternative(${index})">
                    Use this selector approach
                </button>
            </div>
        `;
    }).join('');
    
    // Highlight alternative codes with Prism if available
    if (window.Prism) {
        alternativesList.querySelectorAll('code').forEach(block => {
            Prism.highlightElement(block);
        });
    }
    
    // Show modal
    modal.style.display = 'flex';
}

function createAlternativesModal() {
    const modalHTML = `
        <div id="alternativesModal" class="modal-overlay" style="display: none;">
            <div class="modal modal-lg">
                <div class="modal-header">
                    <h3 class="modal-title">💡 Did you mean?</h3>
                    <button class="modal-close" onclick="closeAlternativesModal()">&times;</button>
                </div>
                <div class="modal-body">
                    <div style="margin-bottom: var(--space-6);">
                        <p style="color: var(--text-secondary); margin-bottom: var(--space-3);"><strong>Your prompt:</strong> <span id="alternativesOriginalPrompt"></span></p>
                        <p style="color: var(--text-secondary); margin-bottom: var(--space-2);"><strong>Generated code (used automatically):</strong></p>
                        <div style="background: var(--bg-secondary); border-radius: var(--radius-md); padding: var(--space-4); max-height: 200px; overflow-y: auto;">
                            <pre style="margin: 0;"><code id="alternativesCurrentCode" class="language-java"></code></pre>
                        </div>
                    </div>
                    <div>
                        <h4 style="color: var(--text-primary); margin-bottom: var(--space-4); font-size: var(--text-lg);">Similar matches found:</h4>
                        <div id="alternativesList"></div>
                    </div>
                </div>
                <div class="modal-footer">
                    <button class="btn" onclick="closeAlternativesModal()" style="background: var(--color-gray-500);">
                        Keep current code
                    </button>
                </div>
            </div>
        </div>
    `;
    document.body.insertAdjacentHTML('beforeend', modalHTML);
}

function useAlternative(alternativeIndex) {
    if (!currentAlternatives || alternativeIndex >= currentAlternatives.length) {
        console.error('[ALTERNATIVES] Invalid alternative index:', alternativeIndex);
        return;
    }
    
    const alternative = currentAlternatives[alternativeIndex];
    console.log('[ALTERNATIVES] Using alternative:', alternative.prompt);
    
    // Update the output with alternative code
    const outputDiv = document.getElementById('resultContent');
    if (outputDiv) {
        outputDiv.textContent = alternative.code || '';
        
        // Re-highlight with Prism if available
        if (window.Prism) {
            outputDiv.className = 'language-java';
            Prism.highlightElement(outputDiv);
        }
    }
    
    // Close modal
    closeAlternativesModal();
    
    // Show notification
    if (typeof showNotification === 'function') {
        showNotification('✅ Code updated with alternative');
    }
}

function toggleVariations(index) {
    const hiddenList = document.getElementById(`variations-hidden-${index}`);
    const toggleLink = document.getElementById(`variations-toggle-${index}`);
    
    if (!hiddenList || !toggleLink) return;
    
    const remainingCount = toggleLink.getAttribute('data-remaining-count') || '0';
    
    if (hiddenList.style.display === 'none') {
        // Show all variations
        hiddenList.style.display = 'block';
        toggleLink.innerHTML = '▲ Show less';
    } else {
        // Hide extra variations
        hiddenList.style.display = 'none';
        toggleLink.innerHTML = `▼ Show ${remainingCount} more variations`;
    }
}

function closeAlternativesModal() {
    const modal = document.getElementById('alternativesModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

// ============== LANGUAGE DISPLAY HELPER ==============

// Initialize language selector change listener
if (typeof window !== 'undefined') {
    window.addEventListener('DOMContentLoaded', function() {
        const languageSelector = document.getElementById('languageSelector');
        const resultContent = document.getElementById('resultContent');
        const promptInput = document.getElementById('promptInput');
        
        if (languageSelector) {
            // Auto-regenerate when language changes (if code was already generated)
            languageSelector.addEventListener('change', async function() {
                // Only regenerate if:
                // 1. There's a prompt
                // 2. Code was already generated (not showing default message)
                if (promptInput && promptInput.value.trim() && 
                    resultContent && !resultContent.textContent.includes('Your generated code will appear here')) {
                    
                    console.log(`[LANGUAGE CHANGE] Auto-regenerating code in ${this.value}`);
                    await generateCode();
                }
            });
        }
    });
}

// Export alternatives functions
window.showAlternativesModal = showAlternativesModal;
window.useAlternative = useAlternative;
window.closeAlternativesModal = closeAlternativesModal;
window.toggleVariations = toggleVariations;