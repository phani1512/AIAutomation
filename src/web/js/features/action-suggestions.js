// Action Suggestion Features

async function suggestAction() {
    const elementType = document.getElementById('elementType').value;
    const context = document.getElementById('contextInput').value.trim();

    showLoading(true);
    const startTime = Date.now();

    try {
        const response = await fetch(`${API_URL}/suggest-action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                element_type: elementType,
                context: context || ''
            })
        });

        const data = await response.json();
        const endTime = Date.now();
        
        let result = `Element Type: ${data.element_type}\n`;
        if (data.context) {
            result += `Context: ${data.context}\n`;
        }
        result += `\nRecommended Actions:\n`;
        
        if (data.recommended_actions && data.recommended_actions.length > 0) {
            data.recommended_actions.forEach((action, idx) => {
                result += `${idx + 1}. ${action}\n`;
            });
        }
        
        if (data.ai_generated_code) {
            result += `\nAI Generated Code:\n${data.ai_generated_code}`;
        }
        
        displayActionResult(result, endTime - startTime);
    } catch (error) {
        displayActionError('Failed to suggest action: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayActionResult(text, timeMs) {
    const codeElement = document.getElementById('actionResultContent');
    codeElement.textContent = text;
    
    // Detect language
    let language = 'java';
    if (text.includes('from selenium') || text.includes('import pytest')) {
        language = 'python';
    } else if (text.includes('const ') || text.includes('let ')) {
        language = 'javascript';
    } else if (text.includes('using ') || text.includes('namespace ')) {
        language = 'csharp';
    }
    
    codeElement.className = `language-${language}`;
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    document.getElementById('copyActionBtn').style.display = 'block';
    document.getElementById('saveActionSnippetBtn').style.display = 'block';
}

function displayActionError(message) {
    document.getElementById('actionResultContent').textContent = `Error: ${message}`;
    document.getElementById('copyActionBtn').style.display = 'none';
    document.getElementById('saveActionSnippetBtn').style.display = 'none';
}

function copyActionResult() {
    const text = document.getElementById('actionResultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyActionBtn');
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

function saveActionToSnippets() {
    const code = document.getElementById('actionResultContent').textContent;
    const elementType = document.getElementById('elementType').value;
    const context = document.getElementById('contextInput').value.trim();
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const snippet = {
        id: Date.now(),
        title: `Action Suggestions - ${elementType}`,
        language: language,
        tags: ['action', 'selenium', elementType],
        description: context ? `Actions for ${elementType} in ${context}` : `Actions for ${elementType}`,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));

    showNotification('✅ Saved to Code Snippets!');
}

// Expose functions to window object
window.suggestAction = suggestAction;
window.copyActionResult = copyActionResult;
window.saveActionToSnippets = saveActionToSnippets;