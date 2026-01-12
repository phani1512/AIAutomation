// Semantic Analysis Functions

let currentSemanticSession = null;
let semanticSessions = [];

async function refreshSemanticSessions() {
    try {
        const response = await fetch(`${window.API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (data.sessions) {
            semanticSessions = data.sessions;
            updateSemanticSessionsList();
        }
    } catch (error) {
        console.error('Error loading semantic sessions:', error);
    }
}

function updateSemanticSessionsList() {
    const select = document.getElementById('semanticSessionSelect');
    
    if (semanticSessions.length === 0) {
        select.innerHTML = '<option value="">No sessions available</option>';
        return;
    }
    
    select.innerHTML = '<option value="">Select a session...</option>' +
        semanticSessions.map(session => {
            const date = new Date(session.timestamp).toLocaleString();
            const count = session.actions ? session.actions.length : 0;
            return `<option value="${session.id}">${session.name || session.id} (${count} actions) - ${date}</option>`;
        }).join('');
}

async function loadSemanticAnalysis() {
    const sessionId = document.getElementById('semanticSessionSelect').value;
    
    if (!sessionId) {
        alert('Please select a session');
        return;
    }
    
    currentSemanticSession = sessionId;
    
    window.showLoading(true);
    
    try {
        const response = await fetch(`${window.API_URL}/semantic/analyze-intent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (data.intent) {
            displaySemanticIntent(data.intent);
        } else {
            throw new Error(data.error || 'Failed to analyze intent');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

function displaySemanticIntent(intent) {
    const container = document.getElementById('semanticIntentDisplay');
    
    container.innerHTML = `
        <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px;">
            <h4 style="color: var(--text-primary); margin-bottom: 15px;">🎯 Detected Intent</h4>
            
            <div style="margin-bottom: 15px;">
                <strong style="color: var(--text-primary);">Primary Intent:</strong>
                <span style="color: var(--accent); margin-left: 10px; font-size: 1.1em;">${intent.primary}</span>
            </div>
            
            ${intent.secondary && intent.secondary.length > 0 ? `
                <div style="margin-bottom: 15px;">
                    <strong style="color: var(--text-primary);">Secondary Intents:</strong>
                    <div style="display: flex; flex-wrap: wrap; gap: 8px; margin-top: 8px;">
                        ${intent.secondary.map(sec => `
                            <span style="background: var(--bg-tertiary); padding: 5px 12px; border-radius: 15px; font-size: 0.9em; color: var(--text-secondary);">
                                ${sec}
                            </span>
                        `).join('')}
                    </div>
                </div>
            ` : ''}
            
            <div style="margin-bottom: 15px;">
                <strong style="color: var(--text-primary);">Confidence:</strong>
                <div style="background: var(--bg-tertiary); height: 20px; border-radius: 10px; margin-top: 8px; overflow: hidden;">
                    <div style="background: ${intent.confidence > 0.7 ? 'var(--success)' : intent.confidence > 0.4 ? 'var(--warning)' : 'var(--error)'}; width: ${intent.confidence * 100}%; height: 100%; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.8em; font-weight: bold;">
                        ${Math.round(intent.confidence * 100)}%
                    </div>
                </div>
            </div>
            
            ${intent.description ? `
                <div>
                    <strong style="color: var(--text-primary);">Description:</strong>
                    <p style="color: var(--text-secondary); margin: 8px 0 0 0;">${intent.description}</p>
                </div>
            ` : ''}
        </div>
    `;
}

async function generateSuggestions() {
    if (!currentSemanticSession) {
        alert('Please analyze intent first');
        return;
    }
    
    window.showLoading(true);
    
    try {
        const response = await fetch(`${window.API_URL}/semantic/suggest-scenarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSemanticSession })
        });
        
        const data = await response.json();
        
        if (data.suggestions) {
            displaySuggestions(data.suggestions);
        } else {
            throw new Error(data.error || 'Failed to generate suggestions');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('semanticSuggestionsDisplay');
    
    if (!suggestions || suggestions.length === 0) {
        container.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No suggestions available</div>';
        return;
    }
    
    // Group by priority
    const grouped = {
        high: suggestions.filter(s => s.priority === 'high'),
        medium: suggestions.filter(s => s.priority === 'medium'),
        low: suggestions.filter(s => s.priority === 'low')
    };
    
    let html = '<div style="display: flex; flex-direction: column; gap: 20px;">';
    
    // High priority
    if (grouped.high.length > 0) {
        html += `
            <div>
                <h4 style="color: var(--error); margin-bottom: 15px;">🔴 High Priority (${grouped.high.length})</h4>
                ${grouped.high.map(s => renderSuggestion(s)).join('')}
            </div>
        `;
    }
    
    // Medium priority
    if (grouped.medium.length > 0) {
        html += `
            <div>
                <h4 style="color: var(--warning); margin-bottom: 15px;">🟡 Medium Priority (${grouped.medium.length})</h4>
                ${grouped.medium.map(s => renderSuggestion(s)).join('')}
            </div>
        `;
    }
    
    // Low priority
    if (grouped.low.length > 0) {
        html += `
            <div>
                <h4 style="color: var(--info); margin-bottom: 15px;">🔵 Low Priority (${grouped.low.length})</h4>
                ${grouped.low.map(s => renderSuggestion(s)).join('')}
            </div>
        `;
    }
    
    html += '</div>';
    container.innerHTML = html;
}

function renderSuggestion(suggestion) {
    const typeIcons = {
        negative: '❌',
        boundary: '📊',
        edge_case: '⚠️',
        variation: '🔄',
        compatibility: '🔌'
    };
    
    const icon = typeIcons[suggestion.type] || '💡';
    
    return `
        <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid ${suggestion.priority === 'high' ? 'var(--error)' : suggestion.priority === 'medium' ? 'var(--warning)' : 'var(--info)'};">
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 10px;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.3em;">${icon}</span>
                        <strong style="color: var(--text-primary); font-size: 1.05em;">${suggestion.title}</strong>
                        <span style="background: var(--bg-tertiary); padding: 3px 10px; border-radius: 12px; font-size: 0.85em; color: var(--text-secondary);">
                            ${suggestion.type.replace('_', ' ')}
                        </span>
                    </div>
                    <p style="color: var(--text-secondary); margin: 0; line-height: 1.5;">${suggestion.description}</p>
                </div>
                <button onclick="generateTestFromSuggestion('${escapeHtml(JSON.stringify(suggestion))}')" style="background: var(--accent); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; white-space: nowrap; margin-left: 15px;">
                    Generate Test
                </button>
            </div>
            
            ${suggestion.steps && suggestion.steps.length > 0 ? `
                <div style="margin-top: 12px; padding-top: 12px; border-top: 1px solid var(--border);">
                    <strong style="color: var(--text-primary); font-size: 0.9em;">Steps:</strong>
                    <ol style="margin: 8px 0 0 0; padding-left: 20px; color: var(--text-secondary); font-size: 0.9em;">
                        ${suggestion.steps.map(step => `<li style="margin: 4px 0;">${step}</li>`).join('')}
                    </ol>
                </div>
            ` : ''}
            
            ${suggestion.expected_result ? `
                <div style="margin-top: 10px; padding: 8px 12px; background: var(--bg-tertiary); border-radius: 6px;">
                    <strong style="color: var(--text-primary); font-size: 0.9em;">Expected:</strong>
                    <span style="color: var(--text-secondary); margin-left: 8px; font-size: 0.9em;">${suggestion.expected_result}</span>
                </div>
            ` : ''}
        </div>
    `;
}

function escapeHtml(text) {
    return text.replace(/"/g, '&quot;').replace(/'/g, '&#39;');
}

async function generateTestFromSuggestion(suggestionJson) {
    const suggestion = JSON.parse(suggestionJson.replace(/&quot;/g, '"').replace(/&#39;/g, "'"));
    
    window.showLoading(true);
    
    try {
        const response = await fetch(`${window.API_URL}/generate-from-suggestion`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                suggestion: suggestion,
                language: document.getElementById('languageSelector').value
            })
        });
        
        const data = await response.json();
        
        if (data.code) {
            window.navigateTo('generator');
            window.displayResult(data.code, 0, 0);
            window.showNotification('✅ Test code generated from suggestion!');
        } else {
            throw new Error(data.error || 'Failed to generate code');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

function generateAllSuggestions() {
    const suggestionsDiv = document.getElementById('semanticSuggestions');
    if (!suggestionsDiv) return;
    
    const allSuggestions = suggestionsDiv.querySelectorAll('.suggestion-item');
    if (allSuggestions.length === 0) {
        alert('No suggestions available');
        return;
    }
    
    window.showNotification(`✅ Generating ${allSuggestions.length} suggestions...`);
    // Implementation would generate code for all suggestions
}

function generateSelectedSuggestions() {
    const checkboxes = document.querySelectorAll('.suggestion-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('No suggestions selected');
        return;
    }
    
    window.showNotification(`✅ Generating ${checkboxes.length} selected suggestion(s)...`);
    // Implementation would generate code for selected suggestions
}

// Expose functions to global scope for HTML onclick handlers
window.refreshSemanticSessions = refreshSemanticSessions;
window.loadSemanticAnalysis = loadSemanticAnalysis;
window.generateSuggestions = generateSuggestions;
window.generateAllSuggestions = generateAllSuggestions;
window.generateSelectedSuggestions = generateSelectedSuggestions;
window.displaySuggestions = displaySuggestions;
window.generateTestFromSuggestion = generateTestFromSuggestion;


