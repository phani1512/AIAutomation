// Code Generation Functions

function setPrompt(text) {
    const promptInput = document.getElementById('promptInput');
    if (promptInput) {
        promptInput.value = text;
    }
}

async function generateCode() {
    console.log('[DEBUG] generateCode() called');
    
    const promptInput = document.getElementById('promptInput');
    if (!promptInput) {
        alert('Error: Prompt input field not found');
        return;
    }
    
    const prompt = promptInput.value.trim();
    if (!prompt) {
        alert('Please enter a test description');
        return;
    }

    const languageSelector = document.getElementById('languageSelector');
    const language = languageSelector ? languageSelector.value : 'python';
    
    const executeCheckbox = document.getElementById('executeCheckbox');
    const execute = executeCheckbox ? executeCheckbox.checked : false;

    const outputDiv = document.getElementById('resultContent');
    if (!outputDiv) {
        alert('Error: Output area not found');
        return;
    }

    if (!prompt) {
        alert('Please enter a test description');
        return;
    }

    outputDiv.textContent = 'Generating code...';

    const startTime = Date.now();

    try {
        const response = await fetch(window.API_URL + '/generate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ prompt, language, execute })
        });

        if (!response.ok) {
            throw new Error('Server returned error: ' + response.status);
        }

        const data = await response.json();
        const endTime = Date.now();
        const responseTime = endTime - startTime;
        
        outputDiv.textContent = data.code || data.generated || 'No code generated';
        
        // Calculate tokens from generated code
        const generatedCode = data.code || data.generated || '';
        const tokens = data.tokens_generated || generatedCode.split(/\s+/).length;
        
        // Update AI metrics in dashboard
        if (window.updateAIMetrics) {
            window.updateAIMetrics(tokens, responseTime);
        }
        
        console.log(`[METRICS] Tokens: ${tokens}, Response Time: ${responseTime}ms`);
        
        // Show action buttons
        const copyBtn = document.getElementById('copyBtn');
        const validateBtn = document.getElementById('validateBtn');
        const saveSnippetBtn = document.getElementById('saveSnippetBtn');
        const exportBtn = document.getElementById('exportBtn');
        if (copyBtn) copyBtn.style.display = 'block';
        if (validateBtn) validateBtn.style.display = 'block';
        if (saveSnippetBtn) saveSnippetBtn.style.display = 'block';
        if (exportBtn) exportBtn.style.display = 'block';
        
        window.showNotification(`Code generated successfully (${tokens} tokens in ${responseTime}ms)`, 'success');
    } catch (error) {
        console.error('[ERROR]', error);
        outputDiv.textContent = 'Error: ' + error.message;
        window.showNotification('Failed to generate code: ' + error.message, 'error');
    }
}

async function suggestLocator() {
    const htmlInput = document.getElementById('htmlInput');
    if (!htmlInput) {
        alert('Error: HTML input field not found');
        return;
    }
    
    const html = htmlInput.value.trim();
    if (!html) {
        alert('Please enter HTML element');
        return;
    }

    const resultDiv = document.getElementById('locatorResultContent');
    if (!resultDiv) {
        alert('Error: Result area not found');
        return;
    }

    resultDiv.textContent = 'Generating locators...';

    try {
        const response = await fetch(window.API_URL + '/suggest-locator', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ html })
        });

        if (!response.ok) {
            throw new Error('Server returned error: ' + response.status);
        }

        const data = await response.json();
        
        let result = 'Recommended Locators:\n';
        if (data.recommended_locators && data.recommended_locators.length > 0) {
            data.recommended_locators.forEach((loc, idx) => {
                result += `${idx + 1}. ${loc}\n`;
            });
        } else {
            result += 'No locators could be generated\n';
        }
        
        if (data.element_analysis) {
            result += '\nElement Analysis:\n';
            result += `Tag: ${data.element_analysis.tag_name || 'Unknown'}\n`;
            result += `Strategy: ${data.element_analysis.strategy || 'Mixed'}\n`;
        }
        
        resultDiv.textContent = result;
        
        const copyBtn = document.getElementById('copyLocatorBtn');
        const saveBtn = document.getElementById('saveLocatorSnippetBtn');
        if (copyBtn) copyBtn.style.display = 'block';
        if (saveBtn) saveBtn.style.display = 'block';
        
        window.showNotification('Locators generated successfully', 'success');
    } catch (error) {
        console.error('[ERROR]', error);
        resultDiv.textContent = 'Error: ' + error.message;
        window.showNotification('Failed to generate locators: ' + error.message, 'error');
    }
}

