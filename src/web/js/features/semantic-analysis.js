// Semantic Analysis Features

let currentSemanticSession = null;
let semanticSessions = [];

async function refreshSemanticSessions() {
    try {
        const response = await fetch(`${API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (data.sessions) {
            semanticSessions = data.sessions;
            updateSemanticSessionsList();
            showNotification('✅ Sessions refreshed');
        } else {
            showNotification('⚠️ No sessions found');
        }
    } catch (error) {
        console.error('Error fetching sessions:', error);
        showNotification('❌ Failed to fetch sessions');
    }
}

function updateSemanticSessionsList() {
    const select = document.getElementById('semanticSessionSelect');
    
    if (!select) return;
    
    if (semanticSessions.length === 0) {
        select.innerHTML = '<option value="">No sessions available - Record a test first</option>';
    } else {
        select.innerHTML = '<option value="">Select a session...</option>' +
            semanticSessions.map(session => {
                // Try multiple date fields and format properly
                const timestamp = session.created_at || session.timestamp || Date.now();
                const dateObj = new Date(typeof timestamp === 'number' ? timestamp * 1000 : timestamp);
                const date = isNaN(dateObj.getTime()) ? '' : ` - ${dateObj.toLocaleString()}`;
                const count = session.actions ? session.actions.length : 0;
                return `<option value="${session.id}">${session.name || session.id} (${count} actions)${date}</option>`;
            }).join('');
    }
}

function onSemanticSessionChange() {
    const sessionId = document.getElementById('semanticSessionSelect').value;
    
    if (sessionId) {
        currentSemanticSession = sessionId;
        showNotification('✅ Session selected. Click "Get Suggestions" to begin.');
        
        const intentDisplay = document.getElementById('semanticIntentDisplay');
        if (intentDisplay) {
            intentDisplay.style.display = 'none';
        }
        const suggestionsDisplay = document.getElementById('semanticSuggestionsDisplay');
        if (suggestionsDisplay) {
            suggestionsDisplay.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Click "Get Suggestions" to generate AI-powered test scenarios</div>';
        }
    } else {
        currentSemanticSession = null;
    }
}

async function loadSemanticAnalysis() {
    const sessionId = document.getElementById('semanticSessionSelect').value;
    
    if (!sessionId) {
        alert('Please select a test session first');
        return;
    }
    
    currentSemanticSession = sessionId;
    showLoading(true);
    
    try {
        const sessionResponse = await fetch(`${API_URL}/recorder/session/${sessionId}`);
        const sessionData = await sessionResponse.json();
        
        if (!sessionData.success || !sessionData.session) {
            showLoading(false);
            showNotification('❌ Failed to load session data');
            return;
        }
        
        const session = sessionData.session;
        const actions = session.actions || [];
        const prompt = `Analyze the intent of this test: ${session.name || 'Test Session'}. Actions: ${actions.map(a => `${a.action} on ${a.selector || 'element'}`).join(', ')}`;
        
        const response = await fetch(`${API_URL}/semantic/analyze-intent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                prompt: prompt
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (data.success && (data.intent || data.analysis)) {
            const intentData = data.intent || data.analysis;
            displaySemanticIntent(intentData);
            showNotification('✅ Intent analysis complete');
        } else {
            showNotification('⚠️ Unable to analyze intent. Try clicking "Get Suggestions" instead.');
            const intentDisplay = document.getElementById('semanticIntentDisplay');
            if (intentDisplay) {
                intentDisplay.style.display = 'none';
            }
        }
    } catch (error) {
        console.error('Error analyzing intent:', error);
        showLoading(false);
        showNotification('❌ Failed to analyze intent: ' + error.message);
    }
}

function displaySemanticIntent(intent) {
    const container = document.getElementById('semanticIntentDisplay');
    if (!container) return;
    
    container.style.display = 'block';
    
    const confidence = intent.confidence || 0;
    const confidencePercent = Math.round(confidence * 100);
    const confidenceColor = confidence > 0.7 ? '#10b981' : confidence > 0.4 ? '#f59e0b' : '#ef4444';
    
    container.innerHTML = `
        <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; border: 2px solid var(--border-color);">
            <h4 style="margin: 0 0 15px 0; color: var(--text-primary);">🎯 Detected Intent</h4>
            <div style="margin-bottom: 12px;">
                <strong style="color: var(--text-primary);">Primary Intent:</strong> 
                <span style="color: var(--text-secondary);">${intent.primary || intent.type || intent.intent || 'Test Scenario'}</span>
            </div>
            <div style="margin-bottom: 12px;">
                <strong style="color: var(--text-primary);">Confidence:</strong>
                <div style="background: var(--bg-tertiary); height: 20px; border-radius: 10px; margin-top: 5px; overflow: hidden;">
                    <div style="width: ${confidencePercent}%; height: 100%; background: ${confidenceColor}; display: flex; align-items: center; justify-content: center; color: white; font-size: 0.75em; font-weight: 600;">
                        ${confidencePercent}%
                    </div>
                </div>
            </div>
            ${intent.description ? `<div style="margin-top: 15px; padding-top: 15px; border-top: 1px solid var(--border-color);"><p style="color: var(--text-secondary); margin: 0;">${intent.description}</p></div>` : ''}
        </div>
    `;
}

async function generateSuggestions() {
    if (!currentSemanticSession) {
        alert('Please select a session first');
        return;
    }
    
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/semantic/suggest-scenarios`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: currentSemanticSession })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (data.suggestions && data.suggestions.length > 0) {
            displaySuggestions(data.suggestions);
            showNotification(`✅ Generated ${data.suggestions.length} test suggestions`);
        } else {
            showNotification('⚠️ No suggestions generated');
        }
    } catch (error) {
        console.error('Error generating suggestions:', error);
        showLoading(false);
        showNotification('❌ Failed to generate suggestions');
    }
}

function displaySuggestions(suggestions) {
    const container = document.getElementById('semanticSuggestionsDisplay');
    if (!container) return;
    
    window.currentSuggestions = suggestions;
    
    const grouped = {
        high: suggestions.filter(s => s.priority === 'high'),
        medium: suggestions.filter(s => s.priority === 'medium'),
        low: suggestions.filter(s => s.priority === 'low')
    };
    
    let html = '';
    
    if (suggestions.length > 0) {
        html += '<div style="display: flex; gap: 10px; margin-bottom: 20px; padding: 15px; background: var(--bg-secondary); border-radius: 8px; flex-wrap: wrap;">';
        html += `<button class="btn" onclick="generateAllHighPriority()" style="background: #ef4444; padding: 8px 16px; font-size: 0.9em; width: auto;">✅ Generate All High Priority (${grouped.high.length})</button>`;
        html += `<button class="btn" onclick="generateSelectedTests()" id="generateSelectedBtn" style="background: #8b5cf6; padding: 8px 16px; font-size: 0.9em; width: auto; display: none;">🚀 Generate Selected (<span id="selectedCount">0</span>)</button>`;
        html += `<button class="btn" onclick="toggleSelectAll()" style="background: #6b7280; padding: 8px 16px; font-size: 0.9em; width: auto;">☑️ Select All</button>`;
        html += '</div>';
    }
    
    if (grouped.high.length > 0) {
        html += '<div style="margin-bottom: 20px;"><h4 style="color: #ef4444; margin: 0 0 12px 0;">🔴 High Priority Scenarios</h4>';
        html += grouped.high.map((s, idx) => renderSuggestion(s, '#ef4444', idx)).join('');
        html += '</div>';
    }
    
    if (grouped.medium.length > 0) {
        html += '<div style="margin-bottom: 20px;"><h4 style="color: #f59e0b; margin: 0 0 12px 0;">🟡 Medium Priority Scenarios</h4>';
        html += grouped.medium.map((s, idx) => renderSuggestion(s, '#f59e0b', idx + grouped.high.length)).join('');
        html += '</div>';
    }
    
    if (grouped.low.length > 0) {
        html += '<div style="margin-bottom: 20px;"><h4 style="color: #3b82f6; margin: 0 0 12px 0;">🔵 Low Priority Scenarios</h4>';
        html += grouped.low.map((s, idx) => renderSuggestion(s, '#3b82f6', idx + grouped.high.length + grouped.medium.length)).join('');
        html += '</div>';
    }
    
    container.innerHTML = html || '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No suggestions available</div>';
}

function renderSuggestion(suggestion, priorityColor, index) {
    const typeIcons = {
        negative: '❌',
        boundary: '📊',
        edge_case: '⚠️',
        variation: '🔄',
        compatibility: '🔌'
    };
    
    const icon = typeIcons[suggestion.type] || '💡';
    
    return `
        <div style="background: var(--card-bg); border-left: 4px solid ${priorityColor}; border-radius: 8px; padding: 15px; margin-bottom: 12px; box-shadow: var(--shadow-sm);">
            <div style="display: flex; justify-content: space-between; align-items: start; gap: 12px;">
                <div style="display: flex; align-items: start; gap: 12px; flex: 1;">
                    <input type="checkbox" class="suggestion-checkbox" data-index="${index}" onchange="updateSelectedCount()" style="margin-top: 3px; width: 18px; height: 18px; cursor: pointer; flex-shrink: 0;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                            <span style="font-size: 1.2em;">${icon}</span>
                            <strong style="color: var(--text-primary);">${suggestion.title || 'Test Scenario'}</strong>
                        </div>
                        <p style="color: var(--text-secondary); margin: 8px 0; font-size: 0.9em;">${suggestion.description || 'No description'}</p>
                    </div>
                </div>
                <button onclick="generateTestFromSuggestionByIndex(${index})" class="btn" style="padding: 4px 8px; font-size: 0.75em; background: #8b5cf6; width: auto; white-space: nowrap; flex-shrink: 0;">
                    🚀 Generate Test
                </button>
            </div>
        </div>
    `;
}

async function generateTestFromSuggestionByIndex(index) {
    if (!window.currentSuggestions || !window.currentSuggestions[index]) {
        showNotification('❌ Suggestion not found');
        return;
    }
    
    const suggestion = window.currentSuggestions[index];
    
    if (!currentSemanticSession) {
        showNotification('❌ No session selected');
        return;
    }
    
    showLoading(true);
    
    try {
        // Get the original recorded session
        const sessionResponse = await fetch(`${API_URL}/recorder/session/${currentSemanticSession}`);
        const sessionData = await sessionResponse.json();
        
        if (!sessionData.success || !sessionData.session) {
            throw new Error('Failed to load session data');
        }
        
        const session = sessionData.session;
        
        // Build enhanced prompt for this suggestion type
        const testDescription = buildEnhancedDescription(suggestion, session);
        
        // Create test name from suggestion title and type
        const testTitle = suggestion.title || suggestion.type || 'Test_Scenario';
        // Sanitize and create meaningful test name
        const baseName = testTitle.replace(/[^a-zA-Z0-9\s]/g, '').replace(/\s+/g, '_');
        const testName = `${baseName}_${suggestion.type}_test`.toLowerCase();
        
        console.log('[SEMANTIC] Generating test:', {
            testName,
            suggestionType: suggestion.type,
            priority: suggestion.priority,
            title: suggestion.title
        });
        
        // Generate test using the recorder endpoint which has full session context
        const response = await fetch(`${API_URL}/recorder/generate-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSemanticSession,
                language: 'python', // Default language for test execution
                test_name: testName,
                description: testDescription,
                suggestion_type: suggestion.type,
                suggestion_priority: suggestion.priority
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (data.success && data.code) {
            // Display in a modal and pass session data for module info
            displayGeneratedTestModal(suggestion, data.code, testDescription, session);
            showNotification('✅ Test generated successfully!');
        } else {
            throw new Error(data.error || 'Failed to generate code');
        }
    } catch (error) {
        console.error('Error:', error);
        showLoading(false);
        showNotification('❌ Failed to generate test: ' + error.message);
    }
}

