// Code Generation Features

async function generateCode() {
    const prompt = document.getElementById('promptInput').value.trim();
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
    
    document.getElementById('copyBtn').style.display = 'block';
    document.getElementById('validateBtn').style.display = 'block';
    document.getElementById('saveSnippetBtn').style.display = 'block';
    document.getElementById('exportBtn').style.display = 'block';
    document.getElementById('validationResults').style.display = 'none';
    
    // Update stats
    stats.totalRequests++;
    stats.totalTokens += tokens;
    stats.totalTime += timeMs;
    
    const prompt = document.getElementById('promptInput').value.trim();
    addTestResult(
        prompt.substring(0, 50) + (prompt.length > 50 ? '...' : ''),
        'pending',
        timeMs,
        `Code generated in ${language}`
    );
    
    updateDashboardStats();
}

function displayError(message) {
    document.getElementById('resultContent').textContent = `Error: ${message}`;
    document.getElementById('copyBtn').style.display = 'none';
    document.getElementById('validateBtn').style.display = 'none';
    document.getElementById('saveSnippetBtn').style.display = 'none';
    document.getElementById('exportBtn').style.display = 'none';
    document.getElementById('validationResults').style.display = 'none';
}

function copyResult() {
    const text = document.getElementById('resultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyBtn');
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

function exportCode() {
    const code = document.getElementById('resultContent').textContent;
    
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
    const filename = document.getElementById('exportFilename').value.trim();
    const extension = document.getElementById('exportExtension').value;
    const code = document.getElementById('resultContent').textContent;
    
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
    const code = document.getElementById('resultContent').textContent;
    if (!code || code === 'Your generated code will appear here...') {
        alert('No code to save');
        return;
    }

    showAddSnippetModal(code);
}

// Expose functions to window object for inline onclick handlers
window.generateCode = generateCode;
window.copyResult = copyResult;
window.exportCode = exportCode;
window.saveToSnippets = saveToSnippets;