async function suggestAction() {
    const elementTypeSelect = document.getElementById('elementType');
    const contextInput = document.getElementById('contextInput');
    
    if (!elementTypeSelect) {
        alert('Error: Element type selector not found');
        return;
    }
    
    const elementType = elementTypeSelect.value;
    const context = contextInput ? contextInput.value.trim() : '';

    const resultDiv = document.getElementById('actionResultContent');
    if (!resultDiv) {
        alert('Error: Result area not found');
        return;
    }

    resultDiv.textContent = 'Generating actions...';

    try {
        const response = await fetch(window.API_URL + '/suggest-action', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ element_type: elementType, context })
        });

        if (!response.ok) {
            throw new Error('Server returned error: ' + response.status);
        }

        const data = await response.json();
        
        let result = `Element Type: ${data.element_type}\n`;
        if (data.context) {
            result += `Context: ${data.context}\n`;
        }
        result += '\nRecommended Actions:\n';
        
        if (data.recommended_actions && data.recommended_actions.length > 0) {
            data.recommended_actions.forEach((action, idx) => {
                result += `${idx + 1}. ${action}\n`;
            });
        } else {
            result += 'No actions could be generated\n';
        }
        
        resultDiv.textContent = result;
        
        const copyBtn = document.getElementById('copyActionBtn');
        const saveBtn = document.getElementById('saveActionSnippetBtn');
        if (copyBtn) copyBtn.style.display = 'block';
        if (saveBtn) saveBtn.style.display = 'block';
        
        window.showNotification('Actions generated successfully', 'success');
    } catch (error) {
        console.error('[ERROR]', error);
        resultDiv.textContent = 'Error: ' + error.message;
        window.showNotification('Failed to generate actions: ' + error.message, 'error');
    }
}

function copyLocatorResult() {
    const text = document.getElementById('locatorResultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyLocatorBtn');
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => btn.textContent = originalText, 2000);
        }
        window.showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        window.showNotification('Failed to copy', 'error');
    });
}

function saveLocatorToSnippets() {
    const code = document.getElementById('locatorResultContent').textContent;
    const htmlInput = document.getElementById('htmlInput');
    const html = htmlInput ? htmlInput.value.trim() : '';
    
    const snippet = {
        id: Date.now(),
        title: 'Locator Suggestions',
        language: 'java',
        tags: ['locator', 'selenium'],
        description: `Locators for: ${html.substring(0, 50)}...`,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    window.showNotification('Saved to Code Snippets', 'success');
    if (window.loadSnippets) window.loadSnippets();
}

function copyActionResult() {
    const text = document.getElementById('actionResultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyActionBtn');
        if (btn) {
            const originalText = btn.textContent;
            btn.textContent = '✅ Copied!';
            setTimeout(() => btn.textContent = originalText, 2000);
        }
        window.showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        window.showNotification('Failed to copy', 'error');
    });
}

function saveActionToSnippets() {
    const code = document.getElementById('actionResultContent').textContent;
    const elementTypeSelect = document.getElementById('elementType');
    const elementType = elementTypeSelect ? elementTypeSelect.value : '';
    
    const snippet = {
        id: Date.now(),
        title: 'Action Suggestions',
        language: 'java',
        tags: ['action', 'selenium'],
        description: `Actions for: ${elementType}`,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    window.showNotification('Saved to Code Snippets', 'success');
    if (window.loadSnippets) window.loadSnippets();
}

function saveGeneratedCode() {
    const code = document.getElementById('resultContent').textContent;
    const promptInput = document.getElementById('promptInput');
    const prompt = promptInput ? promptInput.value.trim() : '';
    const languageSelector = document.getElementById('languageSelector');
    const language = languageSelector ? languageSelector.value : 'python';
    
    const snippet = {
        id: Date.now(),
        title: 'Generated Test',
        language: language,
        tags: ['generated', 'test'],
        description: `Generated from: ${prompt.substring(0, 50)}...`,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    window.showNotification('Saved to Code Snippets', 'success');
    if (window.loadSnippets) window.loadSnippets();
}

function copyGeneratedCode() {
    const text = document.getElementById('resultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        window.showNotification('Copied to clipboard', 'success');
    }).catch(err => {
        window.showNotification('Failed to copy', 'error');
    });
}

// Export all functions to window
window.setPrompt = setPrompt;
window.generateCode = generateCode;
window.suggestLocator = suggestLocator;
window.suggestAction = suggestAction;
window.copyLocatorResult = copyLocatorResult;
window.saveLocatorToSnippets = saveLocatorToSnippets;
window.copyActionResult = copyActionResult;
window.saveActionToSnippets = saveActionToSnippets;
window.saveGeneratedCode = saveGeneratedCode;
window.copyGeneratedCode = copyGeneratedCode;