function buildEnhancedDescription(suggestion, session) {
    let description = `${suggestion.title}\n\n${suggestion.description}\n\n`;
    
    // Get action details from session for context
    const actions = session.actions || [];
    const actionTypes = actions.map(a => a.action).join(', ');
    
    description += `ORIGINAL TEST ACTIONS: ${actionTypes}\n\n`;
    
    // Add type-specific instructions with concrete examples
    switch(suggestion.type.toLowerCase()) {
        case 'negative':
            description += `This is a NEGATIVE TEST - Test failure scenarios:\n`;
            description += `REQUIRED CHANGES:\n`;
            description += `- Replace all valid inputs with INVALID data:\n`;
            description += `  * Email fields: "not-an-email", "user@", "@domain.com", "plaintext"\n`;
            description += `  * Text fields: "", "   " (spaces only), null\n`;
            description += `  * Numbers: -1, "abc", special characters\n`;
            description += `  * Required fields: Leave empty or missing\n`;
            description += `- Change all success assertions to failure assertions:\n`;
            description += `  * Instead of assert success_message: assert error_message\n`;
            description += `  * Verify error messages appear: assert "Invalid" in page or "Required"\n`;
            description += `  * Check validation warnings are displayed\n`;
            description += `- Expected outcome: Operation should FAIL with proper error messages\n`;
            break;
            
        case 'boundary':
            description += `This is a BOUNDARY TEST - Test at limits:\n`;
            description += `REQUIRED CHANGES:\n`;
            description += `- Test MINIMUM values:\n`;
            description += `  * Single character: "a"\n`;
            description += `  * Zero: 0\n`;
            description += `  * Empty array: []\n`;
            description += `- Test MAXIMUM values:\n`;
            description += `  * Very long string: "a" * 1000 or "a" * 255\n`;
            description += `  * Max integer: 2147483647\n`;
            description += `  * Large files: Upload max size\n`;
            description += `- Test exact boundaries:\n`;
            description += `  * If max is 100, test with 99, 100, 101\n`;
            description += `  * Test min-1, min, min+1\n`;
            description += `- Verify proper handling at limits\n`;
            break;
            
        case 'edge_case':
            description += `This is an EDGE CASE TEST - Test unusual inputs:\n`;
            description += `REQUIRED CHANGES:\n`;
            description += `- Use special characters:\n`;
            description += `  * !@#$%^&*()_+-={}[]|\\:";'<>?,./\n`;
            description += `  * Unicode: 你好, مرحبا, Здравствуй\n`;
            description += `  * Emojis: 😀🎉✨\n`;
            description += `- Test security vulnerabilities:\n`;
            description += `  * SQL injection: ' OR '1'='1' --, admin'--\n`;
            description += `  * XSS: <script>alert('xss')</script>, <img src=x onerror=alert(1)>\n`;
            description += `  * Path traversal: ../../../etc/passwd\n`;
            description += `- Test whitespace variations:\n`;
            description += `  * Leading/trailing spaces: "  text  "\n`;
            description += `  * Multiple spaces: "text    text"\n`;
            description += `  * Tabs and newlines\n`;
            description += `- Verify input sanitization and security\n`;
            break;
            
        case 'variation':
            description += `This is a TEST VARIATION - Same goal, different approach:\n`;
            description += `REQUIRED CHANGES:\n`;
            description += `- Use DIFFERENT valid data:\n`;
            description += `  * Different email: user2@example.com instead of user1@example.com\n`;
            description += `  * Different names: Jane Doe instead of John Doe\n`;
            description += `  * Alternative valid formats\n`;
            description += `- Test alternative workflows:\n`;
            description += `  * Use keyboard shortcuts instead of mouse clicks\n`;
            description += `  * Navigate via direct URL instead of clicking links\n`;
            description += `  * Use different but valid paths to same goal\n`;
            description += `- Verify same end result with different data/approach\n`;
            break;
            
        case 'compatibility':
            description += `This is a COMPATIBILITY TEST - Test across platforms:\n`;
            description += `REQUIRED CHANGES:\n`;
            description += `- Add browser-specific checks:\n`;
            description += `  * Test in Chrome, Firefox, Safari, Edge\n`;
            description += `  * Verify responsive design (mobile, tablet, desktop)\n`;
            description += `- Test different screen sizes:\n`;
            description += `  * Mobile: 375x667\n`;
            description += `  * Tablet: 768x1024\n`;
            description += `  * Desktop: 1920x1080\n`;
            description += `- Verify cross-platform behavior consistency\n`;
            break;
            
        default:
            description += `Create a comprehensive test based on the recorded actions.\n`;
    }
    
    if (suggestion.steps && suggestion.steps.length > 0) {
        description += `\nSPECIFIC TEST STEPS FOR THIS ${suggestion.type.toUpperCase()}:\n`;
        suggestion.steps.forEach((step, i) => {
            description += `${i + 1}. ${step}\n`;
        });
    }
    
    if (suggestion.expected_result) {
        description += `\nEXPECTED RESULT: ${suggestion.expected_result}\n`;
    }
    
    description += `\nREMEMBER: This must be a DIFFERENT test from the original. Change the test data and assertions!`;
    
    return description;
}

