// Test Suite Management

async function loadTestCases() {
    try {
        const response = await fetch(`${API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (data.success) {
            // Sort sessions by timestamp - LATEST FIRST
            const sortedSessions = data.sessions.sort((a, b) => {
                const timeA = a.created_at || a.timestamp || 0;
                const timeB = b.created_at || b.timestamp || 0;
                return timeB - timeA; // Descending order (newest first)
            });
            
            window.allTestSessions = sortedSessions;
            populateModuleFilter(sortedSessions);
            populateModulesList(sortedSessions);
            displayTestCases(sortedSessions);
            updateDashboardFromTestSuite(sortedSessions);
        }
    } catch (error) {
        console.error('Error loading test cases:', error);
    }
}

function populateModuleFilter(sessions) {
    const moduleFilter = document.getElementById('moduleFilter');
    
    if (!moduleFilter) {
        return;
    }
    
    const modules = new Set();
    
    sessions.forEach(session => {
        if (session.module) {
            modules.add(session.module);
        }
    });
    
    moduleFilter.innerHTML = '<option value="">All Modules</option>';
    
    Array.from(modules).sort().forEach(module => {
        const option = document.createElement('option');
        option.value = module;
        option.textContent = module;
        moduleFilter.appendChild(option);
    });
}

function populateModulesList(sessions) {
    const modulesList = document.getElementById('moduleFilter');
    
    if (!modulesList) {
        return;
    }
    
    const modules = new Set();
    
    sessions.forEach(session => {
        if (session.module) {
            modules.add(session.module);
        }
    });
    
    // Clear existing options (keep the "All Modules" option)
    while (modulesList.options.length > 1) {
        modulesList.remove(1);
    }
    
    Array.from(modules).sort().forEach(module => {
        const option = document.createElement('option');
        option.value = module;
        option.textContent = module;
        modulesList.appendChild(option);
    });
}

function filterTestsByModule() {
    const selectedModule = document.getElementById('moduleFilter').value;
    
    if (!window.allTestSessions) {
        return;
    }
    
    let filteredSessions = window.allTestSessions;
    
    if (selectedModule) {
        filteredSessions = window.allTestSessions.filter(session => 
            session.module === selectedModule
        );
    }
    
    displayTestCases(filteredSessions);
}

function displayTestCases(sessions) {
    const listDiv = document.getElementById('testCasesList');
    
    if (!listDiv) {
        return;
    }
    
    if (sessions.length === 0) {
        listDiv.innerHTML = '<div style="padding: 20px; text-align: center; color: var(--text-secondary);">No test cases yet. Use the Recorder tab to create your first test!</div>';
        return;
    }
    
    let html = '';
    sessions.forEach(session => {
        const date = new Date(session.created_at * 1000).toLocaleString();
        const moduleTag = session.module ? `<span style="background: linear-gradient(135deg, #667eea 0%, #764ba2 100%); color: white; padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">📁 ${session.module}</span>` : '';
        
        html += `
            <div class="test-case-card" data-test-id="${session.id}" style="padding: 15px; margin-bottom: 10px; background: var(--stat-bg); border: 2px solid var(--border-color); border-radius: 8px;">
                <div style="display: flex; align-items: start; gap: 12px;">
                    <input type="checkbox" class="test-checkbox" data-test-id="${session.id}" onchange="updateDeleteTestsButton()" style="cursor: pointer; width: 18px; height: 18px; margin-top: 3px;">
                    <div style="flex: 1;">
                        <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 8px;">
                            <h4 style="color: #667eea; margin: 0;">${session.name}</h4>
                            ${moduleTag}
                        </div>
                        <div style="font-size: 0.9em; color: var(--text-secondary); margin-bottom: 8px;">
                            <div>📅 Created: ${date}</div>
                            <div>🌐 URL: ${session.url}</div>
                            <div>📊 Actions: ${session.action_count}</div>
                        </div>
                        <div style="display: flex; gap: 8px;">
                            <button class="btn" onclick="viewTestCase('${session.id}')" style="padding: 8px 16px; font-size: 14px;">
                                👁️ View Code
                            </button>
                            <button class="btn" onclick="showDataOverrideModal('${session.id}')" style="padding: 8px 16px; font-size: 14px; background: #10b981;">
                                ▶️ Execute
                            </button>
                            <button class="btn" onclick="deleteSingleTest('${session.id}')" style="padding: 8px 16px; font-size: 14px; background: #ef4444;">
                                🗑️ Delete
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        `;
    });
    
    listDiv.innerHTML = html;
}

async function viewTestCase(sessionId) {
    try {
        const response = await fetch(`${API_URL}/recorder/generate-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId, test_name: 'GeneratedTest' })
        });
        
        const data = await response.json();
        
        if (data.success) {
            displayTestSuiteCode(data.code, sessionId);
        }
    } catch (error) {
        console.error('Error loading test case:', error);
        alert('Error loading test case: ' + error.message);
    }
}

