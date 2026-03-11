// Test Recorder Features

// Use window for global state so it's accessible across modules
if (!window.recorderState) {
    window.recorderState = {
        isRecording: false,
        currentSessionId: null,
        recordedActions: [],
        pollingIntervalId: null,
        liveMonitor: null  // RecorderLiveMonitor instance
    };
}

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
            
            const startBtn = document.getElementById('startRecordBtn');
            const stopBtn = document.getElementById('stopRecordBtn');
            const newBtn = document.getElementById('newTestBtn');
            const actionsContainer = document.getElementById('recordedActionsContainer');
            
            if (startBtn) startBtn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'inline-block';
            if (newBtn) newBtn.style.display = 'none';
            if (actionsContainer) actionsContainer.style.display = 'block';
            
            showRecordingStatus(`✅ Session ${currentSessionId} created! Now initializing browser...`);
            
            // Initialize browser
            try {
                const browserResp = await fetch(`${API_URL}/browser/initialize`, {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({ browser: 'chrome', headless: false })
                });

                if (browserResp.ok) {
                    showRecordingStatus('🔴 Browser initialized. Navigating to: ' + url);
                    
                    // Wait a moment for browser to be ready
                    await new Promise(resolve => setTimeout(resolve, 2000));
                    
                    // Navigate to URL and inject recorder
                    const navResp = await fetch(`${API_URL}/recorder/navigate`, {
                        method: 'POST',
                        headers: { 'Content-Type': 'application/json' },
                        body: JSON.stringify({
                            url: url,
                            session_id: currentSessionId
                        })
                    });
                    
                    console.log('Navigate response status:', navResp.status);
                    
                    if (navResp.ok) {
                        const navData = await navResp.json();
                        console.log('Navigate data:', navData);
                        if (navData.success) {
                            showRecordingStatus('🔴 Recording in progress! Interact with the browser to record actions.');
                            
                            // Auto-focus browser window
                            setTimeout(() => {
                                bringBrowserToFront().catch(err => {
                                    console.warn('Could not auto-focus browser:', err);
                                });
                            }, 1000);
                            
                            // Initialize live monitoring
                            if (window.RecorderLiveMonitor) {
                                const liveStatusPanel = document.getElementById('recorderLiveStatusPanel');
                                if (liveStatusPanel) {
                                    liveStatusPanel.style.display = 'block';
                                }
                                
                                window.recorderState.liveMonitor = new RecorderLiveMonitor();
                                window.recorderState.liveMonitor.start(currentSessionId);
                                console.log('✅ Live monitoring started for session:', currentSessionId);
                            } else {
                                console.warn('⚠️ RecorderLiveMonitor class not found - live monitoring disabled');
                            }
                        } else {
                            showRecordingStatus('⚠️ Navigation failed: ' + (navData.error || 'Unknown error'));
                        }
                    } else {
                        const errorText = await navResp.text();
                        console.error('Navigation error response:', errorText);
                        let errorData;
                        try {
                            errorData = JSON.parse(errorText);
                        } catch (e) {
                            errorData = { error: errorText || 'Unknown error' };
                        }
                        console.error('Navigation error:', errorData);
                        showRecordingStatus('⚠️ Navigation request failed: ' + (errorData.error || `HTTP ${navResp.status}`));
                    }
                    
                    // Poll for recorded actions
                    startPollingActions();
                    updateRecordedActionsList();
                } else {
                    showRecordingStatus('⚠️ Session created but browser failed to initialize.');
                }
            } catch (browserError) {
                console.error('Browser initialization error:', browserError);
                showRecordingStatus('⚠️ Session created but browser initialization failed: ' + browserError.message);
            }
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
                    
                    // Show notification for new actions
                    const newCount = newActions.length - recordedActions.length;
                    if (newCount > 0 && typeof showNotification === 'function') {
                        showNotification(`✅ Captured ${newCount} new action${newCount > 1 ? 's' : ''}`);
                    }
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
    
    // Update action counter badge in recording status
    const actionCounter = document.getElementById('actionCounter');
    if (actionCounter) {
        actionCounter.textContent = recordedActions.length + ' action' + (recordedActions.length !== 1 ? 's' : '');
    }
    
    // Update live panel action count
    const liveActionCount = document.getElementById('liveActionCount');
    if (liveActionCount) {
        liveActionCount.textContent = recordedActions.length;
        // Add animation effect
        liveActionCount.style.transform = 'scale(1.2)';
        setTimeout(() => {
            liveActionCount.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Update dashboard stats
    if (typeof window.stats !== 'undefined') {
        window.stats.totalRequests = recordedActions.length;
        // Save stats to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
        }
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
    }
    
    if (recordedActions.length === 0) {
        if (listElement) {
            listElement.innerHTML = '<div style="padding: 15px; color: var(--text-secondary); text-align: center;">No actions recorded yet. Interact with the webpage...</div>';
        }
        return;
    }
    
    if (listElement) {
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
        
        // Build better element description with text/label
        let elementInfo = 'Unknown';
        if (action.element) {
            const elem = action.element;
            // Priority: text content > aria-label > title > id > name > tagName
            if (elem.text && elem.text.length > 0) {
                elementInfo = `${elem.tagName.toUpperCase()} "${elem.text.substring(0, 30)}${elem.text.length > 30 ? '...' : ''}"`;
            } else if (elem.innerText && elem.innerText.length > 0) {
                elementInfo = `${elem.tagName.toUpperCase()} "${elem.innerText.substring(0, 30)}${elem.innerText.length > 30 ? '...' : ''}"`;
            } else if (elem.ariaLabel) {
                elementInfo = `${elem.tagName.toUpperCase()} [${elem.ariaLabel}]`;
            } else if (elem.title) {
                elementInfo = `${elem.tagName.toUpperCase()} [${elem.title}]`;
            } else if (elem.id) {
                elementInfo = `${elem.tagName.toUpperCase()} #${elem.id}`;
            } else if (elem.name) {
                elementInfo = `${elem.tagName.toUpperCase()} name="${elem.name}"`;
            } else {
                elementInfo = elem.tagName.toUpperCase();
            }
        } else if (action.url) {
            elementInfo = 'Page';
        }
        
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
            
            // Stop live monitoring
            if (window.recorderState.liveMonitor) {
                window.recorderState.liveMonitor.stop();
                window.recorderState.liveMonitor = null;
                console.log('✅ Live monitoring stopped');
                
                const liveStatusPanel = document.getElementById('recorderLiveStatusPanel');
                if (liveStatusPanel) {
                    liveStatusPanel.style.display = 'none';
                }
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
            
            const startBtn1 = document.getElementById('startRecordBtn');
            const stopBtn1 = document.getElementById('stopRecordBtn');
            const newBtn1 = document.getElementById('newTestBtn');
            
            if (startBtn1) startBtn1.style.display = 'none';
            if (stopBtn1) stopBtn1.style.display = 'none';
            if (newBtn1) newBtn1.style.display = 'inline-block';
            
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
            
            const startBtn2 = document.getElementById('startRecordBtn');
            const stopBtn2 = document.getElementById('stopRecordBtn');
            const newBtn2 = document.getElementById('newTestBtn');
            const actionsContainer2 = document.getElementById('recordedActionsContainer');
            
            if (startBtn2) startBtn2.style.display = 'none';
            if (stopBtn2) stopBtn2.style.display = 'inline-block';
            if (newBtn2) newBtn2.style.display = 'none';
            
            showRecordingStatus(`🔴 New test case "${testName}" started! Recording in progress...`);
            
            if (actionsContainer2) actionsContainer2.style.display = 'block';
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
            
            const editBtn = document.getElementById('editRecorderBtn');
            const copyBtn = document.getElementById('copyRecorderBtn');
            const exportBtn = document.getElementById('exportRecorderBtn');
            const saveBtn = document.getElementById('saveRecorderSnippetBtn');
            
            if (editBtn) editBtn.style.display = 'inline-block';
            if (copyBtn) copyBtn.style.display = 'inline-block';
            if (exportBtn) exportBtn.style.display = 'inline-block';
            if (saveBtn) saveBtn.style.display = 'inline-block';
            
            window.lastRecorderCode = data.code;
            window.lastRecorderSessionId = currentSessionId;
            window.lastRecorderLanguage = language;
            
            const executeSection = document.getElementById('executeTestSection');
            if (executeSection) executeSection.style.display = 'block';
            
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

async function bringBrowserToFront() {
    try {
        const response = await fetch(`${API_URL}/browser/focus`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        if (response.ok) {
            const data = await response.json();
            if (data.success) {
                console.log('✅ Browser window brought to front');
                showNotification('🪟 Browser focused');
            } else {
                console.warn('⚠️ Browser focus failed:', data.error);
            }
        } else {
            console.error('Failed to focus browser:', response.status);
        }
    } catch (error) {
        console.error('Error focusing browser:', error);
    }
}

// Expose functions and variables to window object
Object.defineProperty(window, 'isRecording', {
    get: () => window.recorderState.isRecording,
    set: (value) => { window.recorderState.isRecording = value; }
});

Object.defineProperty(window, 'currentSessionId', {
    get: () => window.recorderState.currentSessionId,
    set: (value) => { window.recorderState.currentSessionId = value; }
});

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
window.bringBrowserToFront = bringBrowserToFront;