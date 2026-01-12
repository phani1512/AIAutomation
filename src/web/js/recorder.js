// Test Recorder Functions

let isRecording = false;
let recordedActions = [];
let recorderWindow = null;

function startRecording() {
    const url = document.getElementById('recordingUrl')?.value.trim();
    
    if (!url) {
        alert('Please enter a URL to record');
        return;
    }
    
    if (!url.startsWith('http://') && !url.startsWith('https://')) {
        alert('URL must start with http:// or https://');
        return;
    }
    
    isRecording = true;
    recordedActions = [];
    
    updateRecorderUI(true);
    
    // Open window for recording
    const width = 1200;
    const height = 800;
    const left = (screen.width - width) / 2;
    const top = (screen.height - height) / 2;
    
    recorderWindow = window.open(
        url,
        'RecorderWindow',
        `width=${width},height=${height},left=${left},top=${top}`
    );
    
    if (!recorderWindow) {
        alert('Please allow pop-ups to use the recorder');
        stopRecording();
        return;
    }
    
    // Inject recorder script after page loads
    recorderWindow.addEventListener('load', () => {
        injectRecorderScript();
    });
    
    // Listen for messages from recorder window
    window.addEventListener('message', handleRecorderMessage);
    
    window.showNotification('🎬 Recording started! Perform actions in the new window.');
}

function stopRecording() {
    isRecording = false;
    updateRecorderUI(false);
    
    if (recorderWindow && !recorderWindow.closed) {
        recorderWindow.close();
    }
    recorderWindow = null;
    
    window.removeEventListener('message', handleRecorderMessage);
    
    if (recordedActions.length > 0) {
        generateTestFromRecording();
        window.showNotification(`✅ Recording stopped! ${recordedActions.length} actions recorded.`);
    } else {
        window.showNotification('Recording stopped (no actions recorded)');
    }
}

function injectRecorderScript() {
    if (!recorderWindow) return;
    
    const script = recorderWindow.document.createElement('script');
    script.textContent = `
        (function() {
            let actionCounter = 0;
            
            // Track clicks
            document.addEventListener('click', function(e) {
                const element = e.target;
                const action = {
                    type: 'click',
                    timestamp: Date.now(),
                    element: getElementInfo(element),
                    xpath: getXPath(element)
                };
                window.opener.postMessage({ type: 'recorder-action', action }, '*');
            }, true);
            
            // Track input
            document.addEventListener('input', function(e) {
                const element = e.target;
                if (element.tagName === 'INPUT' || element.tagName === 'TEXTAREA') {
                    const action = {
                        type: 'input',
                        timestamp: Date.now(),
                        element: getElementInfo(element),
                        xpath: getXPath(element),
                        value: element.value
                    };
                    window.opener.postMessage({ type: 'recorder-action', action }, '*');
                }
            }, true);
            
            // Track select changes
            document.addEventListener('change', function(e) {
                const element = e.target;
                if (element.tagName === 'SELECT') {
                    const action = {
                        type: 'select',
                        timestamp: Date.now(),
                        element: getElementInfo(element),
                        xpath: getXPath(element),
                        value: element.value
                    };
                    window.opener.postMessage({ type: 'recorder-action', action }, '*');
                }
            }, true);
            
            function getElementInfo(element) {
                return {
                    tagName: element.tagName,
                    id: element.id || '',
                    className: element.className || '',
                    name: element.name || '',
                    type: element.type || '',
                    text: element.textContent ? element.textContent.substring(0, 50) : '',
                    placeholder: element.placeholder || ''
                };
            }
            
            function getXPath(element) {
                if (element.id !== '') {
                    return '//*[@id="' + element.id + '"]';
                }
                if (element === document.body) {
                    return '/html/body';
                }
                
                let ix = 0;
                const siblings = element.parentNode ? element.parentNode.childNodes : [];
                
                for (let i = 0; i < siblings.length; i++) {
                    const sibling = siblings[i];
                    if (sibling === element) {
                        const path = getXPath(element.parentNode);
                        return path + '/' + element.tagName.toLowerCase() + '[' + (ix + 1) + ']';
                    }
                    if (sibling.nodeType === 1 && sibling.tagName === element.tagName) {
                        ix++;
                    }
                }
            }
            
            // Visual feedback
            const indicator = document.createElement('div');
            indicator.textContent = '🔴 Recording...';
            indicator.style.cssText = \`
                position: fixed;
                top: 10px;
                right: 10px;
                background: rgba(255, 0, 0, 0.9);
                color: white;
                padding: 10px 20px;
                border-radius: 20px;
                font-weight: bold;
                z-index: 999999;
                font-family: Arial, sans-serif;
                box-shadow: 0 2px 10px rgba(0,0,0,0.3);
            \`;
            document.body.appendChild(indicator);
        })();
    `;
    
    recorderWindow.document.body.appendChild(script);
}