function displayTestSuiteCode(code, sessionId) {
    const codeElement = document.getElementById('testSuiteCodeContent');
    codeElement.textContent = code;
    
    window.currentTestSuiteSessionId = sessionId;
    window.currentTestSuiteCode = code;
    
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    codeElement.className = `language-${language}`;
    
    if (typeof Prism !== 'undefined') {
        Prism.highlightElement(codeElement);
    }
    
    document.getElementById('copyTestSuiteBtn').style.display = 'block';
    document.getElementById('exportTestSuiteBtn').style.display = 'block';
    document.getElementById('saveTestSuiteSnippetBtn').style.display = 'block';
}

function copyTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('✅ Code copied to clipboard!');
    });
}

function exportTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    
    let extension = '.java';
    if (code.includes('from selenium') || code.includes('import pytest')) {
        extension = '.py';
    } else if (code.includes('const ') || code.includes('let ')) {
        extension = '.js';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        extension = '.cs';
    }
    
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `TestSuite_${Date.now()}${extension}`;
    a.click();
    
    showNotification('✅ Code exported successfully!');
}

function saveTestSuiteSnippet() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    
    if (!code || code === 'Select a test case from the list to view its code here...') {
        alert('No code to save. Please select a test case first.');
        return;
    }
    
    // Detect language
    let language = 'java';
    if (code.includes('from selenium') || code.includes('import pytest') || code.includes('def ')) {
        language = 'python';
    } else if (code.includes('const ') || code.includes('let ') || code.includes('function ')) {
        language = 'javascript';
    } else if (code.includes('using ') || code.includes('namespace ')) {
        language = 'csharp';
    }
    
    const title = prompt('Enter a title for this snippet:', 'Test Suite Code');
    if (!title) return;
    
    const description = prompt('Enter a description (optional):', 'Generated test suite code');
    const tags = prompt('Enter tags (comma-separated, optional):', 'test-suite, automated');
    
    const snippet = {
        id: Date.now(),
        title: title,
        language: language,
        tags: tags ? tags.split(',').map(t => t.trim()) : [],
        description: description || '',
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    // Load existing snippets from localStorage
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    
    // Save to localStorage
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    showNotification('✅ Snippet saved to Code Snippet Library!');
    
    // Reload snippets if on that page
    if (typeof loadSnippets === 'function') {
        loadSnippets();
    }
}

function toggleSelectAllTests() {
    const selectAll = document.getElementById('selectAllTests');
    const checkboxes = document.querySelectorAll('.test-checkbox');
    
    checkboxes.forEach(cb => {
        cb.checked = selectAll.checked;
    });
    
    updateDeleteTestsButton();
}

function updateDeleteTestsButton() {
    const checkboxes = document.querySelectorAll('.test-checkbox');
    const checkedBoxes = Array.from(checkboxes).filter(cb => cb.checked);
    const deleteBtn = document.getElementById('deleteSelectedTestsBtn');
    const selectAll = document.getElementById('selectAllTests');
    
    if (checkedBoxes.length > 0) {
        deleteBtn.style.display = 'block';
        deleteBtn.textContent = `🗑️ Delete Selected (${checkedBoxes.length})`;
    } else {
        deleteBtn.style.display = 'none';
    }
    
    if (checkedBoxes.length === 0) {
        selectAll.checked = false;
        selectAll.indeterminate = false;
    } else if (checkedBoxes.length === checkboxes.length) {
        selectAll.checked = true;
        selectAll.indeterminate = false;
    } else {
        selectAll.checked = false;
        selectAll.indeterminate = true;
    }
}

