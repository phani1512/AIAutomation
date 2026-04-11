// Semantic Analysis Features

let currentSemanticTestCase = null;
let semanticTestCases = [];

// Helper function to fetch test case data from the correct source
async function fetchTestCaseData(testCaseId) {
    console.log('[SEMANTIC] Fetching test case:', testCaseId);
    
    // Find the test case in our local cache to determine source
    const testCaseInfo = semanticTestCases.find(tc => tc.test_case_id === testCaseId);
    
    if (!testCaseInfo) {
        console.error('[SEMANTIC] Test case not found in cache:', testCaseId);
        return null;
    }
    
    console.log('[SEMANTIC] Test case source:', testCaseInfo.source);
    
    if (testCaseInfo.source === 'recorder') {
        // Return the cached data directly (actions already loaded in refreshSemanticSessions)
        return {
            test_case_id: testCaseInfo.test_case_id,
            name: testCaseInfo.name || testCaseInfo.test_case_id,
            source: 'recorder',
            actions: testCaseInfo.actions || [],
            url: testCaseInfo.url,
            created_at: testCaseInfo.created_at
        };
    } else {
        // Return the cached data directly (actions already loaded in refreshSemanticSessions)
        return {
            test_case_id: testCaseInfo.test_case_id,
            name: testCaseInfo.name || testCaseInfo.test_case_id,
            source: 'test-builder',
            actions: testCaseInfo.actions || testCaseInfo.prompts || testCaseInfo.steps || [],
            url: testCaseInfo.url,
            created_at: testCaseInfo.created_at
        };
    }
}

/**
 * Generate executable actions from ML suggestions
 * Takes original test actions and modifies them based on suggestion type
 */
function generateExecutableActions(suggestion, originalActions, index) {
    if (!originalActions || originalActions.length === 0) {
        // No original actions - return description as action
        return [{
            action: suggestion.title,
            description: suggestion.description,
            type: 'generated',
            steps: suggestion.steps || []
        }];
    }
    
    // Clone original actions
    const clonedActions = JSON.parse(JSON.stringify(originalActions));
    const suggestionType = suggestion.type;
    
    // Modify actions based on suggestion type
    switch (suggestionType) {
        case 'negative':
            return modifyActionsForNegativeTesting(clonedActions, suggestion);
        
        case 'boundary':
            return modifyActionsForBoundaryTesting(clonedActions, suggestion);
        
        case 'edge_case':
            return modifyActionsForEdgeCaseTesting(clonedActions, suggestion);
        
        case 'compatibility':
            return modifyActionsForCompatibilityTesting(clonedActions, suggestion);
        
        case 'performance':
            return modifyActionsForPerformanceTesting(clonedActions, suggestion);
        
        case 'security':
            return modifyActionsForSecurityTesting(clonedActions, suggestion);
        
        case 'data_validation':
        default:
            return modifyActionsForDataVariation(clonedActions, suggestion);
    }
}

function modifyActionsForNegativeTesting(actions, suggestion) {
    // Convert input values to invalid data
    return actions.map(action => {
        if (action.action?.toLowerCase().includes('enter') || 
            action.action?.toLowerCase().includes('type') ||
            action.action?.toLowerCase().includes('fill') ||
            action.prompt?.toLowerCase().includes('enter') ||
            action.prompt?.toLowerCase().includes('type')) {
            
            // Determine invalid value based on suggestion title
            let invalidValue = '';
            const title = suggestion.title.toLowerCase();
            
            if (title.includes('empty')) {
                invalidValue = '';
            } else if (title.includes('invalid email')) {
                invalidValue = 'invalid-email-format';
            } else if (title.includes('weak password')) {
                invalidValue = '123';
            } else if (title.includes('invalid')) {
                invalidValue = '@@@INVALID@@@';
            } else {
                invalidValue = '!@#$%^&*()';
            }
            
            return {
                ...action,
                value: invalidValue,
                prompt: action.prompt || action.action,
                description: `${suggestion.title}: ${action.prompt || action.action} with invalid data`
            };
        }
        return action;
    });
}

function modifyActionsForBoundaryTesting(actions, suggestion) {
    // Modify input values to boundary conditions
    return actions.map(action => {
        if (action.action?.toLowerCase().includes('enter') || 
            action.action?.toLowerCase().includes('type') ||
            action.prompt?.toLowerCase().includes('enter') ||
            action.prompt?.toLowerCase().includes('type')) {
            
            let boundaryValue = '';
            const title = suggestion.title.toLowerCase();
            
            if (title.includes('max') || title.includes('maximum')) {
                boundaryValue = 'A'.repeat(255); // Max length
            } else if (title.includes('min') || title.includes('minimum')) {
                boundaryValue = 'A'; // Min length (1 char)
            } else if (title.includes('length')) {
                boundaryValue = 'A'.repeat(100); // Medium length
            } else {
                boundaryValue = '9'.repeat(50); // Numeric boundary
            }
            
            return {
                ...action,
                value: boundaryValue,
                prompt: action.prompt || action.action,
                description: `${suggestion.title}: ${action.prompt || action.action} at boundary`
            };
        }
        return action;
    });
}

function modifyActionsForEdgeCaseTesting(actions, suggestion) {
    // Add special characters, unicode, rapid actions
    return actions.map(action => {
        if (action.action?.toLowerCase().includes('enter') || 
            action.action?.toLowerCase().includes('type') ||
            action.prompt?.toLowerCase().includes('enter') ||
            action.prompt?.toLowerCase().includes('type')) {
            
            let edgeCaseValue = '';
            const title = suggestion.title.toLowerCase();
            
            if (title.includes('special char')) {
                edgeCaseValue = '!@#$%^&*()[]{}|\\:;"\'<>?,./~`';
            } else if (title.includes('unicode')) {
                edgeCaseValue = '你好世界 مرحبا Привет こんにちは 😀🎉';
            } else if (title.includes('emoji')) {
                edgeCaseValue = '😀🎉👍❤️🚀🌟';
            } else {
                edgeCaseValue = '<script>alert("XSS")</script>';
            }
            
            return {
                ...action,
                value: edgeCaseValue,
                prompt: action.prompt || action.action,
                description: `${suggestion.title}: ${action.prompt || action.action} with edge case data`
            };
        }
        return action;
    });
}