function handleRecorderMessage(event) {
    if (event.data.type === 'recorder-action') {
        recordAction(event.data.action);
    }
}

function recordAction(action) {
    if (!isRecording) return;
    
    recordedActions.push(action);
    updateRecordedActionsList();
}

function updateRecordedActionsList() {
    const list = document.getElementById('recordedActionsList');
    
    if (recordedActions.length === 0) {
        list.innerHTML = '<div style="text-align: center; padding: 40px; color: var(--text-secondary);">No actions recorded yet</div>';
        return;
    }
    
    list.innerHTML = recordedActions.map((action, index) => {
        let icon = '🖱️';
        let description = '';
        
        switch (action.type) {
            case 'click':
                icon = '🖱️';
                description = `Click ${action.element.tagName}`;
                if (action.element.text) {
                    description += `: "${action.element.text.substring(0, 30)}"`;
                }
                break;
            case 'input':
                icon = '⌨️';
                description = `Type in ${action.element.tagName}`;
                if (action.element.placeholder) {
                    description += ` (${action.element.placeholder})`;
                }
                break;
            case 'select':
                icon = '📋';
                description = `Select option: ${action.value}`;
                break;
        }
        
        return `
            <div style="padding: 10px; margin-bottom: 8px; background: var(--bg-secondary); border-radius: 6px; display: flex; justify-content: space-between; align-items: center;">
                <div style="flex: 1;">
                    <span style="font-size: 1.2em; margin-right: 10px;">${icon}</span>
                    <span style="color: var(--text-primary);">${description}</span>
                </div>
                <button onclick="deleteRecordedAction(${index})" style="background: var(--error); color: white; border: none; padding: 5px 10px; border-radius: 4px; cursor: pointer;">🗑️</button>
            </div>
        `;
    }).join('');
}

function deleteRecordedAction(index) {
    recordedActions.splice(index, 1);
    updateRecordedActionsList();
}

function clearRecordedActions() {
    recordedActions = [];
    updateRecordedActionsList();
    window.showNotification('🗑️ All actions cleared');
}

function updateRecorderUI(recording) {
    const startBtn = document.getElementById('startRecordBtn');
    const stopBtn = document.getElementById('stopRecordBtn');
    const urlInput = document.getElementById('recordingUrl');
    const statusContainer = document.getElementById('recordingStatus');
    const statusText = document.getElementById('recordingStatusText');
    const actionsContainer = document.getElementById('recordedActionsContainer');
    
    if (recording) {
        if (startBtn) startBtn.style.display = 'none';
        if (stopBtn) stopBtn.style.display = 'inline-block';
        if (urlInput) urlInput.disabled = true;
        if (statusContainer) statusContainer.style.display = 'block';
        if (statusText) statusText.textContent = '🔴 Recording in progress...';
        if (actionsContainer) actionsContainer.style.display = 'block';
    } else {
        if (startBtn) startBtn.style.display = 'inline-block';
        if (stopBtn) stopBtn.style.display = 'none';
        if (urlInput) urlInput.disabled = false;
        if (statusContainer) statusContainer.style.display = 'none';
        if (statusText) statusText.textContent = '';
    }
}

