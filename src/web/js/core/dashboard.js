// Dashboard Statistics and UI

// Load stats from localStorage or initialize with defaults
function loadStats() {
    const savedStats = localStorage.getItem('dashboardStats');
    if (savedStats) {
        try {
            const parsed = JSON.parse(savedStats);
            return {
                totalRequests: parsed.totalRequests || 0,
                totalTime: parsed.totalTime || 0,
                totalTokens: parsed.totalTokens || 0,
                testsGenerated: parsed.testsGenerated || 0,  // New: only recorder/builder tests
                testResults: parsed.testResults || []
            };
        } catch (e) {
            console.error('[Dashboard] Error loading stats:', e);
            return {
                totalRequests: 0,
                totalTime: 0,
                totalTokens: 0,
                testResults: []
            };
        }
    }
    return {
        totalRequests: 0,
        totalTime: 0,
        totalTokens: 0,
        testsGenerated: 0,  // New: only recorder/builder tests
        testResults: []
    };
}

// Save stats to localStorage
function saveStats() {
    try {
        // Always save window.stats (the global reference) not the module-scoped one
        const statsToSave = window.stats || stats;
        localStorage.setItem('dashboardStats', JSON.stringify(statsToSave));
        console.log('[Dashboard] 💾 Saved to localStorage:', statsToSave);
    } catch (e) {
        console.error('[Dashboard] Error saving stats:', e);
    }
}

// Initialize stats from localStorage
let stats = loadStats();
// Expose as window.stats immediately so all modules use the same reference
window.stats = stats;

function updateDashboardStats() {
    console.log('[Dashboard] 🔄 updateDashboardStats called');
    
    // Reload stats from localStorage every time to ensure we have latest data
    const freshStats = loadStats();
    console.log('[Dashboard] Fresh stats from localStorage:', freshStats);
    
    const totalRequestsEl = document.getElementById('dashboardTotalRequests');
    const avgTimeEl = document.getElementById('dashboardAvgTime');
    const passedEl = document.getElementById('testsPassedCount');
    const failedEl = document.getElementById('testsFailedCount');
    
    // Check if we're on the dashboard page
    if (!totalRequestsEl && !passedEl && !failedEl) {
        console.log('[Dashboard] Dashboard page not loaded yet, skipping update');
        return;
    }
    
    if (totalRequestsEl) {
        // Show testsGenerated (recorder/builder only), not raw code generation requests
        totalRequestsEl.textContent = freshStats.testsGenerated || 0;
        console.log('[Dashboard] Updated dashboardTotalRequests to:', freshStats.testsGenerated);
    }
    
    // Calculate average time from test results
    const testsExecuted = freshStats.testResults.length;
    if (avgTimeEl) {
        if (testsExecuted > 0 && freshStats.totalTime > 0) {
            const avgMs = Math.round(freshStats.totalTime / testsExecuted);
            avgTimeEl.textContent = avgMs + 'ms';
            console.log('[Dashboard] Updated avgTime to:', avgMs, 'ms (from', testsExecuted, 'tests)');
        } else {
            avgTimeEl.textContent = '0ms';
        }
    }
    
    const passed = freshStats.testResults.filter(r => r.status === 'passed').length;
    const failed = freshStats.testResults.filter(r => r.status === 'failed').length;
    
    console.log('[Dashboard] Calculated - Passed:', passed, 'Failed:', failed);
    
    if (passedEl) {
        passedEl.textContent = passed;
        console.log('[Dashboard] Updated testsPassedCount to:', passed);
    }
    
    if (failedEl) {
        failedEl.textContent = failed;
        console.log('[Dashboard] Updated testsFailedCount to:', failed);
    }
}

function addTestResult(name, status, duration, details = '') {
    console.log('[Dashboard] ➕ addTestResult CALLED:', {
        name: name,
        status: status,
        duration: duration,
        details: details,
        timestamp: new Date().toISOString()
    });
    
    // Parse duration to number (handle both "1500ms" and 1500)
    let durationMs = 0;
    if (typeof duration === 'string') {
        durationMs = parseInt(duration.replace('ms', '').replace('s', '000').trim()) || 0;
    } else {
        durationMs = duration || 0;
    }
    
    const result = {
        name: name,
        status: status,
        duration: durationMs,
        details: details,
        timestamp: new Date().toLocaleString()
    };
    
    // Use window.stats to ensure we're updating the global reference
    window.stats.testResults.unshift(result);
    if (window.stats.testResults.length > 10) {
        window.stats.testResults = window.stats.testResults.slice(0, 10);
    }
    
    // Update totalTime for average calculation
    window.stats.totalTime = (window.stats.totalTime || 0) + durationMs;
    
    console.log('[Dashboard] 📊 Current test results count:', window.stats.testResults.length);
    console.log('[Dashboard] ⏱️ Total time accumulated:', window.stats.totalTime, 'ms');
    console.log('[Dashboard] 📋 Full test results:', JSON.stringify(window.stats.testResults, null, 2));
    
    // Save to localStorage immediately
    saveStats();
    
    // Verify save worked
    const savedData = localStorage.getItem('dashboardStats');
    const parsed = savedData ? JSON.parse(savedData) : null;
    console.log('[Dashboard] ✅ VERIFIED localStorage save:', {
        hasData: !!savedData,
        resultCount: parsed?.testResults?.length || 0,
        latestTest: parsed?.testResults?.[0]?.name,
        totalTime: parsed?.totalTime
    });
    console.log('[Dashboard] Verified localStorage has data:', !!savedData);
    
    // Update UI immediately if on dashboard page
    updateDashboardStats();
}

