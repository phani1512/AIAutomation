// Test Suite Management Functions

let testCases = [];
let currentEditingTest = null;

async function loadTestCases() {
    try {
        const sessions = await fetch(`${window.API_URL}/recorder/sessions`);
        const data = await sessions.json();
        
        if (data.sessions) {
            testCases = data.sessions;
            updateTestCasesList();
            updateDashboardFromTestSuite(data.sessions);
        }
    } catch (error) {
        console.error('Error loading test cases:', error);
    }
}

function updateTestCasesList() {
    const container = document.getElementById('testCasesList');
    
    if (testCases.length === 0) {
        container.innerHTML = `
            <div style="text-align: center; padding: 60px 20px; color: var(--text-secondary);">
                <div style="font-size: 3em; margin-bottom: 15px;">📝</div>
                <h3 style="color: var(--text-primary); margin-bottom: 10px;">No Test Cases Yet</h3>
                <p>Add test cases from the Test Recorder or manually</p>
            </div>
        `;
        return;
    }
    
    container.innerHTML = testCases.map((test, index) => {
        const status = test.status || 'pending';
        const statusIcons = {
            passed: '✅',
            failed: '❌',
            pending: '⏳',
            running: '🔄'
        };
        const statusColors = {
            passed: 'var(--success)',
            failed: 'var(--error)',
            pending: 'var(--text-secondary)',
            running: 'var(--info)'
        };
        
        return `
            <div style="background: var(--bg-secondary); padding: 20px; border-radius: 8px; margin-bottom: 15px;">
                <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                    <div style="flex: 1;">
                        <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                            <span style="font-size: 1.2em;">${statusIcons[status]}</span>
                            <h4 style="color: var(--text-primary); margin: 0;">${test.name || `Test Case ${index + 1}`}</h4>
                            <span style="background: ${statusColors[status]}; color: white; padding: 3px 10px; border-radius: 12px; font-size: 0.85em;">
                                ${status}
                            </span>
                        </div>
                        ${test.description ? `
                            <p style="color: var(--text-secondary); margin: 0 0 10px 0;">${test.description}</p>
                        ` : ''}
                        <div style="color: var(--text-secondary); font-size: 0.9em;">
                            Actions: ${test.actions ? test.actions.length : 0} | 
                            Created: ${test.timestamp ? new Date(test.timestamp).toLocaleDateString() : 'Unknown'}
                        </div>
                    </div>
                    <div style="display: flex; gap: 8px;">
                        <button onclick="viewTestCase('${test.id}')" style="background: var(--accent); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
                            👁️ View
                        </button>
                        <button onclick="editTestCase('${test.id}')" style="background: var(--info); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
                            ✏️ Edit
                        </button>
                        <button onclick="deleteTestCase('${test.id}')" style="background: var(--error); color: white; border: none; padding: 8px 16px; border-radius: 6px; cursor: pointer;">
                            🗑️
                        </button>
                    </div>
                </div>
                
                ${test.lastRun ? `
                    <div style="padding-top: 15px; border-top: 1px solid var(--border);">
                        <div style="color: var(--text-secondary); font-size: 0.9em;">
                            Last run: ${new Date(test.lastRun).toLocaleString()} 
                            ${test.duration ? `| Duration: ${test.duration}ms` : ''}
                        </div>
                    </div>
                ` : ''}
            </div>
        `;
    }).join('');
}

