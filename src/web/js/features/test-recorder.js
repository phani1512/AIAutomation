// Test Recorder Features

let isRecording = false;
let currentSessionId = null;
let recordedActions = [];
let pollingIntervalId = null;

async function startRecording() {
    // Close any sticky popup before starting recording
    const stickyPopup = document.getElementById('sticky-close');
    if (stickyPopup) {
        stickyPopup.style.display = 'none';
        stickyPopup.remove();
    }
    
    const url = document.getElementById('recordingUrl').value;
    const testName = document.getElementById('recordingName').value || `Test_${Date.now()}`;
    const moduleName = document.getElementById('recordingModule').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    if (!moduleName) {
        alert('Please enter a module name');
        return;
    }
    
    console.log('Starting recording:', testName, 'at', url, 'Module:', moduleName);
    
    try {
        const response = await fetch(`${API_URL}/recorder/start`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: testName,
                url: url,
                module: moduleName
            })
        });
        
        const data = await response.json();
        console.log('Start response:', data);
        
        if (data.success) {
            currentSessionId = data.session_id;
            isRecording = true;
            recordedActions = [];
            
            document.getElementById('startRecordBtn').style.display = 'none';
            document.getElementById('stopRecordBtn').style.display = 'inline-block';
            document.getElementById('newTestBtn').style.display = 'none';
            
            showRecordingStatus(`🔴 Recording started! Session ID: ${currentSessionId.substring(0, 8)}...`);
            
            document.getElementById('recordedActionsContainer').style.display = 'block';
            updateRecordedActionsList();
            
            startPollingActions();
        } else {
            alert('Failed to start recording: ' + data.error);
        }
    } catch (error) {
        console.error('Error starting recording:', error);
        alert('Error starting recording: ' + error.message);
    }
}