function updateRecentTestResults() {
    console.log('[Dashboard] 📝 updateRecentTestResults called');
    
    // Reload stats from localStorage to get latest data
    const freshStats = loadStats();
    
    const container = document.getElementById('recentTestResults');
    
    if (!container) {
        console.log('[Dashboard] recentTestResults element not found - page may not be loaded');
        return;
    }
    
    console.log('[Dashboard] Test results count:', freshStats.testResults.length);
    
    if (freshStats.testResults.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">📊</div>
                <div class="empty-state-title">No test results yet</div>
                <div class="empty-state-description">
                    Start generating and running tests to see results here
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="result-list">
            ${freshStats.testResults.map(result => `
                <div class="result-card">
                    <div class="result-card-header">
                        <div class="result-card-title">${result.name}</div>
                        <span class="result-card-badge ${result.status}">
                            ${result.status === 'passed' ? '✅ Passed' : 
                              result.status === 'failed' ? '❌ Failed' : 
                              result.status === 'info' ? 'ℹ️ Info' : '⏸️ Pending'}
                        </span>
                    </div>
                    ${result.details ? `
                        <div class="result-card-body">${result.details}</div>
                    ` : ''}
                    <div class="result-card-footer">
                        <div class="result-card-meta">
                            <span class="result-card-meta-item">
                                ⏱️ ${result.duration}ms
                            </span>
                            <span class="result-card-meta-item">
                                📅 ${result.timestamp}
                            </span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

function updateActivityTimeline() {
    const container = document.getElementById('activityTimeline');
    if (!container) return;
    
    // Reload stats from localStorage
    const freshStats = loadStats();
    
    if (freshStats.testResults.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <div class="empty-state-icon">⏱️</div>
                <div class="empty-state-title">No activity yet</div>
                <div class="empty-state-description">
                    Your activity will appear here as you work
                </div>
            </div>
        `;
        return;
    }
    
    container.innerHTML = `
        <div class="timeline">
            ${freshStats.testResults.slice(0, 5).map((result, index) => `
                <div class="timeline-item">
                    <div class="timeline-icon ${result.status}">
                        ${result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : result.status === 'info' ? 'ℹ️' : '⏸️'}
                    </div>
                    <div class="timeline-content">
                        <div class="timeline-title">${result.name}</div>
                        ${result.details ? `<div class="timeline-description">${result.details}</div>` : ''}
                        <div class="timeline-meta">
                            <span>⏱️ ${result.duration}ms</span>
                            <span>📅 ${result.timestamp}</span>
                        </div>
                    </div>
                </div>
            `).join('')}
        </div>
    `;
}

// Add activity log entry (for all activity including raw code generation)
function addActivityLog(name, type, duration, details = '') {
    console.log('[Dashboard] 📝 addActivityLog CALLED:', {
        name: name,
        type: type,  // 'test', 'code_generated', 'execution', etc.
        duration: duration,
        details: details
    });
    
    // Map type to status for display
    const statusMap = {
        'test': 'passed',           // Test created successfully
        'code_generated': 'info',   // Code generated (just an activity, not a test result)
        'action_suggestion': 'info', // Action suggestion generated
        'execution': 'pending',      // Test execution in progress
        'passed': 'passed',
        'failed': 'failed'
    };
    
    const status = statusMap[type] || 'pending';
    
    // Use addTestResult to add to timeline (it handles the UI updates)
    addTestResult(name, status, duration, details);
}

// Increment tests generated counter (only for saved recorder/builder tests)
function incrementTestsGenerated() {
    console.log('[Dashboard] ✅ incrementTestsGenerated CALLED');
    window.stats.testsGenerated = (window.stats.testsGenerated || 0) + 1;
    saveStats();
    updateDashboardStats();
    console.log('[Dashboard] Total tests generated:', window.stats.testsGenerated);
}

// Expose functions to window object (stats already exposed above)
window.loadStats = loadStats;
window.saveStats = saveStats;
window.updateDashboardStats = updateDashboardStats;
window.addTestResult = addTestResult;
window.addActivityLog = addActivityLog;
window.incrementTestsGenerated = incrementTestsGenerated;
window.updateRecentTestResults = updateRecentTestResults;
window.updateActivityTimeline = updateActivityTimeline;

// Initialize dashboard on load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', function() {
        console.log('[Dashboard] DOM loaded via event, initializing...');
        setTimeout(() => {
            console.log('[Dashboard] Running initial dashboard update');
            updateDashboardStats();
            updateRecentTestResults();
            updateActivityTimeline();
        }, 100);
    });
} else {
    // DOM already loaded
    console.log('[Dashboard] DOM already loaded, initializing...');
    setTimeout(() => {
        console.log('[Dashboard] Running initial dashboard update');
        updateDashboardStats();
        updateRecentTestResults();
        updateActivityTimeline();
    }, 100);
}