function modifyActionsForCompatibilityTesting(actions, suggestion) {
    // Add browser/device metadata
    const title = suggestion.title.toLowerCase();
    let compatibility = '';
    
    if (title.includes('mobile')) {
        compatibility = '📱 Mobile Device Testing';
    } else if (title.includes('browser')) {
        compatibility = '🌐 Cross-Browser Testing (Chrome, Firefox, Safari, Edge)';
    } else {
        compatibility = '🔌 Compatibility Testing';
    }
    
    return [{
        action: 'compatibility_test',
        description: `${suggestion.title}: ${compatibility}`,
        prompt: `Run ${compatibility}`,
        steps: suggestion.steps || []
    }, ...actions];
}

function modifyActionsForPerformanceTesting(actions, suggestion) {
    // Add performance monitoring
    return [{
        action: 'performance_test',
        description: `${suggestion.title}: Measure load time and responsiveness`,
        prompt: 'Monitor page load time and performance metrics',
        steps: suggestion.steps || []
    }, ...actions];
}

function modifyActionsForSecurityTesting(actions, suggestion) {
    // Add security checks
    return [{
        action: 'security_test',
        description: `${suggestion.title}: Verify security measures`,
        prompt: 'Test authentication, authorization, and security controls',
        steps: suggestion.steps || []
    }, ...actions];
}

function modifyActionsForDataVariation(actions, suggestion) {
    // Vary input data values
    return actions.map((action, idx) => {
        if (action.action?.toLowerCase().includes('enter') || 
            action.action?.toLowerCase().includes('type') ||
            action.prompt?.toLowerCase().includes('enter') ||
            action.prompt?.toLowerCase().includes('type')) {
            
            const variationValue = `variation_${idx + 1}_data_${Date.now()}`;
            
            return {
                ...action,
                value: variationValue,
                prompt: action.prompt || action.action,
                description: `${suggestion.title}: ${action.prompt || action.action} with varied data`
            };
        }
        return action;
    });
}

async function refreshSemanticSessions() {
    try {
        // Load saved test cases from both recorder and test builder
        const [savedRecorderTestsResponse, testCasesResponse] = await Promise.all([
            fetch(`${API_URL}/recorder/saved-tests`),  // Saved recorder tests
            fetch(`${API_URL}/test-suite/test-cases`)   // Saved builder tests
        ]);
        
        const savedRecorderTests = await savedRecorderTestsResponse.json();
        const testCasesData = await testCasesResponse.json();
        
        let allTestCases = [];
        
        // Add saved recorder test cases WITH ACTIONS
        if (savedRecorderTests.success) {
            const recorderTests = (savedRecorderTests.test_cases || []).map(tc => ({
                ...tc,
                id: tc.test_case_id,
                test_case_id: tc.test_case_id,
                source: 'recorder',
                actions: tc.actions || [],  // ✓ CRITICAL: Cache actions for fetchTestCaseData()
                action_count: tc.action_count || tc.actions?.length || 0
            }));
            allTestCases = recorderTests;
            console.log('[SEMANTIC] Loaded', recorderTests.length, 'saved recorder tests with actions');
        }
        
        // Add saved test builder cases WITH ACTIONS
        if (testCasesData.success) {
            const builderTests = (testCasesData.test_cases || []).map(tc => {
                // ✅ DEBUG: Log URL from API response
                if (tc.test_case_id === 'TC001') {
                    console.log('[SEMANTIC-DEBUG] TC001 from API:', tc);
                    console.log('[SEMANTIC-DEBUG] TC001 URL from API:', tc.url);
                }
                
                return {
                    ...tc,
                    id: tc.test_case_id,
                    test_case_id: tc.test_case_id,
                    name: tc.name || tc.test_case_id,
                    source: 'test-builder',
                    // ✅ CRITICAL: Explicitly include URL
                    url: tc.url || '',
                    actions: tc.prompts || tc.steps || [],  // ✓ CRITICAL: Cache actions for fetchTestCaseData()
                    action_count: (tc.prompts || tc.steps || []).length  // ✓ FIXED: Calculate from actual prompts/steps array
                };
            });
            allTestCases = [...allTestCases, ...builderTests];
            console.log('[SEMANTIC] Loaded', builderTests.length, 'saved builder tests with actions');
        }
        
        semanticTestCases = allTestCases;
        
        // Sort by timestamp descending (newest first)
        semanticTestCases.sort((a, b) => {
            const timeA = a.created_at || a.timestamp || 0;
            const timeB = b.created_at || b.timestamp || 0;
            return timeB - timeA;  // Descending order (newest first)
        });
        
        updateSemanticSessionsList();
        
        // Check if we came from Test Builder with a pre-selected test case
        const preSelectedTestCaseId = sessionStorage.getItem('semanticAnalysisSessionId');
        const preSelectedTestCaseName = sessionStorage.getItem('semanticAnalysisSessionName');
        
        if (preSelectedTestCaseId) {
            // Auto-select the test case
            const select = document.getElementById('semanticSessionSelect');
            if (select) {
                select.value = preSelectedTestCaseId;
                currentSemanticTestCase = preSelectedTestCaseId;
                
                // Clear the session storage
                sessionStorage.removeItem('semanticAnalysisSessionId');
                sessionStorage.removeItem('semanticAnalysisSessionName');
                
                // Show notification
                showNotification(`✅ Auto-selected test case: ${preSelectedTestCaseName || 'Test Case'}`);
                
                // Optionally auto-load suggestions
                setTimeout(() => {
                    const autoLoad = confirm(`🤖 Would you like to automatically generate AI test variations for "${preSelectedTestCaseName}"?`);
                    if (autoLoad) {
                        generateSuggestions();
                    }
                }, 500);
            }
        } else {
            showNotification(`✅ Loaded ${allTestCases.length} test cases`);
        }
    } catch (error) {
        console.error('Error fetching test cases:', error);
        showNotification('❌ Failed to fetch test cases');
    }
}