function displayGeneratedTestModal(suggestion, code, prompt, originalSession) {
    // Create modal overlay
    const modal = document.createElement('div');
    modal.id = 'generatedTestModal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0;
        background: rgba(0, 0, 0, 0.8); z-index: 10000;
        display: flex; align-items: center; justify-content: center;
        padding: 20px; overflow-y: auto;
    `;
    
    const modalContent = document.createElement('div');
    modalContent.style.cssText = `
        background: var(--card-bg); border-radius: 12px;
        max-width: 900px; width: 100%; max-height: 90vh; overflow-y: auto;
        box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
    `;
    
    const typeColors = {
        negative: '#ef4444',
        boundary: '#f59e0b',
        edge_case: '#8b5cf6',
        variation: '#10b981',
        compatibility: '#3b82f6'
    };
    
    const color = typeColors[suggestion.type] || '#6366f1';
    
    modalContent.innerHTML = `
        <div style="background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%); padding: 24px; color: white;">
            <h3 style="margin: 0 0 8px 0; font-size: 1.4em;">✨ Generated Test Code</h3>
            <p style="margin: 0; opacity: 0.9; font-size: 0.95em;">${suggestion.title}</p>
            <div style="margin-top: 12px; padding: 12px; background: rgba(255,255,255,0.15); border-radius: 6px; font-size: 0.85em;">
                <strong>Type:</strong> ${suggestion.type} | <strong>Priority:</strong> ${suggestion.priority}
            </div>
        </div>
        
        <div style="padding: 24px;">
            <div style="margin-bottom: 20px; padding: 16px; background: var(--bg-secondary); border-radius: 8px; border-left: 4px solid ${color};">
                <strong style="display: block; margin-bottom: 8px; color: var(--text-primary);">📝 Test Description:</strong>
                <p style="margin: 0; color: var(--text-secondary); line-height: 1.6;">${suggestion.description}</p>
            </div>
            
            <div style="margin-bottom: 20px;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 12px;">
                    <strong style="color: var(--text-primary);">Generated Code:</strong>
                    <button onclick="copyGeneratedCode()" style="background: ${color}; color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer; font-size: 0.85em;">
                        📋 Copy Code
                    </button>
                </div>
                <pre style="margin: 0; padding: 20px; background: #1e293b; border-radius: 8px; overflow-x: auto; max-height: 400px;"><code id="generatedCodeDisplay" class="language-java">${escapeHtml(code)}</code></pre>
            </div>
            
            <div style="display: flex; gap: 12px; justify-content: flex-end; padding-top: 20px; border-top: 1px solid var(--border-color);">
                <button onclick="saveGeneratedTest()" class="btn" style="background: #10b981; padding: 10px 20px; font-size: 0.9em;">
                    💾 Save to Test Cases
                </button>
                <button onclick="addToSnippetsLibrary()" class="btn" style="background: #8b5cf6; padding: 10px 20px; font-size: 0.9em;">
                    📚 Add to Snippets
                </button>
                <button onclick="openInGenerator()" class="btn" style="background: #3b82f6; padding: 10px 20px; font-size: 0.9em;">
                    🚀 Open in Generator
                </button>
                <button onclick="closeGeneratedTestModal()" class="btn" style="background: var(--bg-tertiary); color: var(--text-primary); padding: 10px 20px; font-size: 0.9em;">
                    ✕ Close
                </button>
            </div>
        </div>
    `;
    
    modal.appendChild(modalContent);
    document.body.appendChild(modal);
    
    // Store data for modal actions
    window.currentGeneratedTest = {
        suggestion: suggestion,
        code: code,
        prompt: prompt,
        originalSession: originalSession
    };
    
    // Apply syntax highlighting if available
    if (window.Prism) {
        Prism.highlightElement(document.getElementById('generatedCodeDisplay'));
    }
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function closeGeneratedTestModal() {
    const modal = document.getElementById('generatedTestModal');
    if (modal) {
        modal.remove();
    }
    window.currentGeneratedTest = null;
}

async function copyGeneratedCode() {
    if (!window.currentGeneratedTest) return;
    
    try {
        await navigator.clipboard.writeText(window.currentGeneratedTest.code);
        showNotification('✅ Code copied to clipboard!');
    } catch (error) {
        console.error('Failed to copy:', error);
        showNotification('❌ Failed to copy code');
    }
}

async function saveGeneratedTest() {
    if (!window.currentGeneratedTest) return;
    
    try {
        const originalSession = window.currentGeneratedTest.originalSession || {};
        const suggestionType = window.currentGeneratedTest.suggestion.type || 'test';
        const suggestionTitle = window.currentGeneratedTest.suggestion.title || 'Generated_Test';
        
        console.log('[SAVE] Suggestion data:', window.currentGeneratedTest.suggestion);
        console.log('[SAVE] Suggestion title:', suggestionTitle);
        console.log('[SAVE] Suggestion type:', suggestionType);
        
        // Create a new session in the backend for this generated test
        const session_id = currentSemanticSession + '_' + suggestionType + '_' + Date.now();
        
        // Use suggestion title with type prefix for better identification
        const testName = `${suggestionTitle} [${suggestionType}]`;
        
        console.log('[SAVE] Final test name:', testName);
        
        // Get module from original session, fallback to 'Semantic Analysis'
        const moduleName = originalSession.module || 'Semantic Analysis';
        
        const payload = {
            session_id: session_id,
            name: testName,
            description: window.currentGeneratedTest.suggestion.description,
            type: suggestionType,
            priority: window.currentGeneratedTest.suggestion.priority,
            code: window.currentGeneratedTest.code,
            language: 'python',
            parent_session: currentSemanticSession,
            module: moduleName
        };
        
        console.log('[SAVE] Sending payload:', payload);
        
        // Save the generated test to the backend as a recorded session
        const response = await fetch(`${API_URL}/recorder/save-generated-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Test case saved to Test Suite!');
            closeGeneratedTestModal();
            
            // Reload test cases if loadTestCases function exists
            if (typeof loadTestCases === 'function') {
                await loadTestCases();
            }
        } else {
            throw new Error(data.error || 'Failed to save test');
        }
    } catch (error) {
        console.error('Error saving test:', error);
        showNotification('❌ Failed to save test: ' + error.message);
    }
}

