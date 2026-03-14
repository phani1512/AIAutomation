// Test Recorder Features

// Use window for global state so it's accessible across modules
if (!window.recorderState) {
    window.recorderState = {
        isRecording: false,
        currentSessionId: null,
        recordedActions: [],
        pollingIntervalId: null,
        liveMonitor: null,  // RecorderLiveMonitor instance
        sessionHistory: [],  // Track all recording sessions
        player: null,        // RecorderPlayer instance (Phase 4)
        templates: null      // RecorderTemplate instance (Phase 4)
    };
}

// Initialize Phase 4 features (Replay & Templates)
function initializePhase4Features() {
    console.log('[Recorder] 🚀 Initializing Phase 4: Advanced Features...');
    
    // Initialize RecorderPlayer if available
    if (typeof RecorderPlayer !== 'undefined') {
        window.recorderState.player = new RecorderPlayer({
            speed: 1,
            onStepComplete: (action, current, total) => {
                console.log(`[Replay] Step ${current}/${total} completed:`, action.type);
                updateReplayProgress(current, total);
            },
            onPlayComplete: (session) => {
                console.log('[Replay] ✅ Playback complete:', session.name);
                showReplayComplete(session);
            },
            onError: (error) => {
                console.error('[Replay] ❌ Error:', error);
                alert(`Replay error: ${error.message}`);
            },
            onBreakpoint: (action) => {
                console.log('[Replay] 🔴 Breakpoint at step:', action.step);
                showBreakpointDialog(action);
            }
        });
        console.log('[Recorder] ✅ RecorderPlayer initialized');
    }
    
    // Initialize RecorderTemplate if available
    if (typeof RecorderTemplate !== 'undefined') {
        window.recorderState.templates = new RecorderTemplate();
        console.log('[Recorder] ✅ RecorderTemplate initialized');
        console.log(`[Recorder] 📋 ${window.recorderState.templates.getAllTemplates().length} templates available`);
    }
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initializePhase4Features);
} else {
    initializePhase4Features();
}

