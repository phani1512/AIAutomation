// Code Generation Features

async function generateCode() {
    const promptInput = document.getElementById('promptInput');
    if (!promptInput) {
        console.error('Prompt input element not found - page may not be loaded yet');
        return;
    }
    
    const prompt = promptInput.value.trim();
    if (!prompt) {
        alert('Please enter a prompt');
        return;
    }

    showLoading(true);
    const startTime = Date.now();

    try {
        const response = await authenticatedFetch(`${API_URL}/generate`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt })
        });

        const data = await response.json();
        const endTime = Date.now();
        
        displayResult(data.generated, endTime - startTime, data.tokens_generated || 0);
    } catch (error) {
        displayError('Failed to generate code: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayResult(text, timeMs, tokens = 0) {
    const codeElement = document.getElementById('resultContent');
    if (!codeElement) {
        console.error('Result content element not found - page may not be loaded yet');
        return;
    }
    
    codeElement.textContent = text;
    
    // Detect language and apply syntax highlighting
    let language = 'java';
    if (text.includes('from selenium') || text.includes('import pytest') || text.includes('def ')) {
        language = 'python';
    } else if (text.includes('const ') || text.includes('let ') || text.includes('function ')) {
        language = 'javascript';
    } else if (text.includes('using ') || text.includes('namespace ')) {
        language = 'csharp';
    }
    
    codeElement.className = `language-${language}`;
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    // Safely update button visibility (elements might not be loaded yet)
    const copyBtn = document.getElementById('copyBtn');
    const validateBtn = document.getElementById('validateBtn');
    const saveSnippetBtn = document.getElementById('saveSnippetBtn');
    const exportBtn = document.getElementById('exportBtn');
    const validationResults = document.getElementById('validationResults');
    
    if (copyBtn) copyBtn.style.display = 'block';
    if (validateBtn) validateBtn.style.display = 'block';
    if (saveSnippetBtn) saveSnippetBtn.style.display = 'block';
    if (exportBtn) exportBtn.style.display = 'block';
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
    
    if (typeof window.addTestResult === 'function') {
        window.addTestResult(
            prompt.substring(0, 50) + (prompt.length > 50 ? '...' : ''),
            'pending',
            timeMs,
            `Code generated in ${language}`
        );
    }
    
    if (typeof window.updateDashboardStats === 'function') {
        window.updateDashboardStats();
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
        <div class="modal-content" style="max-width: 500px;">
            <h3 style="margin-bottom: 20px;">💾 Export Code to File</h3>
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
            <div style="display: flex; gap: 10px; margin-top: 20px;">
                <button class="btn btn-primary" onclick="downloadCodeFile()" style="flex: 1;">
                    💾 Download
                </button>
                <button class="btn btn-secondary" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
                    Cancel
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