async function deleteSelectedTests() {
    const checkboxes = document.querySelectorAll('.test-checkbox:checked');
    const selectedIds = Array.from(checkboxes).map(cb => cb.dataset.testId);
    
    if (selectedIds.length === 0) {
        return;
    }
    
    if (!confirm(`Are you sure you want to delete ${selectedIds.length} test case(s)?`)) {
        return;
    }
    
    let deletedCount = 0;
    let failedCount = 0;
    
    for (const sessionId of selectedIds) {
        try {
            const response = await fetch(`${API_URL}/recorder/delete-session`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ session_id: sessionId })
            });
            
            const data = await response.json();
            
            if (data.success) {
                deletedCount++;
            } else {
                failedCount++;
            }
        } catch (error) {
            failedCount++;
            console.error('Delete error:', error);
        }
    }
    
    document.getElementById('selectAllTests').checked = false;
    document.getElementById('deleteSelectedTestsBtn').style.display = 'none';
    
    const codeElement = document.getElementById('testSuiteCodeContent');
    codeElement.textContent = 'Select a test case from the list to view its code here...';
    codeElement.className = 'language-java';
    document.getElementById('copyTestSuiteBtn').style.display = 'none';
    document.getElementById('exportTestSuiteBtn').style.display = 'none';
    document.getElementById('saveTestSuiteSnippetBtn').style.display = 'none';
    
    await loadTestCases();
    
    if (deletedCount > 0) {
        showNotification(`🗑️ ${deletedCount} test case(s) deleted successfully`);
    }
    if (failedCount > 0) {
        alert(`⚠️ Failed to delete ${failedCount} test case(s)`);
    }
}