function viewTestCase(testId) {
    const test = testCases.find(t => t.id === testId);
    if (!test) return;
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">👁️ ${test.name || 'Test Case'}</h3>
            
            ${test.description ? `
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--text-primary);">Description:</strong>
                    <p style="color: var(--text-secondary); margin: 8px 0 0 0;">${test.description}</p>
                </div>
            ` : ''}
            
            <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                <strong style="color: var(--text-primary); display: block; margin-bottom: 10px;">Actions (${test.actions ? test.actions.length : 0}):</strong>
                <div style="max-height: 300px; overflow-y: auto;">
                    ${test.actions && test.actions.length > 0 ? test.actions.map((action, idx) => `
                        <div style="padding: 10px; margin-bottom: 8px; background: var(--bg-tertiary); border-radius: 6px;">
                            <div style="color: var(--text-primary); font-weight: bold; margin-bottom: 5px;">
                                ${idx + 1}. ${action.type || 'Action'}
                            </div>
                            ${action.element ? `
                                <div style="color: var(--text-secondary); font-size: 0.9em;">
                                    Element: ${action.element.tagName || 'Unknown'}
                                    ${action.element.id ? ` #${action.element.id}` : ''}
                                    ${action.element.className ? ` .${action.element.className}` : ''}
                                </div>
                            ` : ''}
                            ${action.value ? `
                                <div style="color: var(--text-secondary); font-size: 0.9em;">
                                    Value: ${action.value}
                                </div>
                            ` : ''}
                        </div>
                    `).join('') : '<div style="color: var(--text-secondary);">No actions recorded</div>'}
                </div>
            </div>
            
            ${test.code ? `
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 15px;">
                    <strong style="color: var(--text-primary); display: block; margin-bottom: 10px;">Generated Code:</strong>
                    <pre style="background: var(--bg-tertiary); padding: 15px; border-radius: 6px; overflow-x: auto; margin: 0;"><code>${test.code}</code></pre>
                </div>
            ` : ''}
            
            <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="width: 100%;">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

function editTestCase(testId) {
    const test = testCases.find(t => t.id === testId);
    if (!test) return;
    
    currentEditingTest = testId;
    
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">✏️ Edit Test Case</h3>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Test Name:</label>
                <input type="text" id="editTestName" value="${test.name || ''}" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Description:</label>
                <textarea id="editTestDescription" rows="3" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">${test.description || ''}</textarea>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button class="btn" onclick="saveTestCaseEdit()" style="flex: 1; background: var(--success);">
                    💾 Save Changes
                </button>
                <button class="btn" onclick="this.closest('.modal-overlay').remove(); currentEditingTest = null;" style="flex: 1;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function saveTestCaseEdit() {
    const name = document.getElementById('editTestName').value.trim();
    const description = document.getElementById('editTestDescription').value.trim();
    
    if (!name) {
        alert('Please enter a test name');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${window.API_URL}/test-suite/update`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                test_id: currentEditingTest,
                name: name,
                description: description
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'updated') {
            window.showNotification('✅ Test case updated!');
            loadTestCases();
            document.querySelector('.modal-overlay').remove();
            currentEditingTest = null;
        } else {
            throw new Error(data.error || 'Failed to update test case');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    }
}

async function deleteTestCase(testId) {
    if (!confirm('Are you sure you want to delete this test case?')) {
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${window.API_URL}/test-suite/delete`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ test_id: testId })
        });
        
        const data = await response.json();
        
        if (data.status === 'deleted') {
            window.showNotification('🗑️ Test case deleted');
            loadTestCases();
        } else {
            throw new Error(data.error || 'Failed to delete test case');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    }
}