function addToSnippetsLibrary() {
    if (!window.currentGeneratedTest) return;
    
    const snippet = {
        id: Date.now(),
        title: window.currentGeneratedTest.suggestion.title,
        description: window.currentGeneratedTest.suggestion.description,
        category: window.currentGeneratedTest.suggestion.type,
        language: 'java',
        code: window.currentGeneratedTest.code,
        tags: [
            window.currentGeneratedTest.suggestion.type, 
            window.currentGeneratedTest.suggestion.priority,
            'semantic-analysis', 
            'generated'
        ],
        date: new Date().toLocaleString(),
        createdAt: new Date().toISOString()
    };
    
    const snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    showNotification('✅ Added to code snippets library!');
}

function openInGenerator() {
    if (!window.currentGeneratedTest) return;
    
    closeGeneratedTestModal();
    navigateTo('generate');
    
    setTimeout(() => {
        document.getElementById('promptInput').value = window.currentGeneratedTest.prompt;
        displayResult(window.currentGeneratedTest.code, 0, 0);
    }, 100);
}

async function generateAllHighPriority() {
    const highPriorityTests = window.currentSuggestions?.filter(s => s.priority === 'high') || [];
    
    if (highPriorityTests.length === 0) {
        alert('No high priority tests available');
        return;
    }
    
    if (!confirm(`Generate all ${highPriorityTests.length} high priority test(s)? This will create complete executable test code for each scenario based on the recorded session.`)) {
        return;
    }
    
    if (!currentSemanticSession) {
        showNotification('❌ No session selected');
        return;
    }
    
    showLoading(true);
    let successCount = 0;
    let failCount = 0;
    
    for (const suggestion of highPriorityTests) {
        try {
            // Get session data
            const sessionResponse = await fetch(`${API_URL}/recorder/session/${currentSemanticSession}`);
            const sessionData = await sessionResponse.json();
            
            if (!sessionData.success || !sessionData.session) {
                failCount++;
                continue;
            }
            
            const testDescription = buildEnhancedDescription(suggestion, sessionData.session);
            
            // Generate test using the recorder endpoint
            const response = await fetch(`${API_URL}/recorder/generate-test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: currentSemanticSession,
                    language: 'python',
                    test_name: suggestion.title.replace(/[^a-zA-Z0-9]/g, '_'),
                    description: testDescription,
                    suggestion_type: suggestion.type,
                    suggestion_priority: suggestion.priority
                })
            });
            
            const data = await response.json();
            
            if (data.success && data.code) {
                // Save as snippet
                const snippet = {
                    id: Date.now() + Math.random(),
                    title: suggestion.title,
                    language: 'python',
                    tags: ['semantic', suggestion.type, 'high-priority', 'generated'],
                    description: suggestion.description,
                    code: data.code,
                    createdAt: new Date().toISOString(),
                    date: new Date().toLocaleString(),
                    category: suggestion.type,
                    priority: suggestion.priority
                };
                
                let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
                snippets.unshift(snippet);
                localStorage.setItem('codeSnippets', JSON.stringify(snippets));
                
                // Also save as test case
                const testCase = {
                    id: Date.now() + Math.random(),
                    session_id: currentSemanticSession + '_' + suggestion.type + '_' + Date.now(),
                    name: suggestion.title,
                    description: suggestion.description,
                    type: suggestion.type,
                    priority: suggestion.priority,
                    code: data.code,
                    created: new Date().toISOString(),
                    createdDate: new Date().toLocaleString()
                };
                
                const testCases = JSON.parse(localStorage.getItem('testCases') || '[]');
                testCases.unshift(testCase);
                localStorage.setItem('testCases', JSON.stringify(testCases));
                
                successCount++;
            } else {
                failCount++;
            }
            
            // Small delay to avoid overwhelming the API
            await new Promise(resolve => setTimeout(resolve, 500));
            
        } catch (error) {
            console.error('Error generating test:', error);
            failCount++;
        }
    }
    
    showLoading(false);
    
    if (successCount > 0) {
        showNotification(`✅ Generated ${successCount} of ${highPriorityTests.length} complete test(s)! Saved to snippets and test cases. ${failCount > 0 ? `(${failCount} failed)` : ''}`);
    } else {
        showNotification(`❌ Failed to generate tests. Please try again.`);
    }
}

function clearSemanticAnalysis() {
    currentSemanticSession = null;
    window.currentSuggestions = [];
    
    document.getElementById('semanticSessionSelect').value = '';
    
    const intentDisplay = document.getElementById('semanticIntentDisplay');
    if (intentDisplay) {
        intentDisplay.style.display = 'none';
        intentDisplay.innerHTML = '';
    }
    
    const suggestionsDisplay = document.getElementById('semanticSuggestionsDisplay');
    if (suggestionsDisplay) {
        suggestionsDisplay.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Select a test session to begin</div>';
    }

    showNotification('🗑️ Analysis cleared');
}

/**
 * Update selected count for bulk operations
 */
function updateSelectedCount() {
    const checkboxes = document.querySelectorAll('.suggestion-checkbox:checked');
    const count = checkboxes.length;
    const countSpan = document.getElementById('selectedCount');
    const generateBtn = document.getElementById('generateSelectedBtn');
    
    if (countSpan) countSpan.textContent = count;
    if (generateBtn) {
        generateBtn.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

/**
 * Toggle select all checkboxes
 */
function toggleSelectAll() {
    const checkboxes = document.querySelectorAll('.suggestion-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
    
    updateSelectedCount();
}

/**
 * Generate selected tests in bulk
 */
async function generateSelectedTests() {
    const checkboxes = document.querySelectorAll('.suggestion-checkbox:checked');
    
    if (checkboxes.length === 0) {
        alert('Please select at least one test scenario');
        return;
    }
    
    if (!confirm(`Generate ${checkboxes.length} test(s)? This will create complete executable test code for each selected scenario.`)) {
        return;
    }
    
    if (!currentSemanticSession) {
        showNotification('❌ No session selected');
        return;
    }
    
    showLoading('Generating tests...');
    let successCount = 0;
    let failCount = 0;
    
    for (const checkbox of checkboxes) {
        const index = parseInt(checkbox.dataset.index);
        const suggestion = window.currentSuggestions[index];
        
        if (suggestion) {
            try {
                // Get session data
                const sessionResponse = await fetch(`${API_URL}/recorder/session/${currentSemanticSession}`);
                const sessionData = await sessionResponse.json();
                
                if (!sessionData.success || !sessionData.session) {
                    failCount++;
                    continue;
                }
                
                const testDescription = buildEnhancedDescription(suggestion, sessionData.session);
                
                // Generate test using the recorder endpoint
                const response = await fetch(`${API_URL}/recorder/generate-test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        session_id: currentSemanticSession,
                        language: 'python',
                        test_name: suggestion.title.replace(/[^a-zA-Z0-9]/g, '_'),
                        description: testDescription,
                        suggestion_type: suggestion.type,
                        suggestion_priority: suggestion.priority
                    })
                });
                
                const data = await response.json();
                
                if (data.success && data.code) {
                    // Save as snippet and test case
                    const snippet = {
                        id: Date.now() + Math.random(),
                        title: suggestion.title,
                        language: 'python',
                        tags: ['semantic', suggestion.type, suggestion.priority, 'generated'],
                        description: suggestion.description,
                        code: data.code,
                        createdAt: new Date().toISOString(),
                        date: new Date().toLocaleString(),
                        category: suggestion.type,
                        priority: suggestion.priority
                    };
                    
                    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
                    snippets.unshift(snippet);
                    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
                    
                    const testCase = {
                        id: Date.now() + Math.random(),
                        session_id: currentSemanticSession + '_' + suggestion.type + '_' + Date.now(),
                        name: suggestion.title,
                        description: suggestion.description,
                        type: suggestion.type,
                        priority: suggestion.priority,
                        code: data.code,
                        created: new Date().toISOString(),
                        createdDate: new Date().toLocaleString()
                    };
                    
                    const testCases = JSON.parse(localStorage.getItem('testCases') || '[]');
                    testCases.unshift(testCase);
                    localStorage.setItem('testCases', JSON.stringify(testCases));
                    
                    successCount++;
                } else {
                    failCount++;
                }
                
                await new Promise(resolve => setTimeout(resolve, 500));
                
            } catch (error) {
                console.error('Error generating test:', error);
                failCount++;
            }
        }
    }
    
    hideLoading();
    
    if (successCount > 0) {
        showNotification(`✅ Generated ${successCount} of ${checkboxes.length} complete test(s)! ${failCount > 0 ? `(${failCount} failed)` : ''}`);
    } else {
        showNotification(`❌ Failed to generate tests. Please try again.`);
    }
    
    // Uncheck all
    checkboxes.forEach(cb => cb.checked = false);
    updateSelectedCount();
}

// Expose functions to window object
window.refreshSemanticSessions = refreshSemanticSessions;
window.onSemanticSessionChange = onSemanticSessionChange;
window.loadSemanticAnalysis = loadSemanticAnalysis;
window.generateSuggestions = generateSuggestions;
window.clearSemanticAnalysis = clearSemanticAnalysis;
window.generateTestFromSuggestionByIndex = generateTestFromSuggestionByIndex;
window.generateAllHighPriority = generateAllHighPriority;
window.closeGeneratedTestModal = closeGeneratedTestModal;
window.copyGeneratedCode = copyGeneratedCode;
window.saveGeneratedTest = saveGeneratedTest;
window.addToSnippetsLibrary = addToSnippetsLibrary;
window.openInGenerator = openInGenerator;
window.updateSelectedCount = updateSelectedCount;
window.toggleSelectAll = toggleSelectAll;
window.generateSelectedTests = generateSelectedTests;