function updateSemanticSessionsList() {
    const select = document.getElementById('semanticSessionSelect');
    
    if (!select) return;
    
    if (semanticTestCases.length === 0) {
        select.innerHTML = '<option value="">No test cases available - Save a test first</option>';
    } else {
        select.innerHTML = '<option value="">Select a test case...</option>' +
            semanticTestCases.map(testCase => {
                // Try multiple date fields and format properly
                const timestamp = testCase.created_at || testCase.timestamp || Date.now();
                // Handle timestamp - could be in seconds or milliseconds
                const timestampMs = String(timestamp).length <= 10 ? timestamp * 1000 : timestamp;
                const dateObj = new Date(timestampMs);
                const date = isNaN(dateObj.getTime()) ? '' : ` - ${dateObj.toLocaleString()}`;
                const count = testCase.action_count || testCase.prompt_count || 0;
                const source = testCase.source === 'recorder' ? '🎬' : '🧪';
                return `<option value="${testCase.test_case_id}">${source} ${testCase.name || testCase.test_case_id} (${count} steps)${date}</option>`;
            }).join('');
    }
}

function onSemanticSessionChange() {
    const testCaseId = document.getElementById('semanticSessionSelect').value;
    
    if (testCaseId) {
        currentSemanticTestCase = testCaseId;
        
        // Store the test case source for later use
        const selectedTestCase = semanticTestCases.find(tc => tc.test_case_id === testCaseId);
        if (selectedTestCase) {
            window.currentSemanticTestCaseSource = selectedTestCase.source;
            window.currentSemanticTestCaseData = selectedTestCase;
        }
        
        showNotification('✅ Test case selected. Click "Get Suggestions" to begin.');
        
        const intentDisplay = document.getElementById('semanticIntentDisplay');
        if (intentDisplay) {
            intentDisplay.style.display = 'none';
        }
        const suggestionsDisplay = document.getElementById('semanticSuggestionsDisplay');
        if (suggestionsDisplay) {
            suggestionsDisplay.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Click "Get Suggestions" to generate AI-powered test scenarios</div>';
        }
    } else {
        currentSemanticTestCase = null;
        window.currentSemanticTestCaseSource = null;
        window.currentSemanticTestCaseData = null;
    }
}

async function loadSemanticAnalysis() {
    const testCaseId = document.getElementById('semanticSessionSelect').value;
    
    if (!testCaseId) {
        alert('Please select a test case first');
        return;
    }
    
    currentSemanticTestCase = testCaseId;
    showLoading(true);
    
    try {
        // Fetch test case from appropriate source
        const testCase = await fetchTestCaseData(testCaseId);
        
        if (!testCase) {
            console.warn('[SEMANTIC] Test case not found');
            showLoading(false);
            showNotification('⚠️ Test case not found. Please refresh and try again.');
            return;
        }
        
        console.log('[SEMANTIC] Analyzing test case:', testCase);
        const actions = testCase.actions || testCase.prompts || testCase.steps || [];
        
        // Build prompt based on test case structure
        let actionDescription = '';
        if (Array.isArray(actions)) {
            if (actions[0]?.action) {
                // Recorder format: {action, selector, value}
                actionDescription = actions.map(a => `${a.action} on ${a.selector || 'element'}`).join(', ');
            } else if (actions[0]?.prompt) {
                // Builder format: {prompt, type}
                actionDescription = actions.map(a => a.prompt).join(', ');
            } else {
                actionDescription = actions.join(', ');
            }
        }
        
        const prompt = `Analyze the intent of this test: ${testCase.name || 'Test Case'}. Actions: ${actionDescription}`;
        
        const response = await fetch(`${API_URL}/semantic/analyze-intent`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                test_case_id: testCaseId,
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

async function generateTestCases() {
    if (!currentSemanticTestCase) {
        alert('Please select a test case first');
        return;
    }
    
    // Check if user wants to retrain (advanced option)
    const shouldRetrain = document.getElementById('retrainModelCheckbox')?.checked || false;
    
    if (shouldRetrain) {
        // Use slow retraining endpoint
        showLoading(true, '🔄 Step 1/2: Retraining ML model with your test case...', true);
        
        try {
            const response = await fetch(`${API_URL}/semantic/generate-test-cases`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_case_id: currentSemanticTestCase })
            });
            
            const data = await response.json();
            showLoading(false);
            
            if (data.success && data.generated_tests && data.generated_tests.length > 0) {
                displayGeneratedTests(data.generated_tests, data.source_test, data.ml_retrained);
                
                let message = `✅ Generated ${data.total_generated} test cases`;
                if (data.ml_retrained) {
                    message += ' • 🧠 ML model retrained!';
                }
                showNotification(message, 'success');
            } else {
                const errorMsg = data.error || 'No test cases generated';
                showNotification(`⚠️ ${errorMsg}`, 'warning');
            }
        } catch (error) {
            console.error('Error generating test cases:', error);
            showLoading(false);
            showNotification('❌ Failed to generate test cases: ' + error.message, 'error');
        }
    } else {
        // Use FAST ML endpoint (no retraining)
        showLoading(true, '🤖 Getting ML-powered test suggestions...', true);
        
        try {
            const response = await fetch(`${API_URL}/ml/suggest-test-scenarios`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ test_case_id: currentSemanticTestCase })
            });
            
            const data = await response.json();
            showLoading(false);
            
            if (data.success && data.suggestions && data.suggestions.length > 0) {
                // Fetch original test case to get actions
                const originalTestCase = await fetchTestCaseData(currentSemanticTestCase);
                const originalActions = originalTestCase?.actions || [];
                
                // ✅ FIX: Extract URL from parent test case
                const parentUrl = originalTestCase?.url || '';
                console.log('[SEMANTIC-FIX] 🔧 Parent test URL:', parentUrl);
                
                // Convert ML suggestions to test case format WITH executable actions
                const generatedTests = data.suggestions.map((suggestion, index) => {
                    const executableActions = generateExecutableActions(suggestion, originalActions, index);
                    
                    return {
                        test_case_id: `${currentSemanticTestCase}_variant_${index + 1}`,
                        name: suggestion.title,
                        description: suggestion.description,
                        type: suggestion.type,
                        generation_type: suggestion.type,
                        priority: suggestion.priority,
                        confidence: suggestion.confidence,
                        actions: executableActions,
                        steps: suggestion.steps || [], // Include suggested steps as guidance
                        // ✅ FIX: Add URL and parent_test_case_id from parent test
                        url: parentUrl,
                        parent_test_case_id: currentSemanticTestCase
                    };
                });
                
                displayGeneratedTests(generatedTests, { name: data.test_name }, false);
                
                // Count scenarios by type for comprehensive message
                const typeCount = {};
                generatedTests.forEach(test => {
                    typeCount[test.type] = (typeCount[test.type] || 0) + 1;
                });
                
                const typeLabels = {
                    'negative': '🔴 Negative',
                    'boundary': '📏 Boundary',
                    'edge_case': '⚡ Edge Case',
                    'compatibility': '🌐 Compatibility',
                    'performance': '⚙️ Performance',
                    'security': '🔒 Security',
                    'data_validation': '✅ Validation'
                };
                
                let typeBreakdown = Object.entries(typeCount)
                    .map(([type, count]) => `${typeLabels[type] || type}: ${count}`)
                    .join(', ');
                
                let message = `✅ Generated ${data.suggestions_count} comprehensive test scenarios\\n${typeBreakdown}`;
                if (data.ml_used) {
                    message += '\\n🧠 RandomForest ML model';
                }
                showNotification(message, 'success');
            } else {
                const errorMsg = data.error || 'No suggestions generated';
                showNotification(`⚠️ ${errorMsg}`, 'warning');
            }
        } catch (error) {
            console.error('Error getting ML suggestions:', error);
            showLoading(false);
            showNotification('❌ Failed to get suggestions: ' + error.message, 'error');
        }
    }
}