async function deleteSingleTest(sessionId) {
    if (!confirm('Are you sure you want to delete this test case?')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/delete-session`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ session_id: sessionId })
        });
        
        const data = await response.json();
        
        if (data.success) {
            if (window.currentTestSuiteSessionId === sessionId) {
                const codeElement = document.getElementById('testSuiteCodeContent');
                codeElement.textContent = 'Select a test case from the list to view its code here...';
                codeElement.className = 'language-java';
                document.getElementById('copyTestSuiteBtn').style.display = 'none';
                document.getElementById('exportTestSuiteBtn').style.display = 'none';
                document.getElementById('saveTestSuiteSnippetBtn').style.display = 'none';
            }
            
            showNotification('🗑️ Test case deleted successfully');
            await loadTestCases();
        } else {
            alert('❌ Failed to delete test case: ' + data.error);
        }
    } catch (error) {
        console.error('Delete error:', error);
        alert('Error deleting test case: ' + error.message);
    }
}

function updateDashboardFromTestSuite(sessions) {
    const totalTests = sessions.length;
    
    console.log('[Test Suite] 📊 Updating dashboard with', totalTests, 'tests');
    
    // Update the global stats object directly
    if (typeof window.stats !== 'undefined') {
        console.log('[Test Suite] 📝 Before update - window.stats.totalRequests:', window.stats.totalRequests);
        
        // Update total requests on the SAME object reference
        window.stats.totalRequests = totalTests;
        
        console.log('[Test Suite] ✏️ After update - window.stats.totalRequests:', window.stats.totalRequests);
        console.log('[Test Suite] 📦 Full window.stats:', JSON.stringify(window.stats));
        
        // Save to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
            
            // Verify the save
            const savedData = localStorage.getItem('dashboardStats');
            if (savedData) {
                const parsed = JSON.parse(savedData);
                console.log('[Test Suite] ✅ VERIFIED Save - totalRequests in localStorage:', parsed.totalRequests);
            }
        }
        
        // Update the dashboard UI if on dashboard page
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
    } else {
        console.error('[Test Suite] ❌ window.stats is undefined!');
    }
    
    // Directly update dashboard element if it exists (backup for immediate update)
    const dashboardTotalEl = document.getElementById('dashboardTotalRequests');
    if (dashboardTotalEl) {
        dashboardTotalEl.textContent = totalTests;
        console.log('[Test Suite] 🖥️ Updated dashboardTotalRequests element to:', totalTests);
    }
}

function updateDashboardWithExecutionResults(suiteData) {
    // Update test results with execution status
    if (typeof window.stats !== 'undefined' && suiteData.results) {
        suiteData.results.forEach(result => {
            let testResult = window.stats.testResults.find(r => r.name === result.test_name);
            
            if (testResult) {
                testResult.status = result.passed ? 'passed' : 'failed';
                testResult.details = result.passed ? 
                    `Executed ${result.steps_executed}/${result.total_steps} steps successfully` :
                    `Failed at step ${result.steps_executed}/${result.total_steps}${result.error ? ': ' + result.error : ''}`;
                testResult.timestamp = new Date().toLocaleString();
            } else {
                window.stats.testResults.unshift({
                    name: result.test_name,
                    status: result.passed ? 'passed' : 'failed',
                    duration: 0,
                    details: result.passed ? 
                        `Executed ${result.steps_executed}/${result.total_steps} steps successfully` :
                        `Failed at step ${result.steps_executed}/${result.total_steps}${result.error ? ': ' + result.error : ''}`,
                    timestamp: new Date().toLocaleString()
                });
            }
        });
        
        if (window.stats.testResults.length > 10) {
            window.stats.testResults = window.stats.testResults.slice(0, 10);
        }
        
        // Save stats to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
        }
        
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
        if (typeof window.updateRecentTestResults === 'function') {
            window.updateRecentTestResults();
        }
        if (typeof window.updateActivityTimeline === 'function') {
            window.updateActivityTimeline();
        }
    }
}

async function executeTestSuite() {
    const resultsDiv = document.getElementById('executionResults');
    const resultsList = document.getElementById('executionResultsList');
    const currentlyExecutingDiv = document.getElementById('currentlyExecutingTest');
    const currentExecutingTestName = document.getElementById('currentExecutingTestName');
    const selectedModule = document.getElementById('moduleFilter').value;
    
    if (!resultsDiv || !resultsList) {
        showNotification('⚠️ Test execution UI not found');
        return;
    }
    
    resultsDiv.style.display = 'block';
    if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'block';
    
    if (selectedModule) {
        resultsList.innerHTML = `<div style="color: #f59e0b;">⏳ Executing tests from module: ${selectedModule}...</div>`;
        if (currentExecutingTestName) currentExecutingTestName.textContent = `Module: ${selectedModule}`;
    } else {
        resultsList.innerHTML = '<div style="color: #f59e0b;">⏳ Executing all test cases...</div>';
        if (currentExecutingTestName) currentExecutingTestName.textContent = 'Test Suite';
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (!data.success || data.sessions.length === 0) {
            resultsList.innerHTML = '<div style="color: #ef4444;">❌ No test cases to execute</div>';
            if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
            return;
        }
        
        let sessionsToExecute = data.sessions;
        if (selectedModule) {
            sessionsToExecute = data.sessions.filter(s => s.module === selectedModule);
            
            if (sessionsToExecute.length === 0) {
                resultsList.innerHTML = `<div style="color: #ef4444;">❌ No test cases found in module: ${selectedModule}</div>`;
                if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
                return;
            }
        }
        
        const suiteResponse = await fetch(`${API_URL}/recorder/execute-suite`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ module: selectedModule || null })
        });
        
        const suiteData = await suiteResponse.json();
        
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        
        if (suiteData.success) {
            let html = `
                <div style="margin-bottom: 15px; padding: 10px; background: ${suiteData.all_passed ? '#d1fae5' : '#fee2e2'}; border-radius: 6px;">
                    <div style="font-weight: bold; font-size: 1.1em; color: ${suiteData.all_passed ? '#065f46' : '#991b1b'};">
                        ${suiteData.all_passed ? '✅ All Tests Passed' : '⚠️ Some Tests Failed'}
                    </div>
                    <div style="margin-top: 5px; color: ${suiteData.all_passed ? '#047857' : '#7f1d1d'};">
                        Passed: ${suiteData.passed_count} / ${suiteData.total_count}
                    </div>
                </div>
            `;
            
            suiteData.results.forEach(result => {
                html += `
                    <div style="padding: 10px; margin-bottom: 10px; background: ${result.passed ? '#d1fae5' : '#fee2e2'}; border-radius: 6px; border-left: 4px solid ${result.passed ? '#10b981' : '#ef4444'};">
                        <div style="font-weight: bold; color: ${result.passed ? '#065f46' : '#991b1b'};">
                            ${result.passed ? '✅' : '❌'} ${result.test_name}
                        </div>
                        <div style="font-size: 0.9em; color: #374151; margin-top: 5px;">
                            Steps: ${result.steps_executed} / ${result.total_steps}
                        </div>
                        ${result.error ? `<div style="font-size: 0.9em; color: #991b1b; margin-top: 5px;">Error: ${result.error}</div>` : ''}
                    </div>
                `;
            });
            
            resultsList.innerHTML = html;
            updateDashboardWithExecutionResults(suiteData);
        } else {
            resultsList.innerHTML = `<div style="color: #ef4444;">❌ Suite execution failed: ${suiteData.error}</div>`;
        }
    } catch (error) {
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        resultsList.innerHTML = `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
    }
}