function startPollingActions() {
    if (!currentSessionId || !isRecording) {
        console.log('Not polling - no session or not recording');
        return;
    }
    
    console.log('Starting to poll actions for session:', currentSessionId);
    
    const pollActions = async () => {
        if (!isRecording || !currentSessionId) {
            console.log('Stopping polling - recording stopped or no session');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/recorder/session/${currentSessionId}`);
            const data = await response.json();
            
            if (data.success && data.session) {
                const newActions = data.session.actions || [];
                
                if (newActions.length !== recordedActions.length) {
                    console.log(`Actions updated: ${recordedActions.length} -> ${newActions.length}`);
                    recordedActions = newActions;
                    updateRecordedActionsList();
                }
            }
        } catch (error) {
            console.error('Error polling actions:', error);
        }
        
        if (isRecording) {
            pollingIntervalId = setTimeout(pollActions, 1000);
        }
    };
    
    pollActions();
}

function updateRecordedActionsList() {
    const listElement = document.getElementById('recordedActionsList');
    
    if (recordedActions.length === 0) {
        listElement.innerHTML = '<div style="padding: 15px; color: var(--text-secondary); text-align: center;">No actions recorded yet. Interact with the webpage...</div>';
        return;
    }
    
    listElement.innerHTML = recordedActions.map((action, index) => {
        const icons = {
            'click': '🖱️',
            'input': '⌨️',
            'select': '📋',
            'navigate': '🌐',
            'click_and_input': '🖱️⌨️',
            'file_upload': '📁'
        };
        
        const icon = icons[action.action_type] || '✅';
        const elementInfo = action.element ? 
            (action.element.id || action.element.name || action.element.tagName || 'Unknown') : 
            'Page';
        
        return `
        <div style="padding: 10px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center;">
            <div>
                <span style="font-weight: 500;">${icon} ${action.action_type}</span>
                <span style="color: var(--text-secondary); margin-left: 10px;">${elementInfo}</span>
                ${action.value ? `<span style="color: var(--text-tertiary); margin-left: 5px;">= "${action.value}"</span>` : ''}
            </div>
            <span style="color: var(--text-tertiary); font-size: 0.85em;">Step ${action.step || index + 1}</span>
        </div>
        `;
    }).join('');
}

async function stopRecording() {
    if (!isRecording) {
        return;
    }
    
    console.log('Stopping recording for session:', currentSessionId);
    
    try {
        const response = await fetch(`${API_URL}/recorder/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        console.log('Stop response:', data);
        
        if (data.success) {
            if (pollingIntervalId) {
                clearTimeout(pollingIntervalId);
                pollingIntervalId = null;
            }
            
            isRecording = false;
            
            try {
                const sessionResponse = await fetch(`${API_URL}/recorder/session/${currentSessionId}`);
                const sessionData = await sessionResponse.json();
                if (sessionData.success) {
                    recordedActions = sessionData.session.actions;
                    updateRecordedActionsList();
                }
            } catch (err) {
                console.error('Error fetching final actions:', err);
            }
            
            document.getElementById('startRecordBtn').style.display = 'none';
            document.getElementById('stopRecordBtn').style.display = 'none';
            document.getElementById('newTestBtn').style.display = 'inline-block';
            
            showRecordingStatus('✅ Recording stopped. ' + recordedActions.length + ' actions captured. Click "Generate Test Code" to export.');
        } else {
            alert('Failed to stop recording: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error stopping recording:', error);
        alert('Error stopping recording: ' + error.message);
    }
}

async function startNewTestCase() {
    const url = document.getElementById('recordingUrl').value;
    const testName = document.getElementById('recordingName').value || `Test_${Date.now()}`;
    const moduleName = document.getElementById('recordingModule').value.trim();
    
    if (!url) {
        alert('Please enter a URL');
        return;
    }
    
    if (!moduleName) {
        alert('Please enter a module name');
        return;
    }
    
    try {
        const response = await fetch(`${API_URL}/recorder/new-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                name: testName,
                url: url,
                module: moduleName
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            currentSessionId = data.session_id;
            isRecording = true;
            recordedActions = [];
            
            document.getElementById('startRecordBtn').style.display = 'none';
            document.getElementById('stopRecordBtn').style.display = 'inline-block';
            document.getElementById('newTestBtn').style.display = 'none';
            
            showRecordingStatus(`🔴 New test case "${testName}" started! Recording in progress...`);
            
            document.getElementById('recordedActionsContainer').style.display = 'block';
            updateRecordedActionsList();
            
            startPollingActions();
        } else {
            alert('Failed to start new test case: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error starting new test case:', error);
        alert('Error starting new test case: ' + error.message);
    }
}

async function generateTestFromRecording() {
    if (!currentSessionId) {
        alert('No recording session active');
        return;
    }
    
    showLoading(true);
    
    try {
        const testName = document.getElementById('recordingName').value.replace(/\s+/g, '');
        const language = document.getElementById('codeLanguageSelector').value;
        
        const response = await fetch(`${API_URL}/recorder/generate-test`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: currentSessionId,
                test_name: testName,
                language: language
            })
        });
        
        const data = await response.json();
        
        if (data.success) {
            const recorderOutputCode = document.getElementById('recorderOutputCode');
            recorderOutputCode.textContent = data.code;
            recorderOutputCode.className = language === 'python' ? 'language-python' : 'language-java';
            
            if (typeof Prism !== 'undefined') {
                Prism.highlightElement(recorderOutputCode);
            }
            
            document.getElementById('editRecorderBtn').style.display = 'inline-block';
            document.getElementById('copyRecorderBtn').style.display = 'inline-block';
            document.getElementById('exportRecorderBtn').style.display = 'inline-block';
            document.getElementById('saveRecorderSnippetBtn').style.display = 'inline-block';
            
            window.lastRecorderCode = data.code;
            window.lastRecorderSessionId = currentSessionId;
            window.lastRecorderLanguage = language;
            
            document.getElementById('executeTestSection').style.display = 'block';
            showRecordingStatus(`✅ Test code generated successfully in ${language.toUpperCase()}!`);
            
            setTimeout(() => loadTestCases(), 500);
        } else {
            alert('Failed to generate test: ' + data.error);
        }
    } catch (error) {
        alert('Error generating test: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function showRecordingStatus(message) {
    const statusDiv = document.getElementById('recordingStatus');
    const statusText = document.getElementById('recordingStatusText');
    statusDiv.style.display = 'block';
    statusText.textContent = message;
}

function copyRecorderOutput() {
    const code = window.lastRecorderCode || document.getElementById('recorderOutputCode').textContent;
    navigator.clipboard.writeText(code).then(() => {
        showNotification('✅ Code copied to clipboard!');
    });
}

function exportRecorderCode() {
    const code = window.lastRecorderCode || document.getElementById('recorderOutputCode').textContent;
    const testName = document.getElementById('recordingName').value || 'RecordedTest';
    const language = window.lastRecorderLanguage || 'java';
    const extension = language === 'python' ? '.py' : '.java';
    
    const blob = new Blob([code], { type: 'text/plain' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${testName}${extension}`;
    a.click();
    showNotification('✅ Code exported successfully!');
}

function saveRecorderSnippet() {
    const code = window.lastRecorderCode || document.getElementById('recorderOutputCode').textContent;
    const testName = document.getElementById('recordingName').value || 'RecordedTest';
    const module = document.getElementById('recordingModule').value || 'Recorded';
    const language = window.lastRecorderLanguage || 'java';
    
    const snippet = {
        id: Date.now(),
        title: testName,
        language: language,
        tags: ['recorded', 'test', module],
        description: `Recorded test case from ${module} module`,
        code: code,
        createdAt: new Date().toISOString(),
        date: new Date().toLocaleString()
    };
    
    let snippets = JSON.parse(localStorage.getItem('codeSnippets') || '[]');
    snippets.unshift(snippet);
    localStorage.setItem('codeSnippets', JSON.stringify(snippets));
    
    showNotification('✅ Saved to Code Snippets!');
}

function editRecorderOutput() {
    const code = window.lastRecorderCode || document.getElementById('recorderOutputCode').textContent;
    const editArea = document.getElementById('recorderCodeEditArea');
    const editor = document.getElementById('recorderCodeEditor');
    const viewer = document.getElementById('recorderOutputContainer');
    
    editArea.value = code;
    viewer.style.display = 'none';
    editor.style.display = 'block';
}

async function saveRecorderEditedCode() {
    const editedCode = document.getElementById('recorderCodeEditArea').value;
    const sessionId = window.lastRecorderSessionId || currentSessionId;
    
    if (!sessionId) {
        alert('No recording session to save to');
        return;
    }
    
    showLoading(true);
    
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
            window.lastRecorderCode = editedCode;
            document.getElementById('recorderOutputCode').textContent = editedCode;
            cancelRecorderEdit();
            alert('✅ Code updated successfully!');
        } else {
            alert('❌ Failed to save: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        alert('❌ Error saving code: ' + error.message);
    } finally {
        showLoading(false);
    }
}

function cancelRecorderEdit() {
    const editor = document.getElementById('recorderCodeEditor');
    const viewer = document.getElementById('recorderOutputContainer');

    editor.style.display = 'none';
    viewer.style.display = 'block';
}

// Expose functions to window object
window.startRecording = startRecording;
window.stopRecording = stopRecording;
window.startNewTestCase = startNewTestCase;
window.generateTestFromRecording = generateTestFromRecording;
window.editRecorderOutput = editRecorderOutput;
window.saveRecorderEditedCode = saveRecorderEditedCode;
window.cancelRecorderEdit = cancelRecorderEdit;
window.copyRecorderOutput = copyRecorderOutput;
window.exportRecorderCode = exportRecorderCode;
window.saveRecorderSnippet = saveRecorderSnippet;