// Keep old function name for compatibility
const generateSuggestions = generateTestCases;

function displayGeneratedTests(generatedTests, sourceTest, mlRetrained = false) {
    const container = document.getElementById('semanticSuggestionsDisplay');
    if (!container) return;
    
    window.currentGeneratedTests = generatedTests;
    window.sourceTest = sourceTest;
    
    let html = '';
    
    if (generatedTests.length > 0) {
        html += '<div style="display: flex; gap: 10px; margin-bottom: 20px; padding: 15px; background: var(--bg-secondary); border-radius: 8px; flex-wrap: wrap; align-items: center;">';
        html += `<span style="color: var(--text-secondary); font-size: 0.9em;">📊 ${generatedTests.length} test cases generated</span>`;
        
        // Show ML retrain status badge
        if (mlRetrained) {
            html += '<span style="background: #10b981; color: white; padding: 4px 12px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">🧠 ML Retrained</span>';
        }
        
        html += `<button class="btn" onclick="toggleSelectAll()" style="background: #6b7280; padding: 8px 16px; font-size: 0.9em; width: auto;">☑️ Select All</button>`;
        html += `<button class="btn" onclick="saveSelectedGeneratedTests()" id="saveSelectedBtn" style="background: #10b981; padding: 8px 16px; font-size: 0.9em; width: auto; display: none;">💾 Save Selected (<span id="selectedCount">0</span>)</button>`;
        html += '</div>';
        
        // Display all generated tests
        html += '<div style="display: grid; gap: 12px;">';
        html += generatedTests.map((test, idx) => renderGeneratedTest(test, idx)).join('');
        html += '</div>';
    } else {
        html = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No test cases generated</div>';
    }
    
    container.innerHTML = html;
}

// Keep old function for compatibility (if needed)
const displaySuggestions = displayGeneratedTests;

function renderGeneratedTest(test, index) {
    const typeIcons = {
        negative: '❌',
        boundary: '📊',
        edge_case: '⚠️',
        variation: '🔄',
        compatibility: '🔌',
        performance: '⚙️',
        security: '🔒',
        data_validation: '✅'
    };
    
    const testType = test.generation_type || test.type || 'variation';
    const icon = typeIcons[testType] || '🧪';
    const actionCount = test.actions?.length || 0;
    
    // Generate action preview
    let actionPreview = '';
    if (test.actions && test.actions.length > 0) {
        const firstAction = test.actions[0];
        const actionText = firstAction.description || firstAction.prompt || firstAction.action || 'Test action';
        actionPreview = `<div style="color: var(--text-secondary); font-size: 0.85em; margin-top: 5px;">First: ${actionText.substring(0, 60)}${actionText.length > 60 ? '...' : ''}</div>`;
    }
    
    return `
        <div style="background: var(--card-bg); border-left: 4px solid #8b5cf6; border-radius: 8px; padding: 15px; box-shadow: var(--shadow-sm);">
            <div style="display: flex; align-items: start; gap: 12px;">
                <input type="checkbox" class="test-checkbox" data-index="${index}" onchange="updateSelectedCount()" style="margin-top: 3px; width: 18px; height: 18px; cursor: pointer; flex-shrink: 0;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 5px;">
                        <span style="font-size: 1.2em;">${icon}</span>
                        <strong style="color: var(--text-primary);">${test.name || test.test_name || 'Generated Test'}</strong>
                        <span style="background: #8b5cf620; color: #8b5cf6; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">${testType}</span>
                        ${test.confidence ? `<span style="background: #10b98120; color: #10b981; padding: 2px 8px; border-radius: 12px; font-size: 0.75em;">✓ ${Math.round(test.confidence * 100)}%</span>` : ''}
                    </div>
                    <p style="color: var(--text-secondary); margin: 8px 0 12px 0; font-size: 0.9em;">${test.description || 'No description'}</p>
                    <div style="display: flex; gap: 8px; flex-wrap: wrap; font-size: 0.85em; color: var(--text-secondary);">
                        <span>📝 ${actionCount} ${actionCount === 1 ? 'action' : 'actions'}</span>
                        ${test.priority ? `<span>🎯 ${test.priority}</span>` : ''}
                        ${test.suite_name ? `<span>📁 ${test.suite_name}</span>` : ''}
                    </div>
                    ${actionPreview}
                </div>
                <button onclick="viewGeneratedTestDetails(${index})" class="btn" style="padding: 6px 12px; font-size: 0.8em; background: #6366f1; width: auto; white-space: nowrap; flex-shrink: 0;">
                    👁️ View
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
    
    // Enhanced validation with detailed logging
    if (!currentSemanticTestCase) {
        console.error('[SEMANTIC-ERROR] currentSemanticTestCase is null or undefined');
        console.log('[SEMANTIC-DEBUG] Checking dropdown value...');
        const dropdown = document.getElementById('semanticSessionSelect');
        if (dropdown && dropdown.value) {
            console.log('[SEMANTIC-FIX] Found value in dropdown, updating currentSemanticTestCase:', dropdown.value);
            currentSemanticTestCase = dropdown.value;
        } else {
            showNotification('❌ No test case selected. Please select a test case from the dropdown first.');
            return;
        }
    }
    
    console.log('[SEMANTIC] Generating test for suggestion:', { 
        index, 
        type: suggestion.type, 
        title: suggestion.title,
        testCaseId: currentSemanticTestCase 
    });
    
    showLoading(true);
    
    try {
        // Fetch test case from appropriate source
        const testCase = await fetchTestCaseData(currentSemanticTestCase);
        
        if (!testCase) {
            throw new Error('Test case not found. Please refresh and try again.');
        }
        
        console.log('[SEMANTIC] Generating from test case:', testCase);
        
        // Use backend-provided description (contains detailed test instructions)
        const testDescription = suggestion.description;
        
        // Build test name from suggestion
        const testName = `${suggestion.title || 'Test'} [${suggestion.type || 'general'}]`;
        
        // Log the request payload for debugging
        const requestPayload = {
            test_case_id: currentSemanticTestCase,
            language: 'python',
            test_name: testName,
            description: testDescription,
            suggestion_type: suggestion.type,
            suggestion_priority: suggestion.priority,
            compact_mode: true
        };
        
        console.log('[SEMANTIC] Sending generate request:', requestPayload);
        console.log('[SEMANTIC] Test case has', testCase.actions?.length || 0, 'actions');
        
        // Generate test using the test case context
        const response = await fetch(`${API_URL}/recorder/generate-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(requestPayload)
        });
        
        const data = await response.json();
        showLoading(false);
        
        console.log('[SEMANTIC] Generate response:', { success: data.success, hasCode: !!data.code, error: data.error });
        
        if (data.success && data.code) {
            // Display in a modal and pass test case data for module info
            displayGeneratedTestModal(suggestion, data.code, testDescription, testCase);
            showNotification('✅ Test generated successfully!');
        } else {
            const errorMsg = data.error || 'Failed to generate code - no code returned';
            console.error('[SEMANTIC] Generation failed:', errorMsg);
            throw new Error(errorMsg);
        }
    } catch (error) {
        console.error('Error:', error);
        showLoading(false);
        showNotification('❌ Failed to generate test: ' + error.message);
    }
}

