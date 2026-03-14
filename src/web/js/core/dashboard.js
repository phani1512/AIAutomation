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
        totalRequestsEl.textContent = freshStats.totalRequests;
        console.log('[Dashboard] Updated dashboardTotalRequests to:', freshStats.totalRequests);
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
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">No test results yet. Start generating and running tests!</div>';
        return;
    }
    
    container.innerHTML = freshStats.testResults.map(result => `
        <div class="test-result-item ${result.status}">
            <div style="display: flex; justify-content: space-between; align-items: start;">
                <div style="flex: 1;">
                    <div style="display: flex; align-items: center; gap: 10px; margin-bottom: 8px;">
                        <span style="font-size: 1.2em;">${result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⏸️'}</span>
                        <strong style="color: var(--text-primary);">${result.name}</strong>
                    </div>
                    ${result.details ? `<p style="color: var(--text-secondary); font-size: 0.9em; margin: 0 0 8px 0;">${result.details}</p>` : ''}
                    <div style="display: flex; gap: 15px; font-size: 0.85em; color: var(--text-tertiary);">
                        <span>⏱️ ${result.duration}ms</span>
                        <span>📅 ${result.timestamp}</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function updateActivityTimeline() {
    const container = document.getElementById('activityTimeline');
    if (!container) return;
    
    // Reload stats from localStorage
    const freshStats = loadStats();
    
    if (freshStats.testResults.length === 0) {
        container.innerHTML = '<div style="padding: 40px; text-align: center; color: var(--text-secondary);">Your activity will appear here</div>';
        return;
    }
    
    container.innerHTML = freshStats.testResults.slice(0, 5).map((result, index) => `
        <div style="display: flex; gap: 15px; margin-bottom: 20px; ${index < freshStats.testResults.length - 1 ? 'padding-bottom: 20px; border-bottom: 1px solid var(--border-color);' : ''}">
            <div style="font-size: 2em; opacity: 0.5;">${result.status === 'passed' ? '✅' : result.status === 'failed' ? '❌' : '⏸️'}</div>
            <div style="flex: 1;">
                <strong style="color: var(--text-primary);">${result.name}</strong>
                <div style="color: var(--text-secondary); font-size: 0.9em; margin-top: 4px;">${result.timestamp}</div>
            </div>
            <div style="color: var(--text-tertiary); font-size: 0.9em;">${result.duration}ms</div>
        </div>
    `).join('');
}

// Expose functions to window object (stats already exposed above)
window.loadStats = loadStats;
window.saveStats = saveStats;
window.updateDashboardStats = updateDashboardStats;
window.addTestResult = addTestResult;
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
