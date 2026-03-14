// Enhanced Action Suggestion Features with Confidence Scoring

// Loading indicator function specific to action suggestions page
function showActionLoading(show) {
    const resultBox = document.getElementById('actionResultBox');
    const codeElement = document.getElementById('actionResultContent');
    
    // Only update action-specific elements if they exist (we're on the action page)
    if (codeElement) {
        if (show) {
            codeElement.textContent = '⏳ Generating enhanced action suggestions...\nPlease wait...';
            if (resultBox) resultBox.style.opacity = '0.6';
        } else {
            if (resultBox) resultBox.style.opacity = '1';
        }
    }
}

async function suggestAction() {
    const elementType = document.getElementById('elementType').value;
    const context = document.getElementById('contextInput').value.trim();
    const language = document.getElementById('languageSelect')?.value || 'java';

    console.log('[Action Suggestions] Request:', { elementType, context, language });

    showActionLoading(true);
    const startTime = Date.now();

    try {
        const response = await fetch(`${API_URL}/suggest-action`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                element_type: elementType,
                context: context || '',
                language: language
            })
        });

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('[Action Suggestions] Response:', data);
        
        const endTime = Date.now();
        
        displayEnhancedActionResult(data, endTime - startTime);
    } catch (error) {
        console.error('[Action Suggestions] Error:', error);
        displayActionError('Failed to suggest action: ' + error.message);
    } finally {
        showActionLoading(false);
    }
}

function displayEnhancedActionResult(data, timeMs) {
    const codeElement = document.getElementById('actionResultContent');
    
    console.log('[Display] Rendering enhanced result:', {
        hasConfidence: !!data.confidence,
        hasTestScenarios: !!data.test_scenarios,
        hasCodeSamples: !!data.code_samples,
        language: document.getElementById('languageSelect')?.value
    });
    
    // Check if we received enhanced data
    if (!data.confidence && !data.test_scenarios) {
        console.warn('[Display] ⚠️ Received legacy format, not enhanced format');
    }
    
    // Build enhanced result with confidence and test scenarios
    let result = '';
    
    // Header with confidence
    result += `╔════════════════════════════════════════════════════════════╗\n`;
    result += `║        ENHANCED ACTION SUGGESTIONS (v2.0.4)               ║\n`;
    result += `╚════════════════════════════════════════════════════════════╝\n\n`;
    
    result += `Element Type: ${data.element_type || 'Unknown'}\n`;
    if (data.context) {
        result += `Context: ${data.context}\n`;
    }
    
    // Confidence analysis
    if (data.confidence !== undefined) {
        result += `\n┌─ Confidence Analysis ─────────────────────────────────────┐\n`;
        result += `│ Confidence Score: ${data.confidence}%\n`;
        result += `│ Confidence Level: ${data.confidence_level || 'N/A'}\n`;
        result += `│ Total Actions Available: ${data.total_actions || 0}\n`;
        result += `└───────────────────────────────────────────────────────────┘\n\n`;
    }
    
    // Top priority actions
    if (data.top_actions && data.top_actions.length > 0) {
        result += `┌─ Top Priority Actions ────────────────────────────────────┐\n`;
        data.top_actions.forEach((action, idx) => {
            result += `│ ${idx + 1}. ${action}\n`;
        });
        result += `└───────────────────────────────────────────────────────────┘\n\n`;
    }
    
    // All recommended actions with details
    if (data.recommended_actions && data.recommended_actions.length > 0) {
        const displayCount = Math.min(data.recommended_actions.length, 15);  // Show more actions
        result += `┌─ Recommended Actions (showing ${displayCount} of ${data.recommended_actions.length}) ─────────┐\n`;
        data.recommended_actions.slice(0, displayCount).forEach((action, idx) => {
            if (typeof action === 'object') {
                const priority = action.priority === 1 ? '⭐' : action.priority === 2 ? '★' : '☆';
                result += `│ ${priority} ${action.name}()\n`;
                result += `│   Code: ${action.code}\n`;
                result += `│   Description: ${action.description}\n`;
            } else {
                // Legacy format
                result += `│ • ${action}\n`;
            }
            if (idx < displayCount - 1) {
                result += `│   ───────────────────────────────────────────────────────\n`;
            }
        });
        if (data.recommended_actions.length > displayCount) {
            result += `│   ... and ${data.recommended_actions.length - displayCount} more actions\n`;
        }
        result += `└───────────────────────────────────────────────────────────┘\n\n`;
    }
    
    // Context hints
    if (data.context_hints && data.context_hints.length > 0) {
        result += `┌─ Context Hints ───────────────────────────────────────────┐\n`;
        result += `│ Common use cases: ${data.context_hints.slice(0, 10).join(', ')}\n`;
        result += `└───────────────────────────────────────────────────────────┘\n\n`;
    }
    
    // Test Scenarios
    if (data.test_scenarios && data.test_scenarios.length > 0) {
        result += `┌─ Test Scenarios ──────────────────────────────────────────┐\n`;
        data.test_scenarios.forEach((scenario, idx) => {
            result += `│\n│ ${scenario.category}:\n`;
            scenario.cases.slice(0, 4).forEach(testCase => {
                result += `│   • ${testCase}\n`;
            });
            if (idx < data.test_scenarios.length - 1) {
                result += `│\n`;
            }
        });
        result += `└───────────────────────────────────────────────────────────┘\n\n`;
    }
    
    // Code samples - FIXED: Use correct language
    if (data.code_samples) {
        const languageSelect = document.getElementById('languageSelect')?.value || 'java';
        console.log('[Display] Language selected:', languageSelect);
        console.log('[Display] Available code samples:', Object.keys(data.code_samples));
        
        const selectedCode = data.code_samples[languageSelect] || data.code_samples.java || data.ai_generated_code || 'No code sample available';
        
        result += `┌─ Generated Code (${languageSelect.toUpperCase()}) ───────────────────────────────────┐\n`;
        result += `\n${selectedCode}\n`;
        result += `└───────────────────────────────────────────────────────────┘\n`;
        
        console.log('[Display] Using code for language:', languageSelect);
    } else if (data.ai_generated_code) {
        result += `┌─ Generated Code ──────────────────────────────────────────┐\n`;
        result += `\n${data.ai_generated_code}\n`;
        result += `└───────────────────────────────────────────────────────────┘\n`;
    }
    
    // Add performance info
    result += `\n⏱️ Response time: ${timeMs}ms\n`;
    
    codeElement.textContent = result;
    
    // Detect language for syntax highlighting
    const languageSelect = document.getElementById('languageSelect')?.value || 'java';
    let highlightLang = languageSelect;
    
    codeElement.className = `language-${highlightLang}`;
    
    if (typeof Prism !== 'undefined') {
        try {
            Prism.highlightElement(codeElement);
        } catch (e) {
            console.warn('[Display] Prism highlighting failed:', e);
        }
    }
    
    document.getElementById('copyActionBtn').style.display = 'block';
    document.getElementById('saveActionSnippetBtn').style.display = 'block';
    
    // Store full data for later use
    window.lastActionSuggestion = data;
    
    console.log('[Display] ✅ Enhanced result displayed successfully');
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