async function clearTestSuite() {
    if (!confirm('Are you sure you want to clear all test cases? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/clear-sessions`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.success) {
            alert('✅ All test cases cleared successfully');
            loadTestCases();
            
            const executionResults = document.getElementById('executionResults');
            if (executionResults) executionResults.style.display = 'none';
            
            // Reset dashboard metrics
            const dashboardTotalEl = document.getElementById('dashboardTotalRequests');
            if (dashboardTotalEl) dashboardTotalEl.textContent = '0';
            
            if (typeof window.stats !== 'undefined') {
                window.stats.testResults = [];
                if (typeof window.updateRecentTestResults === 'function') window.updateRecentTestResults();
                if (typeof window.updateActivityTimeline === 'function') window.updateActivityTimeline();
            }
        } else {
            alert('❌ Failed to clear test cases: ' + data.error);
        }
    } catch (error) {
        alert('❌ Error: ' + error.message);
    }
}

async function showDataOverrideModal(sessionId) {
    try {
        const response = await fetch(`${API_URL}/recorder/sessions`);
        const data = await response.json();
        
        if (!data.success) {
            executeTestCase(sessionId, {});
            return;
        }
        
        const session = data.sessions.find(s => s.id === sessionId);
        if (!session) {
            executeTestCase(sessionId, {});
            return;
        }
        
        const inputActions = session.actions.filter(a => 
            a.action_type === 'input' || 
            a.action_type === 'click_and_input' || 
            a.action_type === 'select'
        );
        
        if (inputActions.length === 0) {
            executeTestCase(sessionId, {});
            return;
        }
        
        const modal = document.createElement('div');
        modal.id = 'dataOverrideModal';
        modal.style.cssText = 'position: fixed; top: 0; left: 0; width: 100%; height: 100%; background: rgba(0, 0, 0, 0.7); display: flex; align-items: center; justify-content: center; z-index: 10000;';
        
        let formFields = '';
        inputActions.forEach((action, index) => {
            const elementName = action.element.id || action.element.name || action.element.tagName || `Element ${index + 1}`;
            const actionType = action.action_type === 'select' ? 'Select' : 'Input';
            const stepLabel = `Step ${action.step}`;
            
            formFields += `
                <div style="margin-bottom: 20px; padding: 15px; background: #f9fafb; border-radius: 8px; border: 1px solid #e5e7eb;">
                    <label style="display: block; margin-bottom: 8px; color: #111827; font-weight: 600; font-size: 14px;">
                        ${stepLabel}: ${actionType} - ${elementName}
                    </label>
                    <input 
                        type="text" 
                        id="override_${index}" 
                        data-step="${action.step}"
                        placeholder="Enter new value or leave unchanged"
                        value="${action.value || ''}"
                        style="width: 100%; padding: 12px; border: 2px solid #d1d5db; border-radius: 6px; font-size: 14px; font-family: inherit; transition: border-color 0.2s;"
                        onfocus="this.style.borderColor='#667eea'; this.style.outline='none';"
                        onblur="this.style.borderColor='#d1d5db';"
                    />
                    <div style="font-size: 12px; color: #6b7280; margin-top: 6px; font-style: italic;">
                        📝 Original value: "${action.value || 'N/A'}"
                    </div>
                </div>
            `;
        });
        
        modal.innerHTML = `
            <div style="background: white; padding: 35px; border-radius: 16px; max-width: 650px; width: 90%; max-height: 85vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);">
                <h3 style="margin-top: 0; color: #667eea; margin-bottom: 10px; font-size: 24px;">
                    🔧 Override Test Data
                </h3>
                <p style="color: #6b7280; margin-bottom: 20px; font-size: 14px;">
                    Modify the input values below to run the test with different data
                </p>
                <div style="margin-bottom: 25px; padding: 14px; background: #eff6ff; border-left: 4px solid #3b82f6; border-radius: 6px;">
                    <div style="font-size: 14px; color: #1e40af; line-height: 1.5;">
                        💡 <strong>Tip:</strong> Leave fields unchanged to use recorded values, or enter new data to override them during execution.
                    </div>
                </div>
                <form id="dataOverrideForm">
                    <div style="max-height: 400px; overflow-y: auto; padding-right: 10px;">
                        ${formFields}
                    </div>
                    <div style="display: flex; gap: 12px; margin-top: 25px; padding-top: 20px; border-top: 2px solid #e5e7eb;">
                        <button type="submit" class="btn" style="flex: 1; background: linear-gradient(135deg, #10b981 0%, #059669 100%); padding: 14px; font-size: 15px; font-weight: 600; box-shadow: 0 4px 12px rgba(16,185,129,0.3);">
                            ▶️ Execute with Data
                        </button>
                        <button type="button" onclick="closeDataOverrideModal()" class="btn" style="flex: 1; background: #6b7280; padding: 14px; font-size: 15px; font-weight: 600;">
                            ❌ Cancel
                        </button>
                    </div>
                </form>
            </div>
        `;
        
        document.body.appendChild(modal);
        
        document.getElementById('dataOverrideForm').addEventListener('submit', (e) => {
            e.preventDefault();
            
            const overrides = {};
            inputActions.forEach((action, index) => {
                const input = document.getElementById(`override_${index}`);
                const newValue = input.value.trim();
                
                if (newValue !== action.value) {
                    overrides[action.step] = newValue;
                }
            });
            
            closeDataOverrideModal();
            executeTestCase(sessionId, overrides);
        });
        
    } catch (error) {
        console.error('Error showing data override modal:', error);
        executeTestCase(sessionId, {});
    }
}