function displayGeneratedTestModal(suggestion, code, prompt, originalTestCase) {
    // Remove existing modal if any
    const existingModal = document.getElementById('generatedTestModal');
    if (existingModal) {
        existingModal.remove();
    }
    
    // Store for later use
    window.currentGeneratedTest = {
        code: code,
        suggestion: suggestion,
        prompt: prompt,
        originalTestCase: originalTestCase
    };
    window.currentGeneratedCode = code;
    window.currentGeneratedSuggestion = suggestion;
    window.currentGeneratedPrompt = prompt;
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const typeColors = {
        negative: '#ef4444',
        boundary: '#f59e0b',
        edge_case: '#8b5cf6',
        variation: '#10b981',
        compatibility: '#3b82f6'
    };
    
    const color = typeColors[suggestion.type] || '#6366f1';
    
    // Create full-screen modal matching test-suite style
    const modal = document.createElement('div');
    modal.id = 'generatedTestModal';
    modal.className = 'modal-overlay';
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
    
    modal.innerHTML = `
        <div style="width: 90%; max-width: 1200px; height: 90vh; background: var(--bg-secondary); border-radius: 12px; box-shadow: 0 20px 60px rgba(0,0,0,0.5); display: flex; flex-direction: column; overflow: hidden;">
            <!-- Modal Header -->
            <div style="display: flex; justify-content: space-between; align-items: center; padding: 20px 24px; border-bottom: 2px solid var(--border-color); background: linear-gradient(135deg, ${color} 0%, ${color}dd 100%);">
                <div>
                    <h3 style="margin: 0; color: white; font-size: 18px; font-weight: 600;">
                        ✨ Generated Test Code - ${suggestion.title}
                    </h3>
                    <p style="margin: 4px 0 0 0; color: rgba(255,255,255,0.9); font-size: 13px;">
                        Type: ${suggestion.type} | Priority: ${suggestion.priority}
                    </p>
                </div>
                <div style="display: flex; gap: 8px; align-items: center;">
                    <button onclick="copyGeneratedCode()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        📋 Copy
                    </button>
                    <button onclick="saveGeneratedTest()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        💾 Save
                    </button>
                    <button onclick="addToSnippetsLibrary()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; cursor: pointer; font-size: 13px; font-weight: 500;">
                        📚 Snippets
                    </button>
                    <button onclick="closeGeneratedTestModal()" style="padding: 8px 16px; background: rgba(255,255,255,0.2); color: white; border: 1px solid rgba(255,255,255,0.3); border-radius: 6px; cursor: pointer; font-size: 18px; font-weight: 600; line-height: 1;">
                        ✕
                    </button>
                </div>
            </div>
            
            <!-- Modal Body: Code Viewer -->
            <div class="code-modal-body" style="flex: 1; overflow: auto; padding: 0;">
                <pre style="margin: 0; padding: 24px; height: 100%; background: #0f172a;"><code id="generatedCodeDisplay" class="language-${language}" style="font-size: 14px; line-height: 1.6; display: block; white-space: pre;">${escapeHtml(code)}</code></pre>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
    
    // Apply syntax highlighting if available
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(document.getElementById('generatedCodeDisplay'));
    }
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeGeneratedTestModal();
        }
    });
    
    // Close on background click
    modal.addEventListener('click', (e) => {
        if (e.target === modal) {
            closeGeneratedTestModal();
        }
    });
    
    // Store data for modal actions
    window.currentGeneratedTest = {
        suggestion: suggestion,
        code: code,
        prompt: prompt,
        originalTestCase: originalTestCase
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
        const originalTestCase = window.currentGeneratedTest.originalTestCase || {};
        const suggestionType = window.currentGeneratedTest.suggestion.type || 'test';
        const suggestionTitle = window.currentGeneratedTest.suggestion.title || 'Generated_Test';
        
        console.log('[SAVE] Suggestion data:', window.currentGeneratedTest.suggestion);
        console.log('[SAVE] Suggestion title:', suggestionTitle);
        console.log('[SAVE] Suggestion type:', suggestionType);
        
        // Create a new test case ID for this generated test
        const test_case_id = currentSemanticTestCase + '_' + suggestionType + '_' + Date.now();
        
        // Use suggestion title with type prefix for better identification
        const testName = `${suggestionTitle} [${suggestionType}]`;
        
        console.log('[SAVE] Final test name:', testName);
        
        // Get module from original test case, fallback to 'Semantic Analysis'
        const moduleName = originalTestCase.module || originalTestCase.tags?.join(', ') || 'Semantic Analysis';
        
        const payload = {
            test_case_id: test_case_id,
            name: testName,
            description: window.currentGeneratedTest.suggestion.description,
            type: suggestionType,
            priority: window.currentGeneratedTest.suggestion.priority,
            code: window.currentGeneratedTest.code,
            language: 'python',
            parent_test_case: currentSemanticTestCase,
            module: moduleName
        };
        
        console.log('[SAVE] Sending payload:', payload);
        
        // Save the generated test to the backend
        const response = await fetch(`${API_URL}/recorder/save-generated-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(payload)
        });
        
        const data = await response.json();
        
        if (data.success) {
            showNotification('✅ Test case saved to Test Suite!');
            closeGeneratedTestModal();
            
            // Increment tests generated counter (recorder/builder only)
            if (typeof window.incrementTestsGenerated === 'function') {
                window.incrementTestsGenerated();
            }
            
            // Add to activity timeline
            if (typeof window.addTestResult === 'function') {
                window.addTestResult(
                    payload.name || 'Semantic Test',
                    'passed',
                    0,
                    'Test case saved via Semantic Analysis'
                );
            }
            
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
    if (!window.currentGeneratedTest) {
        console.warn('[SEMANTIC] No generated test data available');
        return;
    }
    
    // Store data for later retrieval
    const testData = {
        prompt: window.currentGeneratedTest.prompt || '',
        code: window.currentGeneratedTest.code || '',
        timestamp: Date.now()
    };
    
    // Store in sessionStorage for cross-page access
    sessionStorage.setItem('pendingGeneratedTest', JSON.stringify(testData));
    
    closeGeneratedTestModal();
    navigateTo('generate');
    
    // Wait for generate-code page to fully load and DOM to be ready
    const checkAndPopulate = (attempts = 0) => {
        const promptInput = document.getElementById('promptInput');
        const resultContent = document.getElementById('resultContent');
        
        if (promptInput && resultContent) {
            // Page is ready, populate fields
            const storedData = sessionStorage.getItem('pendingGeneratedTest');
            if (storedData) {
                try {
                    const data = JSON.parse(storedData);
                    promptInput.value = data.prompt;
                    
                    // Use displayResult if available, otherwise direct populate
                    if (typeof displayResult === 'function') {
                        displayResult(data.code, 0, 0);
                    } else {
                        resultContent.textContent = data.code;
                        if (typeof Prism !== 'undefined') {
                            Prism.highlightElement(resultContent);
                        }
                    }
                    
                    // Clear stored data
                    sessionStorage.removeItem('pendingGeneratedTest');
                    console.log('[SEMANTIC] Successfully populated generator with test data');
                } catch (err) {
                    console.error('[SEMANTIC] Error populating generator:', err);
                }
            }
        } else if (attempts < 20) {
            // Page not ready yet, retry with exponential backoff
            setTimeout(() => checkAndPopulate(attempts + 1), 50 + (attempts * 50));
        } else {
            console.error('[SEMANTIC] Generate code page elements not found after multiple retries');
            sessionStorage.removeItem('pendingGeneratedTest');
        }
    };
    
    // Start checking after navigation begins
    setTimeout(() => checkAndPopulate(0), 100);
}