async function executeTestSuite() {
    if (testCases.length === 0) {
        alert('No test cases to execute');
        return;
    }
    
    window.showLoading(true);
    
    try {
        const response = await authenticatedFetch(`${window.API_URL}/test-suite/execute`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        
        if (data.results) {
            displayTestSuiteResults(data.results);
            updateDashboardWithExecutionResults(data);
        } else {
            throw new Error(data.error || 'Failed to execute test suite');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

function displayTestSuiteResults(results) {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    const passed = results.filter(r => r.status === 'passed').length;
    const failed = results.filter(r => r.status === 'failed').length;
    const total = results.length;
    const passRate = total > 0 ? Math.round((passed / total) * 100) : 0;
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 800px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">📊 Test Suite Results</h3>
            
            <div style="display: grid; grid-template-columns: repeat(3, 1fr); gap: 15px; margin-bottom: 20px;">
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 2em; color: var(--success); margin-bottom: 5px;">${passed}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9em;">Passed</div>
                </div>
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 2em; color: var(--error); margin-bottom: 5px;">${failed}</div>
                    <div style="color: var(--text-secondary); font-size: 0.9em;">Failed</div>
                </div>
                <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; text-align: center;">
                    <div style="font-size: 2em; color: var(--accent); margin-bottom: 5px;">${passRate}%</div>
                    <div style="color: var(--text-secondary); font-size: 0.9em;">Pass Rate</div>
                </div>
            </div>
            
            <div style="max-height: 400px; overflow-y: auto;">
                ${results.map((result, idx) => `
                    <div style="background: var(--bg-secondary); padding: 15px; border-radius: 8px; margin-bottom: 10px; border-left: 4px solid ${result.status === 'passed' ? 'var(--success)' : 'var(--error)'};">
                        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 10px;">
                            <strong style="color: var(--text-primary);">${result.name || `Test ${idx + 1}`}</strong>
                            <span style="color: ${result.status === 'passed' ? 'var(--success)' : 'var(--error)'}; font-weight: bold;">
                                ${result.status === 'passed' ? '✅ PASSED' : '❌ FAILED'}
                            </span>
                        </div>
                        ${result.duration ? `
                            <div style="color: var(--text-secondary); font-size: 0.9em; margin-bottom: 5px;">
                                Duration: ${result.duration}ms
                            </div>
                        ` : ''}
                        ${result.error ? `
                            <div style="background: var(--error); color: white; padding: 10px; border-radius: 6px; margin-top: 10px; font-size: 0.9em;">
                                ${result.error}
                            </div>
                        ` : ''}
                    </div>
                `).join('')}
            </div>
            
            <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="margin-top: 20px; width: 100%;">
                Close
            </button>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function clearTestSuite() {
    if (testCases.length === 0) {
        return;
    }
    
    if (!confirm('Are you sure you want to delete ALL test cases? This cannot be undone.')) {
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${window.API_URL}/test-suite/clear`, {
            method: 'POST'
        });
        
        const data = await response.json();
        
        if (data.status === 'cleared') {
            window.showNotification('🗑️ All test cases deleted');
            testCases = [];
            updateTestCasesList();
        } else {
            throw new Error(data.error || 'Failed to clear test suite');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    }
}

function showAddTestModal() {
    const modal = document.createElement('div');
    modal.className = 'modal-overlay';
    
    modal.innerHTML = `
        <div class="modal-content" style="max-width: 600px;">
            <h3 style="color: var(--text-primary); margin-bottom: 20px;">➕ Add Test Case</h3>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Test Name:</label>
                <input type="text" id="newTestName" placeholder="e.g., Login Test" style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);">
            </div>
            
            <div style="margin-bottom: 15px;">
                <label style="display: block; color: var(--text-primary); margin-bottom: 5px;">Description:</label>
                <textarea id="newTestDescription" rows="3" placeholder="Describe what this test does..." style="width: 100%; padding: 10px; border: 1px solid var(--border); border-radius: 6px; background: var(--bg-secondary); color: var(--text-primary);"></textarea>
            </div>
            
            <div style="display: flex; gap: 10px;">
                <button class="btn" onclick="saveNewTestCase()" style="flex: 1; background: var(--success);">
                    💾 Save Test Case
                </button>
                <button class="btn" onclick="this.closest('.modal-overlay').remove()" style="flex: 1;">
                    Cancel
                </button>
            </div>
        </div>
    `;
    
    document.body.appendChild(modal);
}

async function saveNewTestCase() {
    const name = document.getElementById('newTestName').value.trim();
    const description = document.getElementById('newTestDescription').value.trim();
    
    if (!name) {
        alert('Please enter a test name');
        return;
    }
    
    try {
        const response = await authenticatedFetch(`${window.API_URL}/test-suite/add`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: name,
                description: description,
                actions: []
            })
        });
        
        const data = await response.json();
        
        if (data.status === 'added') {
            window.showNotification('✅ Test case added!');
            loadTestCases();
            document.querySelector('.modal-overlay').remove();
        } else {
            throw new Error(data.error || 'Failed to add test case');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    }
}

function deleteSelectedTests() {
    const checkboxes = document.querySelectorAll('.test-checkbox:checked');
    if (checkboxes.length === 0) {
        alert('No tests selected');
        return;
    }
    
    if (confirm(`Delete ${checkboxes.length} selected test(s)?`)) {
        checkboxes.forEach(cb => {
            const testId = cb.dataset.testId;
            if (testId && typeof deleteTestCase === 'function') {
                deleteTestCase(testId);
            }
        });
        window.showNotification(`✅ ${checkboxes.length} test(s) deleted!`);
    }
}

function copyTestSuiteCode() {
    const code = document.getElementById('testSuiteOutput')?.textContent || '';
    if (code) {
        navigator.clipboard.writeText(code).then(() => {
            window.showNotification('✅ Code copied to clipboard!');
        });
    }
}

function exportTestSuiteCode() {
    const code = document.getElementById('testSuiteOutput')?.textContent || '';
    if (code) {
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'test_suite.py';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        window.showNotification('✅ Test suite exported!');
    }
}

function saveTestSuiteSnippet() {
    const code = document.getElementById('testSuiteOutput')?.textContent || '';
    if (code && typeof window.showAddSnippetModal === 'function') {
        window.showAddSnippetModal(code);
    }
}

function saveEditedTestCode() {
    const output = document.getElementById('editTestOutput');
    const editor = document.getElementById('editTestEditor');
    const editorTextarea = document.getElementById('editTestEditorTextarea');
    
    if (output && editor && editorTextarea) {
        output.textContent = editorTextarea.value;
        output.style.display = 'block';
        editor.style.display = 'none';
        window.showNotification('✅ Changes saved!');
    }
}

function cancelEditTestCode() {
    const output = document.getElementById('editTestOutput');
    const editor = document.getElementById('editTestEditor');
    
    if (output && editor) {
        output.style.display = 'block';
        editor.style.display = 'none';
    }
}

// Expose functions to global scope for HTML onclick handlers
window.loadTestCases = loadTestCases;
window.updateTestCasesList = updateTestCasesList;
window.viewTestCase = viewTestCase;
window.editTestCase = editTestCase;
window.saveTestCaseEdit = saveTestCaseEdit;
window.deleteTestCase = deleteTestCase;
window.deleteSelectedTests = deleteSelectedTests;
window.executeTestSuite = executeTestSuite;
window.displayTestSuiteResults = displayTestSuiteResults;
window.clearTestSuite = clearTestSuite;
window.copyTestSuiteCode = copyTestSuiteCode;
window.exportTestSuiteCode = exportTestSuiteCode;
window.saveTestSuiteSnippet = saveTestSuiteSnippet;
window.saveEditedTestCode = saveEditedTestCode;
window.cancelEditTestCode = cancelEditTestCode;
window.showAddTestModal = showAddTestModal;
window.saveNewTestCase = saveNewTestCase;


