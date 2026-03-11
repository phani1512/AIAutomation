// Locator Suggestion Features

async function suggestLocator() {
    const html = document.getElementById('htmlInput').value.trim();
    if (!html) {
        alert('Please enter HTML element');
        return;
    }

    showLoading(true);
    const startTime = Date.now();

    try {
        const response = await fetch(`${API_URL}/suggest-locator`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ html })
        });

        const data = await response.json();
        const endTime = Date.now();
        
        let result = `Recommended Locators:\n`;
        
        if (data.recommended_locators && data.recommended_locators.length > 0) {
            data.recommended_locators.forEach((loc, idx) => {
                result += `${idx + 1}. ${loc}\n`;
            });
        } else {
            result += 'No locators could be generated\n';
        }
        
        if (data.element_analysis) {
            result += `\nElement Analysis:\n`;
            result += `Tag Name: ${data.element_analysis.tag_name || 'Unknown'}\n`;
            result += `Strategy: ${data.element_analysis.strategy || 'Mixed'}\n`;
            result += `Has ID: ${data.element_analysis.has_id ? 'Yes' : 'No'}\n`;
            result += `Has Name: ${data.element_analysis.has_name ? 'Yes' : 'No'}\n`;
            result += `Has Class: ${data.element_analysis.has_class ? 'Yes' : 'No'}\n`;
            result += `Has Type: ${data.element_analysis.has_type ? 'Yes' : 'No'}\n`;
            result += `Has Text: ${data.element_analysis.has_text ? 'Yes' : 'No'}\n`;
            result += `Has Attributes: ${data.element_analysis.has_attributes ? 'Yes' : 'No'}\n`;
        }
        
        displayLocatorResult(result, endTime - startTime);
    } catch (error) {
        displayLocatorError('Failed to suggest locator: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function displayLocatorResult(text, timeMs) {
    const codeElement = document.getElementById('locatorResultContent');
    codeElement.textContent = text;
    codeElement.className = 'language-java';
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    const copyBtn = document.getElementById('copyLocatorBtn');
    const saveBtn = document.getElementById('saveLocatorSnippetBtn');
    if (copyBtn) copyBtn.style.display = 'block';
    if (saveBtn) saveBtn.style.display = 'block';
}

function displayLocatorError(message) {
    document.getElementById('locatorResultContent').textContent = `Error: ${message}`;
    const copyBtn = document.getElementById('copyLocatorBtn');
    const saveBtn = document.getElementById('saveLocatorSnippetBtn');
    if (copyBtn) copyBtn.style.display = 'none';
    if (saveBtn) saveBtn.style.display = 'none';
}

function copyLocatorResult() {
    const text = document.getElementById('locatorResultContent').textContent;
    navigator.clipboard.writeText(text).then(() => {
        const btn = document.getElementById('copyLocatorBtn');
        const originalText = btn.textContent;
        btn.textContent = '✅ Copied!';
        setTimeout(() => {
            btn.textContent = originalText;
        }, 2000);
    });
}

function saveLocatorToSnippets() {
    const code = document.getElementById('locatorResultContent').textContent;
    const html = document.getElementById('htmlInput').value.trim();
    
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

    showNotification('✅ Saved to Code Snippets!');
}

// Expose functions to window object
window.suggestLocator = suggestLocator;
window.copyLocatorResult = copyLocatorResult;
window.saveLocatorToSnippets = saveLocatorToSnippets;