async function generateAllHighPriority() {
    const highPriorityTests = window.currentSuggestions?.filter(s => s.priority === 'high') || [];
    
    if (highPriorityTests.length === 0) {
        alert('No high priority tests available');
        return;
    }
    
    if (!confirm(`Generate all ${highPriorityTests.length} high priority test(s)? This will create complete executable test code for each scenario based on the test case.`)) {
        return;
    }
    
    if (!currentSemanticTestCase) {
        showNotification('❌ No test case selected');
        return;
    }
    
    showLoading(true);
    let successCount = 0;
    let failCount = 0;
    
    for (const suggestion of highPriorityTests) {
        try {
            // Fetch test case from appropriate source
            const testCase = await fetchTestCaseData(currentSemanticTestCase);
            
            if (!testCase) {
                failCount++;
                continue;
            }
            
            // Use backend-provided description (contains detailed test instructions)
            const testDescription = suggestion.description;
            
            // Generate test using the test case context
            const response = await fetch(`${API_URL}/recorder/generate-test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    test_case_id: currentSemanticTestCase,
                    language: 'python',
                    test_name: suggestion.title.replace(/[^a-zA-Z0-9]/g, '_'),
                    description: testDescription,
                    suggestion_type: suggestion.type,
                    suggestion_priority: suggestion.priority,
                    compact_mode: true      // Generate compact code (70% smaller) for DB/CI-CD
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
                    test_case_id: currentSemanticTestCase + '_' + suggestion.type + '_' + Date.now(),
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
    currentSemanticTestCase = null;
    window.currentSuggestions = [];
    
    document.getElementById('semanticSessionSelect').value = '';
    
    const intentDisplay = document.getElementById('semanticIntentDisplay');
    if (intentDisplay) {
        intentDisplay.style.display = 'none';
        intentDisplay.innerHTML = '';
    }
    
    const suggestionsDisplay = document.getElementById('semanticSuggestionsDisplay');
    if (suggestionsDisplay) {
        suggestionsDisplay.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Select a test case to begin</div>';
    }

    showNotification('🗑️ Analysis cleared');
}

/**
 * Update selected count for bulk operations
 */
function updateSelectedCount() {
    // Support both old suggestion-checkbox and new test-checkbox
    const checkboxes = document.querySelectorAll('.suggestion-checkbox:checked, .test-checkbox:checked');
    const count = checkboxes.length;
    const countSpan = document.getElementById('selectedCount');
    const saveBtn = document.getElementById('saveSelectedBtn');
    const generateBtn = document.getElementById('generateSelectedBtn');
    
    if (countSpan) countSpan.textContent = count;
    
    // Show save button for generated tests
    if (saveBtn) {
        saveBtn.style.display = count > 0 ? 'inline-block' : 'none';
    }
    
    // Show generate button for suggestions (legacy)
    if (generateBtn) {
        generateBtn.style.display = count > 0 ? 'inline-block' : 'none';
    }
}

/**
 * Toggle select all checkboxes
 */
function toggleSelectAll() {
    // Support both old and new checkbox classes
    const checkboxes = document.querySelectorAll('.suggestion-checkbox, .test-checkbox');
    const allChecked = Array.from(checkboxes).every(cb => cb.checked);
    
    checkboxes.forEach(cb => {
        cb.checked = !allChecked;
    });
    
    updateSelectedCount();
}

/**
 * Save selected generated tests to test_suites/ with modal
 */
async function saveSelectedGeneratedTests() {
    const checkboxes = document.querySelectorAll('.test-checkbox:checked');
    
    if (checkboxes.length === 0) {
        showNotification('⚠️ Please select at least one test to save', 'warning');
        return;
    }
    
    // Update selected count in modal
    document.getElementById('selectedTestCount').textContent = checkboxes.length;
    
    // Show modal
    document.getElementById('saveGeneratedTestsModal').style.display = 'flex';
}

/**
 * Close save modal
 */
function closeSaveGeneratedTestsModal() {
    const modal = document.getElementById('saveGeneratedTestsModal');
    if (modal) {
        modal.style.display = 'none';
    }
}

/**
 * Confirm and save selected tests
 */
async function confirmSaveGeneratedTests() {
    const checkboxes = document.querySelectorAll('.test-checkbox:checked');
    const selectedIndexes = Array.from(checkboxes).map(cb => parseInt(cb.dataset.index));
    const selectedTests = selectedIndexes.map(idx => window.currentGeneratedTests[idx]).filter(Boolean);
    
    if (selectedTests.length === 0) {
        showNotification('❌ No valid tests selected');
        closeSaveGeneratedTestsModal();
        return;
    }
    
    // Get test type from modal
    const testType = document.getElementById('generatedTestType').value;
    
    // DEBUG: Log current semantic test case value
    console.log('[SEMANTIC-SAVE] 🔍 currentSemanticTestCase:', currentSemanticTestCase);
    console.log('[SEMANTIC-SAVE] 🔍 selectedTests count:', selectedTests.length);
    
    // Determine source from original test case
    const originalTestCase = await fetchTestCaseData(currentSemanticTestCase);
    const sourceType = originalTestCase?.source || 'builder';  // Default to builder
    
    console.log('[SEMANTIC-SAVE] 🔍 originalTestCase:', originalTestCase);
    console.log('[SEMANTIC-SAVE] 🔍 originalTestCase.url:', originalTestCase?.url);
    
    // Add source and semantic metadata to each test
    selectedTests.forEach(test => {
        if (!test.source) {
            test.source = sourceType;
        }
        test.test_type = testType;
        // ✅ Only set parent_test_case_id if not already set during generation
        if (!test.parent_test_case_id) {
            test.parent_test_case_id = currentSemanticTestCase;
        }
        console.log('[SEMANTIC-SAVE] 🔍 Test parent_test_case_id:', test.parent_test_case_id, 'url:', test.url, 'test_id:', test.test_case_id);
        test.generated_by = 'semantic-analysis';
        test.variant_type = test.generation_type || 'semantic-generated';
        
        // Add tags for easy filtering
        const tags = test.tags || [];
        test.tags = [...new Set([...tags, 'semantic', 'ai-generated', testType, test.generation_type || 'generated'])];
    });
    
    // DEBUG: Log test data before sending
    console.log('[SEMANTIC-SAVE] 📤 About to send tests:', selectedTests);
    console.log('[SEMANTIC-SAVE] 📤 First test parent_test_case_id:', selectedTests[0]?.parent_test_case_id);
    console.log('[SEMANTIC-SAVE] 📤 First test url:', selectedTests[0]?.url);
    
    // Close modal and show loading
    closeSaveGeneratedTestsModal();
    showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/semantic/save-generated-tests`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                tests: selectedTests,
                test_type: testType
            })
        });
        
        const data = await response.json();
        showLoading(false);
        
        if (data.success) {
            // Build list of saved test names (not just IDs)
            const testNames = selectedTests.map(t => t.name || t.test_case_id).join(', ');
            let message = `✅ Saved ${data.saved_count} test case${data.saved_count !== 1 ? 's' : ''}: ${testNames}`;
            if (data.saved_as_builder > 0) {
                message += `\n📋 ${data.saved_as_builder} as Builder tests`;
            }
            if (data.saved_as_recorder > 0) {
                message += `\n🎬 ${data.saved_as_recorder} as Recorder tests`;
            }
            message += `\n🎯 Type: ${data.test_type}`;
            message += `\n📁 Location: test_suites/${data.test_type}/`;
            showNotification(message, 'success');
            
            // Uncheck saved tests
            checkboxes.forEach(cb => cb.checked = false);
            updateSelectedCount();
            
            // Refresh test list
            if (typeof refreshSemanticSessions === 'function') {
                setTimeout(() => refreshSemanticSessions(), 1000);
            }
        } else {
            showNotification(`⚠️ ${data.message || data.error || 'Failed to save tests'}`, 'error');
        }
    } catch (error) {
        console.error('Error saving generated tests:', error);
        showLoading(false);
        showNotification('❌ Failed to save tests: ' + error.message, 'error');
    }
}