function closeDataOverrideModal() {
    const modal = document.getElementById('dataOverrideModal');
    if (modal) {
        modal.remove();
    }
}

async function executeTestCase(sessionId, dataOverrides = {}) {
    // Prevent double execution
    if (window.isExecutingTest) {
        console.log('[Test Suite] ⚠️ Test already executing, ignoring duplicate call');
        return;
    }
    window.isExecutingTest = true;
    
    // Close any sticky popup before executing test
    const stickyPopup = document.getElementById('sticky-close');
    if (stickyPopup) {
        stickyPopup.style.display = 'none';
        stickyPopup.remove();
    }
    
    const resultsDiv = document.getElementById('executionResults');
    const resultsList = document.getElementById('executionResultsList');
    const currentlyExecutingDiv = document.getElementById('currentlyExecutingTest');
    const currentExecutingTestName = document.getElementById('currentExecutingTestName');
    
    if (!resultsDiv || !resultsList) {
        window.isExecutingTest = false;
        showNotification('⚠️ Test execution UI not found');
        return;
    }
    
    resultsDiv.style.display = 'block';
    if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'block';
    
    try {
        const sessionsResponse = await fetch(`${API_URL}/recorder/sessions`);
        const sessionsData = await sessionsResponse.json();
        const sessionData = sessionsData.sessions.find(s => s.id === sessionId);
        if (sessionData && currentExecutingTestName) {
            currentExecutingTestName.textContent = sessionData.name;
        } else if (currentExecutingTestName) {
            currentExecutingTestName.textContent = 'Test Case';
        }
    } catch (e) {
        if (currentExecutingTestName) currentExecutingTestName.textContent = 'Test Case';
    }
    
    resultsList.innerHTML = '<div style="color: #f59e0b;">⏳ Executing test case...</div>';
    
    try {
        const response = await fetch(`${API_URL}/recorder/execute-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                data_overrides: dataOverrides
            })
        });
        
        const data = await response.json();
        
        console.log('[Test Suite] 🎯 RAW RESPONSE:', JSON.stringify(data, null, 2));
        console.log('[Test Suite] Response validation:', {
            hasSuccess: 'success' in data,
            hasPassed: 'passed' in data,
            hasTestName: 'test_name' in data,
            hasDuration: 'duration' in data,
            successValue: data.success,
            passedValue: data.passed,
            durationValue: data.duration
        });
        
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        
        // CRITICAL: Record test results for BOTH passed and failed tests
        if (data.success !== undefined && ('passed' in data || data.error)) {
            const result = `
                <div style="padding: 10px; margin-bottom: 10px; background: ${data.passed ? '#d1fae5' : '#fee2e2'}; border-radius: 6px; border-left: 4px solid ${data.passed ? '#10b981' : '#ef4444'};">
                    <div style="font-weight: bold; color: ${data.passed ? '#065f46' : '#991b1b'};">
                        ${data.passed ? '✅ Test Passed' : '❌ Test Failed'}
                    </div>
                    ${data.is_edited_code ? '<div style="font-size: 0.9em; color: #8b5cf6; margin-top: 5px; font-weight: bold;">⚡ Executed edited code</div>' : `<div style="font-size: 0.9em; color: #374151; margin-top: 5px;">Steps executed: ${data.steps_executed} / ${data.total_steps}</div>`}
                    ${Object.keys(dataOverrides).length > 0 ? '<div style="font-size: 0.9em; color: #3b82f6; margin-top: 5px;">🔧 Executed with overridden data</div>' : ''}
                    ${data.output ? `<details style="margin-top: 10px;"><summary style="cursor: pointer; color: #6b7280; font-size: 0.9em;">📋 View Output</summary><pre style="background: #1f2937; color: #e5e7eb; padding: 10px; border-radius: 4px; overflow-x: auto; margin-top: 5px; font-size: 0.85em;">${data.output}</pre></details>` : ''}
                    ${data.error && !data.output ? `<div style="font-size: 0.9em; color: #991b1b; margin-top: 5px;">Error: ${data.error}</div>` : ''}
                </div>
            `;
            resultsList.innerHTML = result;
            
            // Update dashboard with test result (for both passed and failed tests)
            const isPassed = data.passed === true;
            const testName = data.test_name || 'Test Case';
            const duration = data.duration || 0;
            
            console.log('[Test Suite] 📈 Processing test result:', {
                passed: isPassed,
                test_name: testName,
                duration: duration,
                steps: data.steps_executed ? `${data.steps_executed}/${data.total_steps}` : 'N/A',
                hasError: !!data.error,
                timestamp: new Date().toISOString()
            });
            
            if (typeof addTestResult === 'function') {
                const details = isPassed ? 
                    `Executed ${data.steps_executed || 0}/${data.total_steps || 0} steps successfully` :
                    `Failed${data.step ? ' at step ' + data.step : ''}${data.error ? ': ' + data.error.substring(0, 100) : ''}`;
                
                console.log('[Test Suite] 📞 CALLING addTestResult NOW:', { testName, status: isPassed ? 'passed' : 'failed', duration, details });
                
                // Call addTestResult
                addTestResult(testName, isPassed ? 'passed' : 'failed', duration, details);
                
                console.log('[Test Suite] ✅ addTestResult called - waiting 200ms for save...');
                
                // Force dashboard update after a delay to ensure save completed
                setTimeout(() => {
                    console.log('[Test Suite] 🔄 Forcing dashboard update NOW');
                    if (typeof updateDashboardStats === 'function') {
                        updateDashboardStats();
                    }
                    // Double-check localStorage
                    const stats = localStorage.getItem('dashboardStats');
                    console.log('[Test Suite] 📊 Dashboard stats after update:', stats ? JSON.parse(stats) : 'NO DATA');
                }, 200);
            } else {
                console.error('[Test Suite] ❌ CRITICAL: addTestResult function not found!');
                console.log('[Test Suite] Available window functions:', Object.keys(window).filter(k => k.includes('Test') || k.includes('Dashboard')));
            }
        } else {
            const errorHtml = `
                <div style="color: #ef4444; padding: 10px; background: #fee2e2; border-radius: 6px; border-left: 4px solid #ef4444;">
                    <div style="font-weight: bold;">❌ Execution failed</div>
                    <div style="margin-top: 5px; font-size: 0.9em;">${data.error}</div>
                    ${data.hint ? `<div style="margin-top: 8px; padding: 8px; background: #fef3c7; color: #92400e; border-radius: 4px; font-size: 0.9em;">💡 Hint: ${data.hint}</div>` : ''}
                </div>
            `;
            resultsList.innerHTML = errorHtml;
        }
    } catch (error) {
        if (currentlyExecutingDiv) currentlyExecutingDiv.style.display = 'none';
        resultsList.innerHTML = `<div style="color: #ef4444;">❌ Error: ${error.message}</div>`;
    } finally {
        // Reset execution flag
        window.isExecutingTest = false;
    }
}

async function executeCurrentTest() {
    alert('This will execute the currently displayed test code. Feature coming soon!');
}

function editTestSuiteCode() {
    const code = document.getElementById('testSuiteCodeContent').textContent;
    const editArea = document.getElementById('testSuiteCodeEditArea');
    const editor = document.getElementById('testSuiteCodeEditor');
    const viewer = document.getElementById('testSuiteCodeViewer');
    
    if (!editArea || !editor || !viewer) {
        showNotification('⚠️ Edit UI not found');
        return;
    }
    
    editArea.value = code;
    viewer.style.display = 'none';
    editor.style.display = 'block';
}

async function saveEditedTestCode() {
    const editedCode = document.getElementById('testSuiteCodeEditArea').value;
    const sessionId = window.currentTestSuiteSessionId;
    
    if (!sessionId) {
        alert('No test case selected to save');
        return;
    }
    
    if (typeof showLoading === 'function') showLoading(true);
    
    try {
        const response = await fetch(`${API_URL}/recorder/update-test-code`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ 
                session_id: sessionId,
                code: editedCode
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            window.currentTestSuiteCode = editedCode;
            displayTestSuiteCode(editedCode, sessionId);
            cancelEditTestCode();
            alert('✅ Test code updated successfully!');
        } else {
            alert('❌ Failed to save: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error saving test code: ' + error.message);
    } finally {
        if (typeof showLoading === 'function') showLoading(false);
    }
}

function cancelEditTestCode() {
    const editor = document.getElementById('testSuiteCodeEditor');
    const viewer = document.getElementById('testSuiteCodeViewer');
    
    if (editor && viewer) {
        editor.style.display = 'none';
        viewer.style.display = 'block';
    }
}

// Expose functions to window object
window.loadTestCases = loadTestCases;
window.viewTestCase = viewTestCase;
window.displayTestCases = displayTestCases;
window.displayTestSuiteCode = displayTestSuiteCode;
window.filterTestsByModule = filterTestsByModule;
window.populateModuleFilter = populateModuleFilter;
window.populateModulesList = populateModulesList;
window.toggleSelectAllTests = toggleSelectAllTests;
window.updateDeleteTestsButton = updateDeleteTestsButton;
window.deleteSelectedTests = deleteSelectedTests;
window.deleteSingleTest = deleteSingleTest;
window.copyTestSuiteCode = copyTestSuiteCode;
window.exportTestSuiteCode = exportTestSuiteCode;
window.executeTestSuite = executeTestSuite;
window.clearTestSuite = clearTestSuite;
window.showDataOverrideModal = showDataOverrideModal;
window.closeDataOverrideModal = closeDataOverrideModal;
window.executeTestCase = executeTestCase;
window.executeCurrentTest = executeCurrentTest;
window.editTestSuiteCode = editTestSuiteCode;
window.saveEditedTestCode = saveEditedTestCode;
window.cancelEditTestCode = cancelEditTestCode;
window.saveTestSuiteSnippet = saveTestSuiteSnippet;
window.updateDashboardFromTestSuite = updateDashboardFromTestSuite;
window.updateDashboardWithExecutionResults = updateDashboardWithExecutionResults;