async function generateTestFromRecording() {
    if (recordedActions.length === 0) {
        alert('No actions recorded');
        return;
    }
    
    window.showLoading(true);
    
    try {
        const response = await fetch(`${window.API_URL}/generate-from-recording`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                actions: recordedActions,
                language: document.getElementById('languageSelector').value
            })
        });
        
        const data = await response.json();
        
        if (data.code) {
            // Switch to generator page and display code
            window.navigateTo('generator');
            window.displayResult(data.code, 0, 0);
            window.showNotification('✅ Test code generated from recording!');
        } else {
            throw new Error(data.error || 'Failed to generate code');
        }
    } catch (error) {
        window.showNotification('❌ Error: ' + error.message, 'error');
    } finally {
        window.showLoading(false);
    }
}

function exportRecording() {
    if (recordedActions.length === 0) {
        alert('No actions to export');
        return;
    }
    
    const data = JSON.stringify(recordedActions, null, 2);
    const blob = new Blob([data], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'recorded-actions.json';
    
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
    
    window.showNotification('✅ Recording exported!');
}

function importRecording() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = 'application/json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            try {
                const imported = JSON.parse(event.target.result);
                if (Array.isArray(imported)) {
                    recordedActions = imported;
                    updateRecordedActionsList();
                    window.showNotification(`✅ Imported ${imported.length} actions`);
                } else {
                    throw new Error('Invalid format');
                }
            } catch (error) {
                alert('Error importing recording: ' + error.message);
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

function startNewTestCase() {
    if (confirm('Start a new test case? This will clear the current recording.')) {
        recordedActions = [];
        const actionsList = document.getElementById('recordedActions');
        if (actionsList) actionsList.innerHTML = '';
        window.showNotification('✅ New test case started!');
    }
}

function copyRecorderOutput() {
    const code = document.getElementById('recorderOutput')?.textContent || '';
    if (code) {
        navigator.clipboard.writeText(code).then(() => {
            window.showNotification('✅ Code copied to clipboard!');
        });
    }
}

function exportRecorderCode() {
    const code = document.getElementById('recorderOutput')?.textContent || '';
    if (code) {
        const blob = new Blob([code], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = 'recorded_test.py';
        document.body.appendChild(a);
        a.click();
        document.body.removeChild(a);
        URL.revokeObjectURL(url);
        window.showNotification('✅ Code exported!');
    }
}

function saveRecorderSnippet() {
    const code = document.getElementById('recorderOutput')?.textContent || '';
    if (code && typeof window.showAddSnippetModal === 'function') {
        window.showAddSnippetModal(code);
    }
}

function editRecorderOutput() {
    const output = document.getElementById('recorderOutput');
    const editor = document.getElementById('recorderEditor');
    const editorTextarea = document.getElementById('recorderEditorTextarea');
    
    if (output && editor && editorTextarea) {
        editorTextarea.value = output.textContent;
        output.style.display = 'none';
        editor.style.display = 'block';
    }
}

function saveRecorderEditedCode() {
    const output = document.getElementById('recorderOutput');
    const editor = document.getElementById('recorderEditor');
    const editorTextarea = document.getElementById('recorderEditorTextarea');
    
    if (output && editor && editorTextarea) {
        output.textContent = editorTextarea.value;
        output.style.display = 'block';
        editor.style.display = 'none';
        window.showNotification('✅ Changes saved!');
    }
}

function cancelRecorderEdit() {
    const output = document.getElementById('recorderOutput');
    const editor = document.getElementById('recorderEditor');
    
    if (output && editor) {
        output.style.display = 'block';
        editor.style.display = 'none';
    }
}

// Expose functions to global scope for HTML onclick handlers
window.startRecording = startRecording;
window.stopRecording = stopRecording;
window.startNewTestCase = startNewTestCase;
window.injectRecorderScript = injectRecorderScript;
window.recordAction = recordAction;
window.generateTestFromRecording = generateTestFromRecording;
window.copyRecorderOutput = copyRecorderOutput;
window.exportRecorderCode = exportRecorderCode;
window.saveRecorderSnippet = saveRecorderSnippet;
window.editRecorderOutput = editRecorderOutput;
window.saveRecorderEditedCode = saveRecorderEditedCode;
window.cancelRecorderEdit = cancelRecorderEdit;
window.exportRecording = exportRecording;
window.importRecording = importRecording;