/**
 * View details of a generated test case
 */
function viewGeneratedTestDetails(index) {
    if (!window.currentGeneratedTests || !window.currentGeneratedTests[index]) {
        showNotification('❌ Test not found');
        return;
    }
    
    const test = window.currentGeneratedTests[index];
    
    let actionsHtml = '';
    if (test.actions && test.actions.length > 0) {
        actionsHtml = test.actions.map((action, idx) => {
            // Get action text
            const actionText = action.description || action.prompt || action.action || 'Action';
            const valueText = action.value ? `<div style="margin-top: 5px; color: var(--text-secondary);">
                <strong>Value:</strong> <code style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px; font-size: 0.9em;">${action.value}</code>
            </div>` : '';
            
            const locatorInfo = action.locator ? `<div style="margin-top: 5px; font-size: 0.85em; color: var(--text-secondary);">
                <strong>Locator:</strong> ${action.locator_type || 'auto'} = <code style="background: var(--bg-tertiary); padding: 2px 6px; border-radius: 4px;">${action.locator}</code>
            </div>` : '';
            
            const typeInfo = action.type ? `<span style="background: #3b82f620; color: #3b82f6; padding: 2px 8px; border-radius: 12px; font-size: 0.75em; margin-left: 8px;">${action.type}</span>` : '';
            
            return `
                <div style="padding: 12px; background: var(--bg-secondary); border-radius: 6px; margin-bottom: 8px; border-left: 3px solid #8b5cf6;">
                    <div style="display: flex; gap: 8px; align-items: center;">
                        <span style="background: #8b5cf6; color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.75em; font-weight: bold;">Step ${idx + 1}</span>
                        <strong style="color: var(--text-primary);">${actionText}</strong>
                        ${typeInfo}
                    </div>
                    ${valueText}
                    ${locatorInfo}
                    ${action.steps && action.steps.length > 0 ? `
                        <div style="margin-top: 8px; padding-top: 8px; border-top: 1px solid var(--border-color);">
                            <strong style="color: var(--text-secondary); font-size: 0.85em;">Implementation Steps:</strong>
                            <ul style="margin: 5px 0 0 0; padding-left: 20px; color: var(--text-secondary); font-size: 0.85em;">
                                ${action.steps.map(step => `<li>${step}</li>`).join('')}
                            </ul>
                        </div>
                    ` : ''}
                </div>
            `;
        }).join('');
    }
    
    // Add suggested steps if available
    let stepsHtml = '';
    if (test.steps && test.steps.length > 0) {
        stepsHtml = `
            <div style="margin-top: 20px; padding: 15px; background: var(--bg-secondary); border-radius: 8px; border: 1px solid var(--border-color);">
                <h4 style="color: var(--text-primary); margin: 0 0 10px 0;">💡 Suggested Implementation Steps</h4>
                <ol style="margin: 0; padding-left: 20px; color: var(--text-secondary);">
                    ${test.steps.map(step => `<li style="margin-bottom: 5px;">${step}</li>`).join('')}
                </ol>
            </div>
        `;
    }
    
    const modalHtml = `
        <div style="position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;" onclick="this.remove()">
            <div style="background: var(--bg-primary); border-radius: 12px; padding: 25px; max-width: 800px; width: 90%; max-height: 80vh; overflow-y: auto; box-shadow: 0 10px 40px rgba(0,0,0,0.3);" onclick="event.stopPropagation()">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 20px;">
                    <h3 style="color: var(--text-primary); margin: 0;">${test.name || test.test_name || 'Test Details'}</h3>
                    <button onclick="this.closest('div[style*=fixed]').remove()" style="background: #ef4444; color: white; border: none; padding: 5px 10px; border-radius: 6px; cursor: pointer; font-size: 0.9em;">✕ Close</button>
                </div>
                
                ${test.description ? `<p style="color: var(--text-secondary); margin-bottom: 15px;">${test.description}</p>` : ''}
                
                <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
                    <span style="background: #8b5cf620; color: #8b5cf6; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">
                        🏷️ ${test.generation_type || test.type || 'variation'}
                    </span>
                    ${test.priority ? `<span style="background: #f59e0b20; color: #f59e0b; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">🎯 ${test.priority}</span>` : ''}
                    ${test.confidence ? `<span style="background: #10b98120; color: #10b981; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">✓ Confidence: ${Math.round(test.confidence * 100)}%</span>` : ''}
                    ${test.suite_name ? `<span style="background: #3b82f620; color: #3b82f6; padding: 4px 10px; border-radius: 12px; font-size: 0.85em;">📁 ${test.suite_name}</span>` : ''}
                </div>
                
                <h4 style="color: var(--text-primary); margin-top: 20px; margin-bottom: 12px;">📋 Test Actions (${test.actions?.length || 0})</h4>
                ${actionsHtml || '<div style="color: var(--text-secondary); padding: 20px; text-align: center; background: var(--bg-secondary); border-radius: 6px;">No actions defined</div>'}
                
                ${stepsHtml}
            </div>
        </div>
    `;
    
    document.body.insertAdjacentHTML('beforeend', modalHtml);
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
    
    if (!currentSemanticTestCase) {
        showNotification('❌ No test case selected');
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
                // Fetch test case from appropriate source
                const testCase = await fetchTestCaseData(currentSemanticTestCase);
                
                if (!testCase) {
                    failCount++;
                    continue;
                }
                
                // Use backend-provided description (contains detailed test instructions)
                const testDescription = suggestion.description;
                
                // Generate test using the test case context
                const response = await fetch(`${API_URL}/recorder/generate-test`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        test_case_id: currentSemanticTestCase,
                        language: 'python',
                        test_name: suggestion.title.replace(/[^a-zA-Z0-9]/g, '_'),
                        description: testDescription,
                        suggestion_type: suggestion.type,
                        suggestion_priority: suggestion.priority,
                        compact_mode: true      // Generate compact code (70% smaller) for DB/CI-CD
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
                        test_case_id: currentSemanticTestCase + '_' + suggestion.type + '_' + Date.now(),
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
window.generateSuggestions = generateSuggestions; // Legacy compatibility
window.generateTestCases = generateTestCases; // New function
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
window.saveSelectedGeneratedTests = saveSelectedGeneratedTests; // New function
window.closeSaveGeneratedTestsModal = closeSaveGeneratedTestsModal; // New function
window.confirmSaveGeneratedTests = confirmSaveGeneratedTests; // New function
window.viewGeneratedTestDetails = viewGeneratedTestDetails; // New function
window.displayGeneratedTests = displayGeneratedTests; // New function