// Update session history display
function updateSessionHistory(sessionId, testName, actionCount, status = 'active') {
    const history = window.recorderState.sessionHistory;
    
    // Check if session already exists
    const existingIndex = history.findIndex(s => s.id === sessionId);
    
    if (existingIndex >= 0) {
        // Update existing session
        history[existingIndex] = {
            id: sessionId,
            name: testName,
            actionCount: actionCount,
            status: status,
            timestamp: history[existingIndex].timestamp
        };
    } else {
        // Add new session
        history.push({
            id: sessionId,
            name: testName,
            actionCount: actionCount,
            status: status,
            timestamp: Date.now()
        });
    }
    
    // Show panel if we have sessions
    const panel = document.getElementById('sessionHistoryPanel');
    if (panel && history.length > 0) {
        panel.style.display = 'block';
    }
    
    // Update count
    const countDisplay = document.getElementById('sessionHistoryCount');
    if (countDisplay) {
        countDisplay.textContent = `${history.length} session${history.length !== 1 ? 's' : ''}`;
    }
    
    // Update list
    const listDisplay = document.getElementById('sessionHistoryList');
    if (listDisplay) {
        if (history.length === 0) {
            listDisplay.innerHTML = 'No sessions yet';
        } else {
            listDisplay.innerHTML = history.map(session => {
                const statusIcon = session.status === 'active' ? '🔴' : 
                                   session.status === 'stopped' ? '⏹️' : '✅';
                const statusColor = session.status === 'active' ? '#ef4444' : 
                                   session.status === 'stopped' ? '#f59e0b' : '#10b981';
                const isCurrent = session.id === window.recorderState.currentSessionId;
                const currentBadge = isCurrent ? '<span style="background: #667eea; color: white; padding: 2px 6px; border-radius: 4px; font-size: 0.75em; margin-left: 6px;">CURRENT</span>' : '';
                
                return `
                    <div style="padding: 6px; margin-bottom: 4px; background: white; border-radius: 4px; border-left: 3px solid ${statusColor};">
                        <div style="display: flex; justify-content: between; align-items: center;">
                            <span>${statusIcon} <strong>${session.name || 'Unnamed Test'}</strong> ${currentBadge}</span>
                        </div>
                        <div style="font-size: 0.8em; color: #9ca3af; margin-top: 2px;">
                            ID: ${session.id.substring(0, 8)}... | ${session.actionCount} actions | ${new Date(session.timestamp).toLocaleTimeString()}
                        </div>
                    </div>
                `;
            }).reverse().join('');  // Reverse to show newest first
        }
    }
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
            window.recorderState.currentSessionId = data.session_id;
            window.recorderState.isRecording = true;
            window.recorderState.recordedActions = [];
            
            // Track this session in history
            updateSessionHistory(data.session_id, testName, 0, 'active');
            
            const startBtn = document.getElementById('startRecordBtn');
            const stopBtn = document.getElementById('stopRecordBtn');
            const newBtn = document.getElementById('newTestBtn');
            const actionsContainer = document.getElementById('recordedActionsContainer');
            
            if (startBtn) startBtn.style.display = 'none';
            if (stopBtn) stopBtn.style.display = 'inline-block';
            if (newBtn) newBtn.style.display = 'none';
            if (actionsContainer) actionsContainer.style.display = 'block';
            
            showRecordingStatus(`✅ Session ${window.recorderState.currentSessionId} created! Now initializing browser...`);
            
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
                            session_id: window.recorderState.currentSessionId
                        })
                    });
                    
                    console.log('Navigate response status:', navResp.status);
                    
                    if (navResp.ok) {
                        const navData = await navResp.json();
                        console.log('Navigate data:', navData);
                        if (navData.success) {
                        console.log('✅ Navigation successful, recorder script injected');
                        console.log('📝 Recorder should be capturing actions now');
                        console.log('🔍 Check browser console for [Recorder] messages');
                        
                            showRecordingStatus('🔴 Recording in progress! Interact with the browser to record actions.');
                            
                            // Verify recorder is actually running (diagnostic check)
                            setTimeout(async () => {
                                try {
                                    const checkResponse = await fetch(`${API_URL}/browser/execute`, {
                                        method: 'POST',
                                        headers: { 'Content-Type': 'application/json' },
                                        body: JSON.stringify({
                                            code: 'return { isRecording: window.isRecording, hasStartFunction: typeof window.startRecorderCapture === "function", actionCount: window.actionCount || 0 };'
                                        })
                                    });
                                    
                                    if (checkResponse.ok) {
                                        const checkData = await checkResponse.json();
                                        console.log('🔍 RECORDER STATUS CHECK:', checkData);
                                        
                                        if (checkData.success && checkData.result) {
                                            if (!checkData.result.isRecording) {
                                                console.error('❌ PROBLEM: window.isRecording is FALSE!');
                                                console.error('   The recorder was not started properly');
                                                console.error('   Attempting to manually start it now...');
                                                
                                                // Try to start it manually
                                                const startResponse = await fetch(`${API_URL}/browser/execute`, {
                                                    method: 'POST',
                                                    headers: { 'Content-Type': 'application/json' },
                                                    body: JSON.stringify({
                                                        code: 'if (typeof window.startRecorderCapture === "function") { window.startRecorderCapture(); return "Recorder started manually"; } else { return "ERROR: startRecorderCapture function not found"; }'
                                                    })
                                                });
                                                
                                                if (startResponse.ok) {
                                                    const startData = await startResponse.json();
                                                    console.log('🔄 Manual start result:', startData);
                                                    showNotification('Recorder manually started', 'info');
                                                }
                                            } else {
                                                console.log('✅ Recorder is active (window.isRecording = true)');
                                            }
                                        } else {
                                            console.warn('⚠️ Could not get recorder status');
                                        }
                                    }
                                } catch (err) {
                                    console.warn('Could not verify recorder status:', err);
                                }
                            }, 2000);
                            
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
                                window.recorderState.liveMonitor.start(window.recorderState.currentSessionId);
                                console.log('✅ Live monitoring started for session:', window.recorderState.currentSessionId);
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
    if (!window.recorderState.currentSessionId || !window.recorderState.isRecording) {
        console.log('Not polling - no session or not recording');
        return;
    }
    
    console.log('Starting to poll actions for session:', window.recorderState.currentSessionId);
    
    const pollActions = async () => {
        if (!window.recorderState.isRecording || !window.recorderState.currentSessionId) {
            console.log('Stopping polling - recording stopped or no session');
            return;
        }
        
        try {
            const response = await fetch(`${API_URL}/recorder/session/${window.recorderState.currentSessionId}`);
            const data = await response.json();
            
            if (data.success && data.session) {
                const newActions = data.session.actions || [];
                
                if (newActions.length !== window.recorderState.recordedActions.length) {
                    console.log(`Actions updated: ${window.recorderState.recordedActions.length} -> ${newActions.length}`);
                    const previousCount = window.recorderState.recordedActions.length;
                    window.recorderState.recordedActions = newActions;
                    updateRecordedActionsList();
                    
                    // Show visual feedback for new actions
                    const newCount = newActions.length - previousCount;
                    if (newCount > 0) {
                        // Toast notification
                        if (typeof showNotification === 'function') {
                            const lastAction = newActions[newActions.length - 1];
                            const actionIcon = getActionIcon(lastAction.action_type);
                            showNotification(`${actionIcon} Action #${newActions.length}: ${lastAction.action_type}`);
                        }
                        
                        // Visual pulse effect on action counter
                        const actionCounter = document.getElementById('actionCounter');
                        if (actionCounter) {
                            actionCounter.style.animation = 'pulse 0.5s ease';
                            setTimeout(() => {
                                actionCounter.style.animation = '';
                            }, 500);
                        }
                        
                        // Sound feedback (optional)
                        playRecordSound();
                    }
                }
            }
        } catch (error) {
            console.error('Error polling actions:', error);
        }
        
        if (window.recorderState.isRecording) {
            window.recorderState.pollingIntervalId = setTimeout(pollActions, 1000);
        }
    };
    
    pollActions();
}

function updateRecordedActionsList() {
    const listElement = document.getElementById('recordedActionsList');
    
    // Update action counter badge in recording status
    const actionCounter = document.getElementById('actionCounter');
    if (actionCounter) {
        actionCounter.textContent = window.recorderState.recordedActions.length + ' action' + (window.recorderState.recordedActions.length !== 1 ? 's' : '');
    }
    
    // Update live panel action count
    const liveActionCount = document.getElementById('liveActionCount');
    if (liveActionCount) {
        liveActionCount.textContent = window.recorderState.recordedActions.length;
        // Add animation effect
        liveActionCount.style.transform = 'scale(1.2)';
        setTimeout(() => {
            liveActionCount.style.transform = 'scale(1)';
        }, 200);
    }
    
    // Update dashboard stats
    if (typeof window.stats !== 'undefined') {
        window.stats.totalRequests = window.recorderState.recordedActions.length;
        // Save stats to localStorage
        if (typeof window.saveStats === 'function') {
            window.saveStats();
        }
        if (typeof window.updateDashboardStats === 'function') {
            window.updateDashboardStats();
        }
    }
    
    // Update session history with current action count
    if (window.recorderState.currentSessionId && window.recorderState.isRecording) {
        updateSessionHistory(
            window.recorderState.currentSessionId,
            document.getElementById('recordingName')?.value || 'Unnamed Test',
            window.recorderState.recordedActions.length,
            'active'
        );
    }
    
    if (window.recorderState.recordedActions.length === 0) {
        if (listElement) {
            listElement.innerHTML = '<div style="padding: 15px; color: var(--text-secondary); text-align: center;">No actions recorded yet. Interact with the webpage...</div>';
        }
        return;
    }
    
    if (listElement) {
        listElement.innerHTML = window.recorderState.recordedActions.map((action, index) => {
        const icons = {
            'click': '🖱️',
            'input': '⌨️',
            'select': '📋',
            'navigate': '🌐',
            'click_and_input': '🖱️⌨️',
            'file_upload': '📁',
            'hover': '👆',
            'scroll': '📜',
            'verify_message': '✅'
        };
        
        const icon = icons[action.action_type] || '✅';
        
        // Framework badge
        const framework = action.element?.framework;
        const frameworkBadge = framework ? 
            `<span style="background: ${getFrameworkColor(framework)}; color: white; padding: 2px 6px; border-radius: 3px; font-size: 0.75em; margin-left: 8px;">${framework.toUpperCase()}</span>` : '';
        
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
        <div class="action-item-new" style="padding: 12px; border-bottom: 1px solid var(--border-color); display: flex; justify-content: space-between; align-items: center; transition: all 0.2s; background: ${index === window.recorderState.recordedActions.length - 1 ? 'rgba(16, 185, 129, 0.05)' : 'transparent'};">
            <div style="flex: 1;">
                <div style="display: flex; align-items: center; gap: 8px; margin-bottom: 4px;">
                    <span style="font-weight: 600; font-size: 1.1em;">${icon}</span>
                    <span style="font-weight: 500; color: var(--text-primary);">${action.action_type}</span>
                    ${frameworkBadge}
                </div>
                <div style="margin-left: 32px;">
                    <span style="color: var(--text-secondary); font-size: 0.9em;">${elementInfo}</span>
                    ${action.value ? `<div style="color: var(--text-tertiary); margin-top: 4px; font-size: 0.85em;">💬 Value: <code style="background: var(--bg-secondary); padding: 2px 6px; border-radius: 3px;">"${action.value.substring(0, 50)}${action.value.length > 50 ? '...' : ''}"</code></div>` : ''}
                </div>
            </div>
            <span style="background: var(--bg-secondary); color: var(--text-primary); padding: 4px 10px; border-radius: 12px; font-size: 0.85em; font-weight: 600;">#{action.step || index + 1}</span>
        </div>
        `;
        }).join('');
    }
}

async function stopRecording() {
    if (!window.recorderState.isRecording) {
        alert('No active recording session');
        return;
    }
    
    console.log('Stopping recording for session:', window.recorderState.currentSessionId);
    
    try {
        const response = await fetch(`${API_URL}/recorder/stop`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' }
        });
        
        const data = await response.json();
        console.log('Stop response:', data);
        
        if (data.success) {
            if (window.recorderState.pollingIntervalId) {
                clearTimeout(window.recorderState.pollingIntervalId);
                window.recorderState.pollingIntervalId = null;
            }
            
            // Stop live monitoring and reset timer display
            if (window.recorderState.liveMonitor) {
                window.recorderState.liveMonitor.stop();
                window.recorderState.liveMonitor = null;
                console.log('✅ Live monitoring stopped');
            }
            
            // Hide and reset live status panel
            const liveStatusPanel = document.getElementById('recorderLiveStatusPanel');
            if (liveStatusPanel) {
                liveStatusPanel.style.display = 'none';
            }
            
            // Reset timer display to prevent showing stale time
            const timeDisplay = document.getElementById('liveSessionTime');
            if (timeDisplay) {
                timeDisplay.textContent = '00:00';
            }
            
            window.recorderState.isRecording = false;
            
            try {
                const sessionResponse = await fetch(`${API_URL}/recorder/session/${window.recorderState.currentSessionId}`);
                const sessionData = await sessionResponse.json();
                if (sessionData.success) {
                    window.recorderState.recordedActions = sessionData.session.actions;
                    updateRecordedActionsList();
                    
                    // Update session history to stopped status
                    updateSessionHistory(
                        window.recorderState.currentSessionId, 
                        document.getElementById('recordingName').value || 'Unnamed Test',
                        window.recorderState.recordedActions.length, 
                        'stopped'
                    );
                }
            } catch (err) {
                console.error('Error fetching final actions:', err);
            }
            
            const startBtn1 = document.getElementById('startRecordBtn');
            const stopBtn1 = document.getElementById('stopRecordBtn');
            const newBtn1 = document.getElementById('newTestBtn');
            const replayBtn = document.getElementById('replayBtn');
            
            if (startBtn1) startBtn1.style.display = 'none';
            if (stopBtn1) stopBtn1.style.display = 'none';
            if (newBtn1) newBtn1.style.display = 'inline-block';
            if (replayBtn && window.recorderState.recordedActions.length > 0) {
                replayBtn.style.display = 'inline-block';
            }
            
            showRecordingStatus('✅ Recording stopped. ' + window.recorderState.recordedActions.length + ' actions captured. Click "Generate Test Code" to export or "Replay" to verify.');
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
            const previousSessionId = window.recorderState.currentSessionId;
            window.recorderState.currentSessionId = data.session_id;
            window.recorderState.isRecording = true;
            window.recorderState.recordedActions = [];
            
            console.log(`✅ NEW TEST CASE CREATED:`);
            console.log(`   Previous Session: ${previousSessionId}`);
            console.log(`   New Session: ${data.session_id}`);
            console.log(`   Test Name: ${testName}`);
            console.log(`   Module: ${moduleName}`);
            console.log(`   Browser: Reused (not restarted)`);
            
            // Track new test session in history
            updateSessionHistory(data.session_id, testName, 0, 'active');
            
            const startBtn2 = document.getElementById('startRecordBtn');
            const stopBtn2 = document.getElementById('stopRecordBtn');
            const newBtn2 = document.getElementById('newTestBtn');
            const actionsContainer2 = document.getElementById('recordedActionsContainer');
            
            if (startBtn2) startBtn2.style.display = 'none';
            if (stopBtn2) stopBtn2.style.display = 'inline-block';
            if (newBtn2) newBtn2.style.display = 'none';
            
            showRecordingStatus(`🔴 NEW TEST CASE: "${testName}" | Session: ${data.session_id.substring(0, 8)}... | Recording in progress...`);
            showNotification(`✨ New test case created with separate session ID!`, 'success');
            
            if (actionsContainer2) actionsContainer2.style.display = 'block';
            updateRecordedActionsList();
            
            // Restart live monitoring for new test case
            if (window.RecorderLiveMonitor) {
                const liveStatusPanel = document.getElementById('recorderLiveStatusPanel');
                if (liveStatusPanel) {
                    liveStatusPanel.style.display = 'block';
                }
                
                if (window.recorderState.liveMonitor) {
                    window.recorderState.liveMonitor.stop();
                }
                
                window.recorderState.liveMonitor = new RecorderLiveMonitor();
                window.recorderState.liveMonitor.start(window.recorderState.currentSessionId);
                console.log('✅ Live monitoring restarted for new test case:', window.recorderState.currentSessionId);
            }
            
            startPollingActions();
            
            showNotification(`✨ New test case "${testName}" started!`);
        } else {
            alert('Failed to start new test case: ' + (data.error || 'Unknown error'));
        }
    } catch (error) {
        console.error('Error starting new test case:', error);
        alert('Error starting new test case: ' + error.message);
    }
}

async function generateTestFromRecording() {
    console.log('[generateTestFromRecording] 🎬 Button clicked!');
    console.log('[generateTestFromRecording] currentSessionId:', window.recorderState.currentSessionId);
    console.log('[generateTestFromRecording] recordedActions count:', window.recorderState.recordedActions.length);
    
    if (!window.recorderState.currentSessionId) {
        alert('No recording session active');
        return;
    }
    
    const generateBtn = event?.target;
    if (generateBtn) generateBtn.disabled = true;
    
    showLoading(true);
    
    try {
        const testName = document.getElementById('recordingName').value.replace(/\s+/g, '');
        const moduleName = document.getElementById('recordingModule').value || 'default';
        const url = document.getElementById('recordingUrl').value;
        const language = document.getElementById('codeLanguageSelector')?.value || 'java';
        
        // Use RecorderSession entity for multi-format export
        if (typeof RecorderSession !== 'undefined' && window.recorderState.recordedActions.length > 0) {
            console.log('🎯 Using RecorderSession entity for export');
            
            // Create session (start with empty actions)
            const session = new RecorderSession({
                id: window.recorderState.currentSessionId,
                name: testName,
                module: moduleName,
                url: url
            });
            
            // Add actions properly using addAction method to ensure proper instantiation
            window.recorderState.recordedActions.forEach((action, index) => {
                session.addAction({
                    type: action.action_type,
                    element: action.element, // RecorderAction constructor will convert to RecordedElement
                    value: action.value,
                    timestamp: action.timestamp || Date.now()
                });
            });
            
            // Export in selected format
            const formatMap = {
                'java': 'java',
                'python': 'python',
                'javascript': 'javascript',
                'playwright': 'javascript',
                'cypress': 'cypress'
            };
            
            const exportFormat = formatMap[language] || 'java';
            const code = session.export(exportFormat);
            
            // Display the code
            const recorderOutputCode = document.getElementById('recorderOutputCode');
            recorderOutputCode.textContent = code;
            recorderOutputCode.className = `language-${language === 'python' ? 'python' : 'java'}`;
            
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
            
            window.lastRecorderCode = code;
            window.lastRecorderSessionId = window.recorderState.currentSessionId;
            window.lastRecorderLanguage = language;
            
            const executeSection = document.getElementById('executeTestSection');
            if (executeSection) executeSection.style.display = 'block';
            
            showRecordingStatus(`✅ Test code generated with ${window.recorderState.recordedActions.length} actions in ${exportFormat.toUpperCase()}!`);
            showNotification(`✨ Multi-format export: ${exportFormat.toUpperCase()}`);
            
            setTimeout(() => loadTestCases && loadTestCases(), 500);
            
        } else {
            // Fallback to backend generation
            console.log('⚠️ RecorderSession not available, using backend');
            
            const response = await fetch(`${API_URL}/recorder/generate-test`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    session_id: window.recorderState.currentSessionId,
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
                window.lastRecorderSessionId = window.recorderState.currentSessionId;
                window.lastRecorderLanguage = language;
                
                const executeSection = document.getElementById('executeTestSection');
                if (executeSection) executeSection.style.display = 'block';
                
                showRecordingStatus(`✅ Test code generated successfully in ${language.toUpperCase()}!`);
                
                setTimeout(() => loadTestCases && loadTestCases(), 500);
            } else {
                alert('Failed to generate test: ' + data.error);
            }
        }
    } catch (error) {
        console.error('Error generating test:', error);
        alert('Error generating test: ' + error.message);
    } finally {
        showLoading(false);
        const generateBtn = document.querySelector('button[onclick="generateTestFromRecording()"]');
        if (generateBtn) generateBtn.disabled = false;
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
    const sessionId = window.lastRecorderSessionId || window.recorderState.currentSessionId;
    
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

// Visual Feedback Helper Functions
function getActionIcon(actionType) {
    const icons = {
        'click': '🖱️',
        'input': '⌨️',
        'select': '📋',
        'navigate': '🌐',
        'click_and_input': '🖱️⌨️',
        'file_upload': '📁',
        'hover': '👆',
        'scroll': '📜'
    };
    return icons[actionType] || '✅';
}

function getFrameworkColor(framework) {
    const colors = {
        'react': '#61dafb',
        'vue': '#42b883',
        'angular': '#dd0031',
        'svelte': '#ff3e00',
        'ember': '#e04e39'
    };
    return colors[framework.toLowerCase()] || '#6366f1';
}

function playRecordSound() {
    // Subtle audio feedback using Web Audio API
    if (typeof AudioContext !== 'undefined' || typeof webkitAudioContext !== 'undefined') {
        try {
            const AudioCtx = AudioContext || webkitAudioContext;
            const audioContext = new AudioCtx();
            const oscillator = audioContext.createOscillator();
            const gainNode = audioContext.createGain();
            
            oscillator.connect(gainNode);
            gainNode.connect(audioContext.destination);
            
            oscillator.frequency.value = 800;
            oscillator.type = 'sine';
            
            gainNode.gain.setValueAtTime(0.1, audioContext.currentTime);
            gainNode.gain.exponentialRampToValueAtTime(0.01, audioContext.currentTime + 0.1);
            
            oscillator.start(audioContext.currentTime);
            oscillator.stop(audioContext.currentTime + 0.1);
        } catch (e) {
            // Silent fail if audio not supported
            console.debug('Audio feedback not available:', e);
        }
    }
}

// Add CSS for pulse animation if not exists
if (!document.getElementById('recorder-animations')) {
    const style = document.createElement('style');
    style.id = 'recorder-animations';
    style.textContent = `
        @keyframes pulse {
            0%, 100% { transform: scale(1); }
            50% { transform: scale(1.15); background: rgba(16, 185, 129, 0.2); }
        }
        
        @keyframes slideInRight {
            from { transform: translateX(400px); opacity: 0; }
            to { transform: translateX(0); opacity: 1; }
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(-10px); }
            to { opacity: 1; transform: translateY(0); }
        }
        
        .action-item-new {
            animation: fadeIn 0.3s ease-out;
        }
        
        .recording-pulse {
            animation: pulse 2s ease-in-out infinite;
        }
    `;
    document.head.appendChild(style);
}

// ============== PHASE 4: REPLAY & TEMPLATE FUNCTIONS ==============

/**
 * Replay a recorded session
 */
async function replaySession(sessionId = null) {
    if (!window.recorderState.player) {
        alert('RecorderPlayer not initialized. Please ensure recorder-player.js is loaded.');
        return;
    }

    // Use last recorded session if no sessionId provided
    if (!sessionId) {
        sessionId = window.lastRecorderSessionId || window.recorderState.currentSessionId;
    }

    if (!sessionId || window.recorderState.recordedActions.length === 0) {
        alert('No recorded session available to replay');
        return;
    }

    console.log('[Replay] Starting replay for session:', sessionId);

    try {
        // Create RecorderSession from recorded actions
        const session = new RecorderSession({
            id: sessionId,
            name: document.getElementById('recordingName')?.value || 'Replay Session',
            url: document.getElementById('recordingUrl')?.value,
            actions: window.recorderState.recordedActions
        });

        // Load session into player
        window.recorderState.player.loadSession(session);

        // Show replay UI
        showReplayControls();

        // Start playback
        await window.recorderState.player.play();

    } catch (error) {
        console.error('[Replay] Error:', error);
        alert(`Replay failed: ${error.message}`);
    }
}

/**
 * Show replay controls UI
 */
function showReplayControls() {
    const existingControls = document.getElementById('replayControls');
    if (existingControls) {
        existingControls.style.display = 'flex';
        return;
    }

    const controls = document.createElement('div');
    controls.id = 'replayControls';
    controls.style.cssText = `
        position: fixed; bottom: 20px; right: 20px; z-index: 999999;
        background: linear-gradient(135deg, #667eea, #764ba2);
        padding: 15px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
        display: flex; gap: 10px; align-items: center;
    `;

    controls.innerHTML = `
        <div style="color: white; font-weight: 600; margin-right: 10px;">
            <div style="font-size: 0.9em; opacity: 0.8;">Replay</div>
            <div id="replayProgress" style="font-size: 1.1em;">0 / 0</div>
        </div>
        <button onclick="pauseReplay()" style="padding: 8px 12px; border: none; border-radius: 6px; background: rgba(255,255,255,0.2); color: white; cursor: pointer;">⏸️</button>
        <button onclick="resumeReplay()" style="padding: 8px 12px; border: none; border-radius: 6px; background: rgba(255,255,255,0.2); color: white; cursor: pointer;">▶️</button>
        <button onclick="stopReplay()" style="padding: 8px 12px; border: none; border-radius: 6px; background: rgba(255,255,255,0.2); color: white; cursor: pointer;">⏹️</button>
        <select id="replaySpeed" onchange="changeReplaySpeed()" style="padding: 6px; border: none; border-radius: 6px; background: rgba(255,255,255,0.9);">
            <option value="0.5">0.5x</option>
            <option value="1" selected>1x</option>
            <option value="1.5">1.5x</option>
            <option value="2">2x</option>
        </select>
    `;

    document.body.appendChild(controls);
}

/**
 * Update replay progress
 */
function updateReplayProgress(current, total) {
    const progressElement = document.getElementById('replayProgress');
    if (progressElement) {
        progressElement.textContent = `${current} / ${total}`;
    }
}

/**
 * Show replay complete message
 */
function showReplayComplete(session) {
    const controls = document.getElementById('replayControls');
    if (controls) {
        controls.style.background = 'linear-gradient(135deg, #10b981, #059669)';
        setTimeout(() => {
            controls.style.display = 'none';
        }, 3000);
    }
    
    alert(`✅ Replay complete: ${session.name}\n${session.actions.length} actions executed successfully`);
}

/**
 * Show breakpoint dialog
 */
function showBreakpointDialog(action) {
    const message = `Breakpoint reached at step ${action.step}\nAction: ${action.type}\n\nContinue replay?`;
    if (confirm(message)) {
        window.recorderState.player.resume();
    }
}

/**
 * Pause replay
 */
function pauseReplay() {
    if (window.recorderState.player) {
        window.recorderState.player.pause();
        console.log('[Replay] Paused');
    }
}

/**
 * Resume replay
 */
function resumeReplay() {
    if (window.recorderState.player) {
        window.recorderState.player.resume();
        console.log('[Replay] Resumed');
    }
}

/**
 * Stop replay
 */
function stopReplay() {
    if (window.recorderState.player) {
        window.recorderState.player.stop();
        const controls = document.getElementById('replayControls');
        if (controls) {
            controls.style.display = 'none';
        }
        console.log('[Replay] Stopped');
    }
}

/**
 * Change replay speed
 */
function changeReplaySpeed() {
    const speedSelect = document.getElementById('replaySpeed');
    if (speedSelect && window.recorderState.player) {
        const speed = parseFloat(speedSelect.value);
        window.recorderState.player.setSpeed(speed);
        console.log(`[Replay] Speed changed to ${speed}x`);
    }
}

/**
 * Show available templates
 */
function showTemplates() {
    if (!window.recorderState.templates) {
        alert('RecorderTemplate not initialized. Please ensure recorder-template.js is loaded.');
        return;
    }

    const templates = window.recorderState.templates.getAllTemplates();
    const categories = window.recorderState.templates.getCategories();

    console.log(`[Templates] ${templates.length} templates in ${categories.length} categories`);

    // Create template selector modal
    const modal = document.createElement('div');
    modal.id = 'templateModal';
    modal.style.cssText = `
        position: fixed; top: 0; left: 0; right: 0; bottom: 0; z-index: 999999;
        background: rgba(0,0,0,0.7); display: flex; align-items: center; justify-content: center;
    `;

    const content = document.createElement('div');
    content.style.cssText = `
        background: white; border-radius: 12px; padding: 30px; max-width: 800px;
        max-height: 80vh; overflow-y: auto; box-shadow: 0 20px 60px rgba(0,0,0,0.3);
    `;

    let html = `
        <h2 style="margin: 0 0 20px 0; color: #1f2937;">📋 Recording Templates</h2>
        <p style="color: #6b7280; margin-bottom: 20px;">Choose a template to guide your recording</p>
    `;

    // Group by category
    categories.forEach(category => {
        const categoryTemplates = window.recorderState.templates.getTemplatesByCategory(category);
        html += `<h3 style="color: #667eea; margin: 20px 0 10px 0; text-transform: capitalize;">${category}</h3>`;
        html += `<div style="display: grid; grid-template-columns: repeat(auto-fill, minmax(250px, 1fr)); gap: 15px;">`;

        categoryTemplates.forEach(template => {
            html += `
                <div onclick="applyTemplate('${template.id}')" style="
                    padding: 15px; border: 2px solid #e5e7eb; border-radius: 8px; cursor: pointer;
                    transition: all 0.2s; background: white;
                " onmouseover="this.style.borderColor='#667eea'; this.style.background='#f9fafb';" 
                   onmouseout="this.style.borderColor='#e5e7eb'; this.style.background='white';">
                    <div style="font-size: 2em; margin-bottom: 8px;">${template.icon}</div>
                    <div style="font-weight: 600; color: #1f2937; margin-bottom: 5px;">${template.name}</div>
                    <div style="font-size: 0.85em; color: #6b7280; margin-bottom: 8px;">${template.description}</div>
                    <div style="font-size: 0.75em; color: #9ca3af;">${template.steps.length} steps • ${template.estimatedTime}</div>
                </div>
            `;
        });

        html += `</div>`;
    });

    html += `
        <div style="margin-top: 20px; display: flex; justify-content: space-between;">
            <button onclick="closeTemplateModal()" style="padding: 10px 20px; border: 1px solid #d1d5db; border-radius: 6px; background: white; cursor: pointer;">Cancel</button>
            <button onclick="closeTemplateModal(); startRecording();" style="padding: 10px 20px; border: none; border-radius: 6px; background: #667eea; color: white; cursor: pointer;">Start Without Template</button>
        </div>
    `;

    content.innerHTML = html;
    modal.appendChild(content);
    document.body.appendChild(modal);
}

/**
 * Apply template
 */
function applyTemplate(templateId) {
    if (!window.recorderState.templates) return;

    const result = window.recorderState.templates.applyTemplate(templateId);
    console.log('[Templates] Applied template:', result.template.name);

    closeTemplateModal();

    // Show template guidance
    showTemplateGuidance(result);

    // Start recording with template
    startRecording();
}

/**
 * Show template guidance
 */
function showTemplateGuidance(result) {
    const guidance = document.createElement('div');
    guidance.id = 'templateGuidance';
    guidance.style.cssText = `
        position: fixed; top: 80px; right: 20px; z-index: 999998;
        background: white; border-radius: 12px; padding: 20px; width: 300px;
        box-shadow: 0 8px 24px rgba(0,0,0,0.2);
    `;

    let html = `
        <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 15px;">
            <h3 style="margin: 0; color: #1f2937;">${result.template.icon} ${result.template.name}</h3>
            <button onclick="closeTemplateGuidance()" style="border: none; background: none; font-size: 1.5em; cursor: pointer;">×</button>
        </div>
        <div style="font-size: 0.9em; color: #6b7280; margin-bottom: 15px;">${result.template.description}</div>
        <div style="max-height: 400px; overflow-y: auto;">
    `;

    result.guidance.forEach((step, index) => {
        const icon = step.required ? '🔴' : '⚪';
        html += `
            <div id="templateStep${index}" style="padding: 10px; margin-bottom: 8px; background: #f3f4f6; border-radius: 6px; border-left: 3px solid #d1d5db;">
                <div style="font-weight: 600; color: #374151; margin-bottom: 3px;">${icon} Step ${step.stepNumber}</div>
                <div style="font-size: 0.85em; color: #6b7280;">${step.description}</div>
            </div>
        `;
    });

    html += `</div>`;
    guidance.innerHTML = html;
    document.body.appendChild(guidance);
}

/**
 * Close template modal
 */
function closeTemplateModal() {
    const modal = document.getElementById('templateModal');
    if (modal) {
        modal.remove();
    }
}

/**
 * Close template guidance
 */
function closeTemplateGuidance() {
    const guidance = document.getElementById('templateGuidance');
    if (guidance) {
        guidance.remove();
    }
}

/**
 * Detect and suggest template
 */
function detectTemplate() {
    if (!window.recorderState.templates || window.recorderState.recordedActions.length === 0) {
        return;
    }

    const detection = window.recorderState.templates.detectTemplate(window.recorderState.recordedActions);
    
    if (detection) {
        console.log(`[Templates] Detected pattern: ${detection.template.name} (${(detection.confidence * 100).toFixed(0)}% confidence)`);
        
        // Show suggestion to user
        const suggestion = document.createElement('div');
        suggestion.style.cssText = `
            position: fixed; bottom: 80px; right: 20px; z-index: 999998;
            background: linear-gradient(135deg, #667eea, #764ba2); color: white;
            padding: 15px 20px; border-radius: 12px; box-shadow: 0 8px 24px rgba(0,0,0,0.3);
            animation: fadeIn 0.3s ease-out;
        `;

        suggestion.innerHTML = `
            <div style="font-weight: 600; margin-bottom: 5px;">📋 Pattern Detected!</div>
            <div style="font-size: 0.9em; opacity: 0.9;">Your actions match: ${detection.template.name}</div>
            <div style="font-size: 0.85em; opacity: 0.8; margin-top: 5px;">${(detection.confidence * 100).toFixed(0)}% confidence</div>
        `;

        document.body.appendChild(suggestion);

        setTimeout(() => {
            suggestion.style.opacity = '0';
            suggestion.style.transition = 'opacity 0.3s';
            setTimeout(() => suggestion.remove(), 300);
        }, 5000);
    }
}

// Auto-detect template after recording stops
const originalStopRecording = stopRecording;
if (typeof originalStopRecording === 'function') {
    stopRecording = async function() {
        await originalStopRecording();
        setTimeout(detectTemplate, 1000);
    };
}

console.log('[Recorder] ✅ Phase 4 functions loaded (Replay & Templates)');

// ============== END PHASE 4 ==============

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